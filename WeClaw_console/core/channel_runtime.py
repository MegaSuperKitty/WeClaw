# -*- coding: utf-8 -*-
"""Runtime process management for console channels."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import threading
import time
from typing import Dict, IO, Iterable, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tail_text(path: Path, max_lines: int = 10, max_chars: int = 600) -> str:
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    text = "\n".join(lines[-max_lines:]).strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


@dataclass
class _RuntimeRecord:
    status: str = "stopped"
    running: bool = False
    pid: Optional[int] = None
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None
    exit_code: Optional[int] = None
    last_error: str = ""
    launch_count: int = 0
    command: List[str] = field(default_factory=list)
    workdir: str = ""
    log_path: str = ""
    process: Optional[subprocess.Popen[str]] = None
    log_handle: Optional[IO[str]] = None


class ChannelRuntimeManager:
    """Track and control subprocess-backed channels."""

    def __init__(self, log_dir: str, startup_grace_seconds: float = 1.0):
        self.log_dir = Path(log_dir).resolve()
        self.startup_grace_seconds = max(0.0, float(startup_grace_seconds))
        self._lock = threading.Lock()
        self._records: Dict[str, _RuntimeRecord] = {}

    def snapshot(self, channel_name: str) -> Dict[str, object]:
        with self._lock:
            record = self._ensure_record(channel_name)
            self._refresh_locked(channel_name, record)
            return self._snapshot_record(record)

    def start_channel(
        self,
        channel_name: str,
        *,
        command: Iterable[str],
        workdir: str,
        log_path: str,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, object]:
        argv = [str(item) for item in command if str(item).strip()]
        if not argv:
            raise ValueError("launch command is empty")

        with self._lock:
            record = self._ensure_record(channel_name)
            self._refresh_locked(channel_name, record)
            if record.running and record.process is not None:
                return self._snapshot_record(record)

            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_file = Path(log_path).resolve()
            log_file.parent.mkdir(parents=True, exist_ok=True)
            self._close_record_io_locked(record)
            handle = log_file.open("a", encoding="utf-8", buffering=1)
            handle.write(f"\n[{_utc_now_iso()}] starting: {' '.join(argv)}\n")
            handle.flush()

            try:
                proc = subprocess.Popen(
                    argv,
                    cwd=str(Path(workdir).resolve()),
                    stdin=subprocess.DEVNULL,
                    stdout=handle,
                    stderr=handle,
                    text=True,
                    env=env,
                    start_new_session=True,
                )
            except Exception as exc:
                try:
                    handle.write(f"[{_utc_now_iso()}] start failed: {exc}\n")
                    handle.flush()
                except Exception:
                    pass
                try:
                    handle.close()
                except Exception:
                    pass
                record.process = None
                record.log_handle = None
                record.running = False
                record.status = "failed"
                record.pid = None
                record.started_at = None
                record.stopped_at = _utc_now_iso()
                record.exit_code = None
                record.last_error = str(exc)
                record.command = list(argv)
                record.workdir = str(Path(workdir).resolve())
                record.log_path = str(log_file)
                return self._snapshot_record(record)

            record.process = proc
            record.log_handle = handle
            record.running = True
            record.status = "running"
            record.pid = int(proc.pid) if proc.pid else None
            record.started_at = _utc_now_iso()
            record.stopped_at = None
            record.exit_code = None
            record.last_error = ""
            record.launch_count += 1
            record.command = list(argv)
            record.workdir = str(Path(workdir).resolve())
            record.log_path = str(log_file)

        if self.startup_grace_seconds:
            time.sleep(self.startup_grace_seconds)

        with self._lock:
            record = self._ensure_record(channel_name)
            self._refresh_locked(channel_name, record)
            if not record.running and record.status == "failed" and not record.last_error:
                record.last_error = _tail_text(Path(record.log_path)) or "Process exited during startup."
            return self._snapshot_record(record)

    def stop_channel(self, channel_name: str, timeout_seconds: float = 5.0) -> Dict[str, object]:
        with self._lock:
            record = self._ensure_record(channel_name)
            self._refresh_locked(channel_name, record)
            proc = record.process
            if proc is None:
                record.running = False
                if record.status == "":
                    record.status = "stopped"
                return self._snapshot_record(record)

            try:
                proc.terminate()
                proc.wait(timeout=max(0.1, float(timeout_seconds)))
            except Exception:
                try:
                    proc.kill()
                    proc.wait(timeout=max(0.1, float(timeout_seconds)))
                except Exception:
                    pass

            exit_code = proc.poll()
            self._close_record_process_locked(record)
            record.running = False
            record.status = "stopped"
            record.pid = None
            record.stopped_at = _utc_now_iso()
            record.exit_code = exit_code
            record.last_error = ""
            return self._snapshot_record(record)

    def shutdown_all(self) -> None:
        with self._lock:
            names = list(self._records.keys())
        for name in names:
            try:
                self.stop_channel(name)
            except Exception:
                continue

    def _ensure_record(self, channel_name: str) -> _RuntimeRecord:
        if channel_name not in self._records:
            self._records[channel_name] = _RuntimeRecord()
        return self._records[channel_name]

    def _refresh_locked(self, channel_name: str, record: _RuntimeRecord) -> None:
        proc = record.process
        if proc is None:
            if not record.status:
                record.status = "stopped"
            return

        code = proc.poll()
        if code is None:
            record.running = True
            record.status = "running"
            record.pid = int(proc.pid) if proc.pid else None
            return

        self._close_record_process_locked(record)
        record.running = False
        record.pid = None
        record.stopped_at = _utc_now_iso()
        record.exit_code = code
        if code == 0:
            record.status = "stopped"
            if record.last_error:
                record.last_error = ""
        else:
            record.status = "failed"
            tail = _tail_text(Path(record.log_path))
            record.last_error = tail or f"Process exited with code {code}."

    def _close_record_io_locked(self, record: _RuntimeRecord) -> None:
        handle = record.log_handle
        record.log_handle = None
        if handle is None:
            return
        try:
            handle.flush()
        except Exception:
            pass
        try:
            handle.close()
        except Exception:
            pass

    def _close_record_process_locked(self, record: _RuntimeRecord) -> None:
        record.process = None
        self._close_record_io_locked(record)

    @staticmethod
    def _snapshot_record(record: _RuntimeRecord) -> Dict[str, object]:
        return {
            "status": record.status,
            "running": record.running,
            "pid": record.pid,
            "started_at": record.started_at,
            "stopped_at": record.stopped_at,
            "exit_code": record.exit_code,
            "last_error": record.last_error,
            "launch_count": record.launch_count,
            "command": list(record.command),
            "workdir": record.workdir,
            "log_path": record.log_path,
        }
