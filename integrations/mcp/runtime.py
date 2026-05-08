# -*- coding: utf-8 -*-
"""High-level MCP runtime: discovery, configuration, and active tool state."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from integrations.mcp.discovery import (
    default_client_configs,
    delete_client_config,
    discover_local_servers,
    ensure_default_client_configs,
    load_client_configs,
    save_client_config,
)
from integrations.mcp.local_stdio_templates import local_stdio_template
from integrations.mcp.manager import MCPClientManager
from integrations.mcp.model_runtime_resolver import build_model_runtime_resolver
from integrations.mcp.schema import MCPClientConfig, MCPRuntimeSnapshot
from integrations.mcp.secrets import load_mcp_secrets, mask_secret, resolve_secret_value, save_mcp_secrets, stable_secret_ref


class MCPRuntime:
    """Own discovery/configuration state for MCP-backed tools."""

    def __init__(
        self,
        project_root: str,
        client_dir: Optional[str] = None,
        secrets_path: Optional[str] = None,
    ):
        self.project_root = str(Path(project_root).resolve())
        self.client_dir = str(Path(client_dir or (Path(self.project_root) / "mcp" / "mcp_client")).resolve())
        self.secrets_path = str(Path(secrets_path or (Path(self.project_root) / "local_mcp_secrets.yaml")).resolve())
        self.manager = MCPClientManager()
        self._snapshot = MCPRuntimeSnapshot()
        self._bootstrap_workspace_storage()
        ensure_default_client_configs(self.client_dir, project_root=self.project_root)

    def sync(self, target=None) -> MCPRuntimeSnapshot:
        discovered = discover_local_servers()
        availability_by_server = self._server_availability_map(discovered)
        configured = self._materialize_builtin_local_stdio(self._load_configs())
        secrets = load_mcp_secrets(self.secrets_path)
        active = [config for config in configured if config.enabled and self._client_server_available(config, availability_by_server)]
        active_tools, bindings, available_by_client, errors = self.manager.sync_active(active, secrets, target)
        self._cache_client_tool_catalog(configured, available_by_client)
        configured_rows = self._build_configured_rows(
            configured=configured,
            discovered=discovered,
            availability_by_server=availability_by_server,
            secrets=secrets,
            available_by_client=available_by_client,
            bindings=bindings,
            errors=errors,
        )
        self._snapshot = MCPRuntimeSnapshot(
            discovered=list(self._decorate_discovered_rows(discovered, availability_by_server)),
            configured=list(configured_rows),
            active_clients=list(active),
            active_tools=list(active_tools),
            tool_bindings=list(bindings),
        )
        return self._snapshot

    def snapshot(self) -> MCPRuntimeSnapshot:
        return self._snapshot

    def discover_rows(self) -> List[Dict[str, object]]:
        if self._snapshot.discovered:
            return self._snapshot.discovered_rows()
        discovered = discover_local_servers()
        availability_by_server = self._server_availability_map(discovered)
        return self._decorate_discovered_rows(discovered, availability_by_server)

    def configured_rows(self) -> List[Dict[str, object]]:
        if self._snapshot.configured:
            return self._snapshot.configured_rows()
        rows: List[Dict[str, object]] = []
        secrets = load_mcp_secrets(self.secrets_path)
        discovered = discover_local_servers()
        discovered_by_id = {item.server_id: item for item in discovered}
        availability_by_server = self._server_availability_map(discovered)
        for config in self._materialize_builtin_local_stdio(self._load_configs()):
            rows.append(
                self._build_client_row(
                    config=config,
                    discovered_by_id=discovered_by_id,
                    availability_by_server=availability_by_server,
                    secrets=secrets,
                    available_tools=None,
                    active_tool_names=[],
                    runtime_error="",
                )
            )
        return rows

    def upsert_client(
        self,
        config: MCPClientConfig,
        target=None,
        *,
        original_client_id: str = "",
        secret_values: Optional[Mapping[str, object]] = None,
    ) -> MCPRuntimeSnapshot:
        normalized = config.normalized()
        current_configs = {item.client_id: item for item in self._load_configs()}
        existing = current_configs.get(str(original_client_id or normalized.client_id).strip())
        if original_client_id and existing is None:
            raise ValueError(f"MCP client not found: {original_client_id}")
        if original_client_id and normalized.client_id != str(original_client_id).strip():
            raise ValueError("client_id cannot be changed after creation.")
        if existing is not None:
            normalized = self._merge_client(existing, normalized)
        normalized = self._apply_builtin_local_stdio_template(normalized)
        normalized = self._finalize_metadata(normalized, existing)
        self._apply_secret_updates(normalized, existing, secret_values)
        save_client_config(self.client_dir, normalized.normalized())
        if target is None:
            return self.sync()
        from integrations.mcp.sync import sync_mcp_runtime

        return sync_mcp_runtime(target, runtime=self)

    def toggle_client(self, client_id: str, enabled: bool, target=None) -> MCPRuntimeSnapshot:
        configs = {config.client_id: config for config in self._load_configs()}
        current = configs.get(client_id)
        if current is None:
            raise ValueError(f"MCP client not found: {client_id}")
        current.enabled = bool(enabled)
        save_client_config(self.client_dir, current.normalized())
        if target is None:
            return self.sync()
        from integrations.mcp.sync import sync_mcp_runtime

        return sync_mcp_runtime(target, runtime=self)

    def delete_client(self, client_id: str, target=None) -> MCPRuntimeSnapshot:
        configs = {config.client_id: config for config in self._load_configs()}
        current = configs.get(client_id)
        if current is None:
            raise ValueError(f"MCP client not found: {client_id}")
        metadata = dict(current.metadata or {})
        if str(metadata.get("source") or "").strip() == "builtin":
            raise ValueError(f"builtin MCP client cannot be deleted: {client_id}")
        delete_client_config(self.client_dir, client_id)
        if target is None:
            return self.sync()
        from integrations.mcp.sync import sync_mcp_runtime

        return sync_mcp_runtime(target, runtime=self)

    def default_rows(self) -> List[Dict[str, object]]:
        return [config.to_dict() for config in default_client_configs(project_root=self.project_root)]

    def close(self) -> None:
        self.manager.close()

    def _bootstrap_workspace_storage(self) -> None:
        client_root = Path(self.client_dir)
        client_root.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_project_clients(client_root)
        self._migrate_legacy_project_secrets(Path(self.secrets_path))

    def _migrate_legacy_project_clients(self, target_root: Path) -> None:
        if any(target_root.glob("*.yaml")):
            return
        legacy_root = Path(self.project_root) / "mcp" / "mcp_client"
        if legacy_root.resolve() == target_root.resolve() or not legacy_root.is_dir():
            return
        for path in sorted(legacy_root.glob("*.yaml")):
            shutil.copy2(path, target_root / path.name)

    def _migrate_legacy_project_secrets(self, target_path: Path) -> None:
        legacy_path = Path(self.project_root) / "local_mcp_secrets.yaml"
        if legacy_path.resolve() == target_path.resolve() or not legacy_path.is_file():
            return
        current = load_mcp_secrets(str(target_path))
        if current:
            return
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_path, target_path)

    def _materialize_builtin_local_stdio(self, configured: List[MCPClientConfig]) -> List[MCPClientConfig]:
        rows: List[MCPClientConfig] = []
        for config in configured:
            rows.append(self._apply_builtin_local_stdio_template(config))
        return rows

    def _load_configs(self) -> List[MCPClientConfig]:
        rows = load_client_configs(self.client_dir)
        builtin_by_id = {item.client_id: item for item in default_client_configs(project_root=self.project_root)}
        restored: List[MCPClientConfig] = []
        for config in rows:
            restored.append(self._restore_builtin_metadata(config, builtin_by_id.get(config.client_id)))
        return restored

    def _restore_builtin_metadata(
        self,
        config: MCPClientConfig,
        builtin_template: Optional[MCPClientConfig],
    ) -> MCPClientConfig:
        if builtin_template is None:
            return config.normalized()
        metadata = dict(config.metadata or {})
        if str(metadata.get("source") or "").strip():
            return config.normalized()
        restored = dict(builtin_template.metadata or {})
        restored.update(metadata)
        config.metadata = restored
        if not config.server_id and builtin_template.server_id:
            config.server_id = builtin_template.server_id
        if not config.command and builtin_template.command:
            config.command = builtin_template.command
        if not config.args and builtin_template.args:
            config.args = list(builtin_template.args)
        if not config.cwd and builtin_template.cwd:
            config.cwd = builtin_template.cwd
        return config.normalized()

    def _apply_builtin_local_stdio_template(self, config: MCPClientConfig) -> MCPClientConfig:
        normalized = config.normalized()
        if normalized.mode != "local":
            return normalized
        if not normalized.server_id:
            inferred = self._infer_server_id_from_client(normalized.client_id)
            if inferred:
                normalized.server_id = inferred
        if normalized.command or not normalized.server_id:
            return normalized
        template = local_stdio_template(self.project_root, normalized.server_id)
        if not isinstance(template, dict):
            return normalized
        normalized.command = str(template.get("command") or "").strip()
        normalized.args = [str(item) for item in (template.get("args") or []) if str(item).strip()]
        normalized.cwd = str(template.get("cwd") or "").strip()
        return normalized.normalized()

    def _infer_server_id_from_client(self, client_id: str) -> str:
        candidate = str(client_id or "").strip()
        if not candidate:
            return ""
        discovered = {str(item.server_id).strip() for item in discover_local_servers()}
        return candidate if candidate in discovered else ""

    def _merge_client(self, existing: MCPClientConfig, incoming: MCPClientConfig) -> MCPClientConfig:
        incoming.secret_refs = dict(existing.secret_refs)
        if not incoming.server_id and existing.server_id:
            incoming.server_id = existing.server_id
        if not incoming.endpoint and existing.endpoint:
            incoming.endpoint = existing.endpoint
        if not incoming.command and existing.command:
            incoming.command = existing.command
        if not incoming.args and existing.args:
            incoming.args = list(existing.args)
        if not incoming.cwd and existing.cwd:
            incoming.cwd = existing.cwd
        if not incoming.headers and existing.headers:
            incoming.headers = dict(existing.headers)
        if not incoming.env and existing.env:
            incoming.env = dict(existing.env)
        metadata = dict(existing.metadata or {})
        metadata.update(dict(incoming.metadata or {}))
        incoming.metadata = metadata
        return incoming

    def _finalize_metadata(
        self,
        config: MCPClientConfig,
        existing: Optional[MCPClientConfig],
    ) -> MCPClientConfig:
        metadata = dict(config.metadata or {})
        if existing is not None:
            return config.normalized()
        if not str(metadata.get("source") or "").strip():
            metadata["source"] = "user"
        if not str(metadata.get("managed_by") or "").strip():
            metadata["managed_by"] = "user"
        if not str(metadata.get("install_kind") or "").strip():
            metadata["install_kind"] = "user_created"
        config.metadata = metadata
        return config.normalized()

    def _apply_secret_updates(
        self,
        config: MCPClientConfig,
        existing: Optional[MCPClientConfig],
        secret_values: Optional[Mapping[str, object]],
    ) -> None:
        refs = dict(config.secret_refs or {})
        if existing is not None:
            refs.update({str(k): str(v) for k, v in (existing.secret_refs or {}).items() if str(k).strip() and str(v).strip()})

        for slot_name in self._required_secret_slots(config):
            refs.setdefault(slot_name, stable_secret_ref(config.client_id, slot_name))

        updates: Dict[str, str] = {}
        for slot_name, raw_value in (secret_values or {}).items():
            slot = str(slot_name or "").strip()
            value = str(raw_value or "").strip()
            if not slot or not value:
                continue
            refs.setdefault(slot, stable_secret_ref(config.client_id, slot))
            secret_ref = str(refs.get(slot) or "").strip()
            if secret_ref:
                updates[secret_ref] = value

        if updates:
            save_mcp_secrets(self.secrets_path, updates)
        config.secret_refs = refs

    def _required_secret_slots(self, config: MCPClientConfig) -> List[str]:
        if config.mode == "local":
            discovered_by_id = {item.server_id: item for item in discover_local_servers()}
            server = discovered_by_id.get(config.server_id)
            if server and server.requires_secrets:
                return [str(item).strip() for item in (server.required_secrets or []) if str(item).strip()]
            return [str(key).strip() for key in (config.secret_refs or {}).keys() if str(key).strip()]
        slots = [str(key).strip() for key in (config.secret_refs or {}).keys() if str(key).strip()]
        if slots:
            return slots
        return ["api_key"]

    def _cache_client_tool_catalog(
        self,
        configured: List[MCPClientConfig],
        available_by_client: Mapping[str, List[Dict[str, Any]]],
    ) -> None:
        for config in configured:
            if config.mode == "remote":
                pass
            elif config.mode == "local" and config.command and not config.server_id:
                pass
            else:
                continue
            catalog = [dict(item) for item in (available_by_client.get(config.client_id) or []) if isinstance(item, dict)]
            if not catalog:
                continue
            cached = config.metadata.get("cached_tools")
            if cached == catalog:
                continue
            config.metadata["cached_tools"] = catalog
            save_client_config(self.client_dir, config.normalized())

    def _build_configured_rows(
        self,
        *,
        configured: List[MCPClientConfig],
        discovered: List[Any],
        availability_by_server: Mapping[str, Dict[str, Any]],
        secrets: Mapping[str, str],
        available_by_client: Mapping[str, List[Dict[str, Any]]],
        bindings,
        errors: Mapping[str, str],
    ) -> List[Dict[str, Any]]:
        discovered_by_id = {
            str(item.server_id): item
            for item in discovered
            if hasattr(item, "server_id") and str(getattr(item, "server_id", "")).strip()
        }
        active_by_client: Dict[str, List[str]] = {}
        for binding in bindings:
            active_by_client.setdefault(str(binding.client_id), []).append(str(binding.tool_name))

        rows: List[Dict[str, Any]] = []
        for config in configured:
            available_tools = available_by_client.get(config.client_id)
            rows.append(
                self._build_client_row(
                    config=config,
                    discovered_by_id=discovered_by_id,
                    availability_by_server=availability_by_server,
                    secrets=secrets,
                    available_tools=available_tools,
                    active_tool_names=active_by_client.get(config.client_id, []),
                    runtime_error=str(errors.get(config.client_id, "") or ""),
                )
            )
        return rows

    def _build_client_row(
        self,
        *,
        config: MCPClientConfig,
        discovered_by_id: Mapping[str, Any],
        availability_by_server: Mapping[str, Dict[str, Any]],
        secrets: Mapping[str, str],
        available_tools: Optional[List[Dict[str, Any]]],
        active_tool_names: List[str],
        runtime_error: str,
    ) -> Dict[str, Any]:
        tools = self._available_tools_for_client(config, discovered_by_id, available_tools)
        selected = {str(name).strip() for name in (config.enabled_tools or []) if str(name).strip()}
        tool_rows: List[Dict[str, Any]] = []
        for item in tools:
            tool_name = str(item.get("name") or "").strip()
            if not tool_name:
                continue
            tool_rows.append(
                {
                    "name": tool_name,
                    "description": str(item.get("description") or "").strip(),
                    "selected": (tool_name in selected) if selected else True,
                }
            )
        secret_slots = self._secret_slots_for_client(config, discovered_by_id, secrets)
        row = config.to_api_dict(
            available_tools=tool_rows,
            active_tool_names=active_tool_names,
            secret_slots=secret_slots,
            runtime_error=runtime_error,
        )
        readiness = self._build_readiness_state(
            config=config,
            discovered_by_id=discovered_by_id,
            availability_by_server=availability_by_server,
            available_tools=tool_rows,
            active_tool_names=active_tool_names,
            runtime_error=runtime_error,
        )
        row.update(readiness)
        return row

    def _build_readiness_state(
        self,
        *,
        config: MCPClientConfig,
        discovered_by_id: Mapping[str, Any],
        availability_by_server: Mapping[str, Dict[str, Any]],
        available_tools: List[Dict[str, Any]],
        active_tool_names: List[str],
        runtime_error: str,
    ) -> Dict[str, Any]:
        enabled = bool(config.enabled)
        mode = str(config.mode or "").strip().lower() or "local"
        server_known = bool(str(config.server_id or "").strip() and discovered_by_id.get(str(config.server_id or "").strip()))
        has_local_command = bool(str(config.command or "").strip())
        has_runtime_tools = bool(active_tool_names)
        has_catalog = bool(available_tools)
        runtime_error_text = str(runtime_error or "").strip()
        server_availability = dict(availability_by_server.get(str(config.server_id or "").strip(), {}))
        server_available = True if not config.server_id else bool(server_availability.get("available", True))
        server_availability_detail = str(server_availability.get("availability_detail") or "")

        readiness_status = "disabled"
        readiness_detail = ""
        if not enabled:
            readiness_status = "disabled"
            readiness_detail = "client_disabled"
        elif mode == "local" and config.server_id and not server_available:
            readiness_status = "blocked"
            readiness_detail = server_availability_detail or "server_unavailable"
        elif runtime_error_text:
            readiness_status = "error"
            readiness_detail = runtime_error_text
        elif mode == "remote":
            readiness_status = "ready"
            readiness_detail = "remote_client"
        elif has_runtime_tools or has_catalog:
            readiness_status = "ready"
            readiness_detail = "local_tools_ready"
        elif server_known or has_local_command:
            readiness_status = "starting"
            readiness_detail = "local_runtime_pending"
        else:
            readiness_status = "configured"
            readiness_detail = "local_server_unavailable"

        blocks_chat = mode == "local" and enabled and readiness_status in {"configured", "starting", "error", "blocked"}
        return {
            "readiness_status": readiness_status,
            "readiness_detail": readiness_detail,
            "blocks_chat": bool(blocks_chat),
            "server_available": bool(server_available),
            "server_availability_detail": server_availability_detail,
        }

    def _server_availability_map(self, discovered: List[Any]) -> Dict[str, Dict[str, Any]]:
        resolver = build_model_runtime_resolver(self.project_root)
        rows: Dict[str, Dict[str, Any]] = {}
        tool_model_types = {
            "speech_models": ["speech_to_text", "text_to_speech"],
            "embedding_models": ["text_embedding", "multimodal_embedding"],
        }
        for item in discovered:
            server_id = str(getattr(item, "server_id", "") or "").strip()
            required = [str(name).strip() for name in (getattr(item, "required_model_types", []) or []) if str(name).strip()]
            if not server_id:
                continue
            if not required:
                rows[server_id] = {"available": True, "availability_detail": "ok"}
                continue
            checks = []
            if server_id in tool_model_types:
                for name in tool_model_types[server_id]:
                    availability = resolver.availability(name)
                    if availability.get("available"):
                        checks.append(availability)
                        continue
                    fallback = resolver.free_fallback_available(name)
                    checks.append(fallback)
            else:
                checks = [resolver.availability(name) for name in required]
            use_any = server_id in {"generation_models", "speech_models", "embedding_models"}
            available = any(bool(check.get("available")) for check in checks) if use_any else all(bool(check.get("available")) for check in checks)
            if available:
                rows[server_id] = {"available": True, "availability_detail": "ok"}
                continue
            if server_id not in tool_model_types:
                rows[server_id] = {
                    "available": False,
                    "availability_detail": f"missing_model_type:{','.join(required)}",
                }
                continue
            detail = ",".join(str(check.get("detail") or "").strip() for check in checks if str(check.get("detail") or "").strip())
            if not detail:
                detail = f"missing_model_type:{','.join(required)}"
            rows[server_id] = {"available": False, "availability_detail": detail}
        return rows

    def _decorate_discovered_rows(
        self,
        discovered: List[Any],
        availability_by_server: Mapping[str, Dict[str, Any]],
    ) -> List[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        for item in discovered:
            base = item.to_dict() if hasattr(item, "to_dict") else dict(item)
            availability = dict(availability_by_server.get(str(base.get("server_id") or "").strip(), {}))
            base["available"] = bool(availability.get("available", True))
            base["availability_detail"] = str(availability.get("availability_detail") or "ok")
            rows.append(base)
        return rows

    def _client_server_available(
        self,
        config: MCPClientConfig,
        availability_by_server: Mapping[str, Dict[str, Any]],
    ) -> bool:
        if str(config.mode or "").strip().lower() != "local":
            return True
        server_id = str(config.server_id or "").strip()
        if not server_id:
            return True
        row = dict(availability_by_server.get(server_id, {}))
        return bool(row.get("available", True))

    def _available_tools_for_client(
        self,
        config: MCPClientConfig,
        discovered_by_id: Mapping[str, Any],
        available_tools: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        if available_tools:
            return [dict(item) for item in available_tools if isinstance(item, dict)]
        if config.mode == "local":
            if config.command:
                if config.server_id:
                    server = discovered_by_id.get(config.server_id)
                    if server is not None:
                        return [{"name": str(name), "description": ""} for name in (server.tools or []) if str(name).strip()]
                cached = config.metadata.get("cached_tools")
                if isinstance(cached, list):
                    return [dict(item) for item in cached if isinstance(item, dict)]
                return []
            server = discovered_by_id.get(config.server_id)
            if server is None:
                return []
            return [{"name": str(name), "description": ""} for name in (server.tools or []) if str(name).strip()]
        cached = config.metadata.get("cached_tools")
        if isinstance(cached, list):
            return [dict(item) for item in cached if isinstance(item, dict)]
        return []

    def _secret_slots_for_client(
        self,
        config: MCPClientConfig,
        discovered_by_id: Mapping[str, Any],
        secrets: Mapping[str, str],
    ) -> List[Dict[str, Any]]:
        slot_names = self._required_secret_slots(config)
        if not slot_names and config.secret_refs:
            slot_names = [str(key).strip() for key in config.secret_refs.keys() if str(key).strip()]
        rows: List[Dict[str, Any]] = []
        for slot_name in slot_names:
            secret_ref = str((config.secret_refs or {}).get(slot_name) or "").strip()
            value = resolve_secret_value(slot_name, secret_ref, secrets)
            rows.append(
                {
                    "slot_name": slot_name,
                    "secret_ref": secret_ref,
                    "has_value": bool(value),
                    "masked_value": mask_secret(value),
                }
            )
        if config.mode == "local":
            server = discovered_by_id.get(config.server_id)
            if server is not None and not server.requires_secrets:
                for row in rows:
                    row["note"] = ""
        return rows
