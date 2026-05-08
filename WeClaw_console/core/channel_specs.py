# -*- coding: utf-8 -*-
"""Static channel definitions for the console."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple


@dataclass(frozen=True)
class ChannelFieldSpec:
    key: str
    field_type: str = "text"
    required: bool = False
    secret: bool = False
    placeholder: str = ""
    env_keys: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ChannelSpec:
    name: str
    display_name: str
    description: str
    tag: str
    runtime_mode: str
    default_enabled: bool
    default_bot_prefix: str = ""
    default_settings: Mapping[str, str] = field(default_factory=dict)
    fields: Tuple[ChannelFieldSpec, ...] = field(default_factory=tuple)
    entry_script: str = ""


def default_channel_specs() -> Dict[str, ChannelSpec]:
    return {
        "web": ChannelSpec(
            name="web",
            display_name="Browser",
            description="Web Console (local)",
            tag="builtin",
            runtime_mode="self",
            default_enabled=True,
            default_settings={
                "base_url": "http://127.0.0.1:7788",
                "bind_host": "127.0.0.1",
                "port": "7788",
            },
            fields=(
                ChannelFieldSpec(key="base_url", placeholder="http://127.0.0.1:7788"),
                ChannelFieldSpec(key="bind_host", placeholder="127.0.0.1"),
                ChannelFieldSpec(key="port", field_type="number", placeholder="7788"),
            ),
        ),
        "cli": ChannelSpec(
            name="cli",
            display_name="CLI",
            description="Local command line",
            tag="builtin",
            runtime_mode="manual",
            default_enabled=True,
            default_settings={
                "command": ".\\.venv\\Scripts\\python.exe channels\\cli.py",
            },
            fields=(
                ChannelFieldSpec(
                    key="command",
                    placeholder=".\\.venv\\Scripts\\python.exe channels\\cli.py",
                ),
            ),
        ),
        "qq": ChannelSpec(
            name="qq",
            display_name="QQ",
            description="QQ channel (botpy)",
            tag="external",
            runtime_mode="subprocess",
            default_enabled=False,
            default_settings={
                "app_id": "",
                "client_secret": "",
            },
            fields=(
                ChannelFieldSpec(
                    key="app_id",
                    required=True,
                    placeholder="Bot App ID",
                    env_keys=("BOTPY_APPID",),
                ),
                ChannelFieldSpec(
                    key="client_secret",
                    field_type="password",
                    required=True,
                    secret=True,
                    placeholder="Bot Secret",
                    env_keys=("BOTPY_SECRET",),
                ),
            ),
            entry_script="channels/runners/qq_runner.py",
        ),
        "discord": ChannelSpec(
            name="discord",
            display_name="Discord",
            description="Discord channel",
            tag="external",
            runtime_mode="subprocess",
            default_enabled=False,
            default_settings={
                "bot_token": "",
                "http_proxy": "",
                "http_proxy_auth": "",
                "guild_id": "",
            },
            fields=(
                ChannelFieldSpec(
                    key="bot_token",
                    field_type="password",
                    required=True,
                    secret=True,
                    placeholder="Discord Bot Token",
                    env_keys=("DISCORD_BOT_TOKEN",),
                ),
                ChannelFieldSpec(
                    key="http_proxy",
                    placeholder="http://127.0.0.1:7890",
                    env_keys=("DISCORD_HTTP_PROXY",),
                ),
                ChannelFieldSpec(
                    key="http_proxy_auth",
                    field_type="password",
                    secret=True,
                    placeholder="username:password",
                    env_keys=("DISCORD_HTTP_PROXY_AUTH",),
                ),
                ChannelFieldSpec(
                    key="guild_id",
                    placeholder="Guild ID (optional)",
                    env_keys=("DISCORD_GUILD_ID",),
                ),
            ),
            entry_script="channels/runners/discord_runner.py",
        ),
        "plugin_channel_host": ChannelSpec(
            name="plugin_channel_host",
            display_name="Plugin Channel Host",
            description="TypeScript plugin channel host",
            tag="external",
            runtime_mode="subprocess",
            default_enabled=False,
            default_settings={
                "bind_host": "127.0.0.1",
                "port": "8765",
                "gateway_base_url": "http://127.0.0.1:7788/api/v1",
                "plugin_dirs": "",
            },
            fields=(
                ChannelFieldSpec(
                    key="bind_host",
                    placeholder="127.0.0.1",
                    env_keys=("WECLAW_PLUGIN_CHANNEL_HOST_BIND",),
                ),
                ChannelFieldSpec(
                    key="port",
                    field_type="number",
                    placeholder="8765",
                    env_keys=("WECLAW_PLUGIN_CHANNEL_HOST_PORT",),
                ),
                ChannelFieldSpec(
                    key="gateway_base_url",
                    placeholder="http://127.0.0.1:7788/api/v1",
                    env_keys=("WECLAW_GATEWAY_BASE_URL",),
                ),
                ChannelFieldSpec(
                    key="plugin_dirs",
                    placeholder="Optional extra plugin directories separated by path delimiter",
                    env_keys=("WECLAW_PLUGIN_CHANNEL_PLUGIN_DIRS",),
                ),
            ),
            entry_script="channels/runners/plugin_channel_host_runner.py",
        ),
    }


def normalize_channel_name(value: str) -> str:
    return str(value or "").strip().lower()


def default_channel_names() -> Tuple[str, ...]:
    return tuple(default_channel_specs().keys())


def coerce_text_settings(data: Mapping[str, Any] | None) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not isinstance(data, Mapping):
        return out
    for key, value in data.items():
        out[str(key)] = str(value or "").strip()
    return out
