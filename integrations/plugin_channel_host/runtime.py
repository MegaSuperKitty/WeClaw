# -*- coding: utf-8 -*-
"""Workspace-backed runtime preparation for the plugin channel host."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Iterable

from core.workspace.layout import ensure_workspace_layout_for_source


RUNTIME_MANIFEST = ".plugin_channel_host_runtime.json"


@dataclass(frozen=True)
class PreparedPluginChannelHost:
    runtime_root: str
    dist_entry: str
    node_bin: str
    npm_bin: str
    source_hash: str
    install_hash: str


class PluginChannelHostRuntime:
    """Prepare and maintain a workspace-local plugin channel host runtime."""

    def __init__(self, project_root: str, agent_id: str | None = None):
        self.project_root = Path(project_root).resolve()
        self.layout = ensure_workspace_layout_for_source(str(self.project_root), agent_id=agent_id)
        self.source_root = self.project_root / "channel_services" / "plugin_channel_host"
        self.runtime_root = Path(self.layout.plugin_channel_host_root).resolve()
        self.manifest_path = self.runtime_root / RUNTIME_MANIFEST

    def ensure_ready(self) -> PreparedPluginChannelHost:
        if not self.source_root.is_dir():
            raise RuntimeError(f"plugin channel host source not found: {self.source_root}")

        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self._sync_source_tree()

        npm_bin = shutil.which("npm.cmd") or shutil.which("npm")
        node_bin = shutil.which("node.exe") or shutil.which("node")
        if not npm_bin:
            raise RuntimeError("npm executable not found")
        if not node_bin:
            raise RuntimeError("node executable not found")

        source_hash = self._hash_paths([
            self.runtime_root / "src",
            self.runtime_root / "plugins",
            self.runtime_root / "package.json",
            self.runtime_root / "tsconfig.json",
        ])
        install_hash = self._hash_paths([
            self.runtime_root / "package-lock.json",
            self.runtime_root / "package.json",
        ])
        manifest = self._load_manifest()

        if manifest.get("install_hash") != install_hash or not (self.runtime_root / "node_modules").is_dir():
            self._run_command([npm_bin, "install"], cwd=self.runtime_root)
            manifest["install_hash"] = install_hash

        if manifest.get("build_hash") != source_hash or not (self.runtime_root / "dist" / "index.js").is_file():
            self._run_command([npm_bin, "run", "build"], cwd=self.runtime_root)
            manifest["build_hash"] = source_hash

        manifest["source_hash"] = source_hash
        manifest["runtime_root"] = str(self.runtime_root)
        self._save_manifest(manifest)

        return PreparedPluginChannelHost(
            runtime_root=str(self.runtime_root),
            dist_entry=str((self.runtime_root / "dist" / "index.js").resolve()),
            node_bin=str(Path(node_bin).resolve()),
            npm_bin=str(Path(npm_bin).resolve()),
            source_hash=source_hash,
            install_hash=install_hash,
        )

    def runtime_plugin_dirs(self) -> list[str]:
        echo_plugin = self.runtime_root / "plugins" / "echo_channel"
        return [str(echo_plugin.resolve())]

    def _sync_source_tree(self) -> None:
        self._replace_path(self.source_root / "src", self.runtime_root / "src")
        self._replace_path(self.source_root / "plugins", self.runtime_root / "plugins")
        for name in ("package.json", "package-lock.json", "tsconfig.json", "README.md"):
            source = self.source_root / name
            if source.exists():
                shutil.copy2(source, self.runtime_root / name)

    def _replace_path(self, source: Path, target: Path) -> None:
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.unlink()
        if source.is_dir():
            shutil.copytree(source, target)
            return
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def _load_manifest(self) -> dict[str, str]:
        if not self.manifest_path.is_file():
            return {}
        try:
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _save_manifest(self, payload: dict[str, str]) -> None:
        self.manifest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _hash_paths(self, paths: Iterable[Path]) -> str:
        digest = hashlib.sha256()
        for path in sorted({Path(item).resolve() for item in paths}, key=lambda item: str(item).lower()):
            if not path.exists():
                digest.update(f"missing:{path.name}\n".encode("utf-8"))
                continue
            if path.is_file():
                digest.update(f"file:{path.name}\n".encode("utf-8"))
                digest.update(path.read_bytes())
                continue
            for child in sorted(path.rglob("*"), key=lambda item: str(item.relative_to(path)).replace("\\", "/")):
                relative = str(child.relative_to(path)).replace("\\", "/")
                if child.is_dir():
                    digest.update(f"dir:{path.name}/{relative}\n".encode("utf-8"))
                    continue
                digest.update(f"file:{path.name}/{relative}\n".encode("utf-8"))
                digest.update(child.read_bytes())
        return digest.hexdigest()

    @staticmethod
    def _run_command(command: list[str], *, cwd: Path) -> None:
        completed = subprocess.run(
            [str(item) for item in command],
            cwd=str(cwd),
            check=False,
            text=True,
            env=os.environ.copy(),
        )
        if completed.returncode != 0:
            raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}")
