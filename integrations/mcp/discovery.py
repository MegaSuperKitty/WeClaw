# -*- coding: utf-8 -*-
"""Discovery and persistence helpers for MCP server manifests and client configs."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from integrations.mcp.local_stdio_templates import local_stdio_template
from integrations.mcp.mcp_server import list_server_manifests
from integrations.mcp.schema import MCPClientConfig
from integrations.mcp.secrets import stable_secret_ref


def discover_local_servers():
    return list_server_manifests()


def load_client_configs(client_dir: str) -> List[MCPClientConfig]:
    root = Path(client_dir)
    if not root.is_dir():
        return []
    rows: List[MCPClientConfig] = []
    try:
        import yaml
    except Exception:
        return rows
    for path in sorted(root.glob("*.yaml")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except Exception:
            continue
        config = _parse_client_config(data, fallback_client_id=path.stem)
        if config is not None:
            rows.append(config)
    return rows


def save_client_config(client_dir: str, config: MCPClientConfig) -> Path:
    root = Path(client_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{config.client_id}.yaml"
    import yaml

    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config.to_dict(), handle, allow_unicode=False, sort_keys=False)
    return path


def delete_client_config(client_dir: str, client_id: str) -> bool:
    path = Path(client_dir) / f"{client_id}.yaml"
    if not path.is_file():
        return False
    path.unlink()
    return True


def ensure_default_client_configs(client_dir: str, project_root: str = "") -> None:
    root = Path(client_dir)
    root.mkdir(parents=True, exist_ok=True)
    if any(root.glob("*.yaml")):
        return
    for config in default_client_configs(project_root=project_root):
        save_client_config(client_dir, config)


def default_client_configs(project_root: str = "") -> List[MCPClientConfig]:
    configs: List[MCPClientConfig] = []
    for manifest in discover_local_servers():
        config = MCPClientConfig(
            client_id=manifest.server_id,
            name=manifest.name,
            description=manifest.description,
            enabled=bool(manifest.default_enabled),
            mode="local",
            transport=manifest.transport,
            server_id=manifest.server_id,
            secret_refs={
                secret: stable_secret_ref(manifest.server_id, secret)
                for secret in manifest.required_secrets
                if str(secret or "").strip()
            },
            metadata={
                "source": "builtin",
                "managed_by": "system",
                "origin_server_id": manifest.server_id,
                "install_kind": "workspace_bootstrap",
            },
        )
        template = local_stdio_template(project_root, manifest.server_id)
        if isinstance(template, dict):
            config.command = str(template.get("command") or "").strip()
            config.args = [str(item) for item in (template.get("args") or []) if str(item).strip()]
            config.cwd = str(template.get("cwd") or "").strip()
        configs.append(config.normalized())
    configs.append(
        MCPClientConfig(
            client_id="zhipu_web_search",
            name="Zhipu Web Search",
            description="Remote Zhipu web search via streamable HTTP MCP.",
            enabled=True,
            mode="remote",
            transport="streamable_http",
            endpoint="https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp",
            secret_refs={"api_key": stable_secret_ref("zhipu_web_search", "api_key")},
            metadata={
                "source": "builtin",
                "managed_by": "system",
                "origin_server_id": "zhipu_web_search",
                "install_kind": "workspace_bootstrap",
            },
        ).normalized()
    )
    return configs


def _parse_client_config(data: object, fallback_client_id: str = "") -> Optional[MCPClientConfig]:
    if not isinstance(data, dict):
        return None
    text_map: Dict[str, object] = dict(data)
    client_id = str(text_map.get("client_id") or fallback_client_id or "").strip()
    if not client_id:
        return None
    config = MCPClientConfig(
        client_id=client_id,
        name=str(text_map.get("name") or client_id),
        description=str(text_map.get("description") or ""),
        enabled=bool(text_map.get("enabled", True)),
        mode=str(text_map.get("mode") or "local"),
        transport=str(text_map.get("transport") or ""),
        server_id=str(text_map.get("server_id") or ""),
        endpoint=str(text_map.get("endpoint") or ""),
        command=str(text_map.get("command") or ""),
        args=_to_str_list(text_map.get("args")),
        cwd=str(text_map.get("cwd") or ""),
        enabled_tools=_to_str_list(text_map.get("enabled_tools")),
        env=_to_str_dict(text_map.get("env")),
        headers=_to_str_dict(text_map.get("headers")),
        secret_refs=_to_str_dict(text_map.get("secret_refs")),
        metadata=dict(text_map.get("metadata") or {}),
    )
    return config.normalized()


def _to_str_dict(value: object) -> Dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): str(item)
        for key, item in value.items()
        if item is not None and str(item).strip()
    }


def _to_str_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    rows: List[str] = []
    for item in value:
        text = str(item or "").strip()
        if text:
            rows.append(text)
    return rows
