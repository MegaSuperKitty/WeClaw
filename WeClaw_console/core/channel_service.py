# -*- coding: utf-8 -*-
"""Channel config + runtime orchestration for the console."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Mapping

import yaml

from .channel_config_store import ChannelConfigStore
from .channel_runtime import ChannelRuntimeManager
from .channel_specs import ChannelFieldSpec, ChannelSpec, normalize_channel_name


class ChannelServiceError(RuntimeError):
    """Base error for channel service operations."""


class ChannelNotFoundError(ChannelServiceError):
    """Raised when a channel does not exist."""


class ChannelConflictError(ChannelServiceError):
    """Raised when a requested channel action is not allowed."""


@dataclass(frozen=True)
class _ResolvedChannel:
    enabled: bool
    bot_prefix: str
    settings: Dict[str, str]


class ChannelService:
    """High-level channel operations exposed to the API layer."""

    def __init__(
        self,
        *,
        project_root: str,
        secrets_path: str,
        channel_log_dir: str,
        config_store: ChannelConfigStore,
        runtime_manager: ChannelRuntimeManager,
        specs: Mapping[str, ChannelSpec],
    ):
        self.project_root = Path(project_root).resolve()
        self.secrets_path = Path(secrets_path).resolve()
        self.channel_log_dir = Path(channel_log_dir).resolve()
        self.config_store = config_store
        self.runtime_manager = runtime_manager
        self.specs = {normalize_channel_name(name): spec for name, spec in specs.items()}
        self._runtime_secrets_cache: Dict[str, str] = {}

    def get_state(self) -> Dict[str, Any]:
        return {"channels": self._build_rows()}

    def update_channel(
        self,
        *,
        channel_name: str,
        enabled: bool | None = None,
        bot_prefix: str | None = None,
        settings: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        spec = self._get_spec(channel_name)
        field_secret_flags = {field.key: bool(field.secret) for field in spec.fields}
        incoming = settings if isinstance(settings, Mapping) else {}
        allowed = set(field_secret_flags.keys())
        filtered_settings = {
            str(key): value
            for key, value in incoming.items()
            if str(key) in allowed
        }
        self.config_store.update_channel(
            spec.name,
            default_enabled=spec.default_enabled,
            default_bot_prefix=spec.default_bot_prefix,
            field_secret_flags=field_secret_flags,
            enabled=enabled,
            bot_prefix=bot_prefix,
            settings=filtered_settings,
        )
        if enabled is False and spec.runtime_mode == "subprocess":
            self.runtime_manager.stop_channel(spec.name)
        return self.get_state()

    def start_channel(self, channel_name: str) -> Dict[str, Any]:
        spec = self._get_spec(channel_name)
        runtime_secrets = self._load_runtime_secrets()
        resolved = self._resolve_config(spec, self._raw_channels().get(spec.name, {}), runtime_secrets)
        missing = self._missing_required(spec, resolved.settings)
        configured = len(missing) == 0
        if not resolved.enabled:
            raise ChannelConflictError("channel is disabled")
        if spec.runtime_mode != "subprocess":
            raise ChannelConflictError("channel does not support managed start")
        if not configured:
            missing_text = ", ".join(missing)
            raise ChannelConflictError(f"missing required settings: {missing_text}")
        launch = self._build_launch(spec, resolved.settings)
        self.runtime_manager.start_channel(
            spec.name,
            command=launch["command"],
            workdir=launch["workdir"],
            log_path=launch["log_path"],
            env=launch["env"],
        )
        return self.get_state()

    def stop_channel(self, channel_name: str) -> Dict[str, Any]:
        spec = self._get_spec(channel_name)
        if spec.runtime_mode != "subprocess":
            raise ChannelConflictError("channel does not support managed stop")
        self.runtime_manager.stop_channel(spec.name)
        return self.get_state()

    def restart_channel(self, channel_name: str) -> Dict[str, Any]:
        spec = self._get_spec(channel_name)
        runtime_secrets = self._load_runtime_secrets()
        resolved = self._resolve_config(spec, self._raw_channels().get(spec.name, {}), runtime_secrets)
        missing = self._missing_required(spec, resolved.settings)
        configured = len(missing) == 0
        if not resolved.enabled:
            raise ChannelConflictError("channel is disabled")
        if spec.runtime_mode != "subprocess":
            raise ChannelConflictError("channel does not support managed restart")
        if not configured:
            missing_text = ", ".join(missing)
            raise ChannelConflictError(f"missing required settings: {missing_text}")
        launch = self._build_launch(spec, resolved.settings)
        self.runtime_manager.stop_channel(spec.name)
        self.runtime_manager.start_channel(
            spec.name,
            command=launch["command"],
            workdir=launch["workdir"],
            log_path=launch["log_path"],
            env=launch["env"],
        )
        return self.get_state()

    def shutdown(self) -> None:
        self.runtime_manager.shutdown_all()

    def _build_rows(self) -> List[Dict[str, Any]]:
        self._runtime_secrets_cache = self._load_runtime_secrets()
        channels = self._raw_channels()
        return [self._build_row(spec, channels.get(spec.name, {})) for spec in self.specs.values()]

    def _build_row(self, spec: ChannelSpec, raw_row: Mapping[str, Any]) -> Dict[str, Any]:
        resolved = self._resolve_config(spec, raw_row, self._runtime_secrets_cache)
        missing_required = self._missing_required(spec, resolved.settings)
        configured = len(missing_required) == 0
        ready = (not resolved.enabled) or configured
        managed = spec.runtime_mode == "subprocess"
        runtime = self._runtime_view(spec)
        launch_command = self._launch_preview(spec, resolved.settings)
        fields = self._field_rows(spec, resolved.settings)
        launchable = bool(resolved.enabled and configured and managed and launch_command)

        return {
            "name": spec.name,
            "display_name": spec.display_name,
            "description": spec.description,
            "tag": spec.tag,
            "enabled": resolved.enabled,
            "configured": configured,
            "ready": ready,
            "missing_required": missing_required,
            "bot_prefix": resolved.bot_prefix,
            "managed": managed,
            "runtime_mode": spec.runtime_mode,
            "launchable": launchable,
            "launch_command": launch_command,
            "launch_hint": launch_command,
            "fields": fields,
            "runtime": runtime,
        }

    def _field_rows(self, spec: ChannelSpec, settings: Mapping[str, str]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for field in spec.fields:
            value = str(settings.get(field.key, "") or "")
            rows.append(
                {
                    "key": field.key,
                    "type": field.field_type,
                    "required": bool(field.required),
                    "secret": bool(field.secret),
                    "placeholder": field.placeholder,
                    "value": "" if field.secret else value,
                    "has_value": bool(value),
                }
            )
        return rows

    def _resolve_config(
        self,
        spec: ChannelSpec,
        raw_row: Mapping[str, Any],
        runtime_secrets: Mapping[str, str],
    ) -> _ResolvedChannel:
        row = raw_row if isinstance(raw_row, Mapping) else {}
        source_settings = row.get("settings", {})
        source_settings = source_settings if isinstance(source_settings, Mapping) else {}

        settings = {key: str(value or "").strip() for key, value in spec.default_settings.items()}
        for field in spec.fields:
            current = str(source_settings.get(field.key, settings.get(field.key, "")) or "").strip()
            if current:
                settings[field.key] = current
                continue
            fallback = self._lookup_fallback(field, runtime_secrets)
            settings[field.key] = fallback or settings.get(field.key, "")

        return _ResolvedChannel(
            enabled=bool(row.get("enabled", spec.default_enabled)),
            bot_prefix=str(row.get("bot_prefix", spec.default_bot_prefix) or "").strip(),
            settings=settings,
        )

    def _lookup_fallback(self, field: ChannelFieldSpec, runtime_secrets: Mapping[str, str]) -> str:
        for env_key in field.env_keys:
            direct = str(os.getenv(env_key, "") or "").strip()
            if direct:
                return direct
            secret_value = str(runtime_secrets.get(env_key, "") or "").strip()
            if secret_value:
                return secret_value
        return ""

    def _missing_required(self, spec: ChannelSpec, settings: Mapping[str, str]) -> List[str]:
        missing: List[str] = []
        for field in spec.fields:
            if not field.required:
                continue
            if not str(settings.get(field.key, "") or "").strip():
                missing.append(field.key)
        return missing

    def _runtime_view(self, spec: ChannelSpec) -> Dict[str, Any]:
        if spec.runtime_mode == "self":
            return {
                "status": "running",
                "running": True,
                "pid": os.getpid(),
                "started_at": None,
                "stopped_at": None,
                "exit_code": None,
                "last_error": "",
                "launch_count": 0,
                "command": [],
                "workdir": str(self.project_root),
                "log_path": "",
            }
        if spec.runtime_mode == "manual":
            return {
                "status": "manual",
                "running": False,
                "pid": None,
                "started_at": None,
                "stopped_at": None,
                "exit_code": None,
                "last_error": "",
                "launch_count": 0,
                "command": [],
                "workdir": str(self.project_root),
                "log_path": "",
            }
        return self.runtime_manager.snapshot(spec.name)

    def _launch_preview(self, spec: ChannelSpec, settings: Mapping[str, str]) -> str:
        if spec.runtime_mode == "self":
            host = str(settings.get("bind_host", "127.0.0.1") or "127.0.0.1").strip() or "127.0.0.1"
            port = str(settings.get("port", "7788") or "7788").strip() or "7788"
            python_bin = sys.executable or "python"
            entry_path = self.project_root / "entry_weclaw_console.py"
            return self._format_command([python_bin, str(entry_path), "--host", host, "--port", port])
        if spec.runtime_mode == "manual":
            command = str(settings.get("command", "") or "").strip()
            return command
        if spec.runtime_mode == "subprocess":
            python_bin = sys.executable or "python"
            script_path = self.project_root / spec.entry_script
            return self._format_command([python_bin, str(script_path)])
        return ""

    def _build_launch(self, spec: ChannelSpec, settings: Mapping[str, str]) -> Dict[str, Any]:
        if spec.runtime_mode != "subprocess" or not spec.entry_script:
            raise ChannelConflictError("channel does not define a managed process")
        python_bin = sys.executable or "python"
        script_path = self.project_root / spec.entry_script
        if not script_path.is_file():
            raise ChannelConflictError(f"entry script not found: {script_path}")
        command = [python_bin, str(script_path)]
        log_path = self.channel_log_dir / f"{spec.name}.log"
        env = os.environ.copy()
        for field in spec.fields:
            value = str(settings.get(field.key, "") or "").strip()
            if not value:
                continue
            for env_key in field.env_keys:
                env[env_key] = value
        return {
            "command": command,
            "workdir": str(self.project_root),
            "log_path": str(log_path),
            "env": env,
        }

    def _raw_channels(self) -> Dict[str, Dict[str, Any]]:
        return self.config_store.read_channels()

    def _get_spec(self, channel_name: str) -> ChannelSpec:
        name = normalize_channel_name(channel_name)
        spec = self.specs.get(name)
        if spec is None:
            raise ChannelNotFoundError("channel not found")
        return spec

    def _load_runtime_secrets(self) -> Dict[str, str]:
        if not self.secrets_path.is_file():
            return {}
        try:
            payload = yaml.safe_load(self.secrets_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}
        if not isinstance(payload, Mapping):
            return {}
        out: Dict[str, str] = {}
        for key, value in payload.items():
            text = str(value or "").strip()
            if text:
                out[str(key)] = text
        return out

    @staticmethod
    def _format_command(command: Iterable[str]) -> str:
        argv = [str(item) for item in command]
        if os.name == "nt":
            return subprocess.list2cmdline(argv)
        return shlex.join(argv)
