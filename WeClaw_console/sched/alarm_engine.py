# -*- coding: utf-8 -*-
"""Unified alarm scheduler for once/daily/weekly background prompts."""

from __future__ import annotations

from datetime import datetime, timedelta
import threading
import time
from typing import Any, Dict, List, Optional
import uuid

from .store import JsonStore, deep_copy_dict, now_iso


WEEKDAY_MAP = {
    "mon": 0,
    "monday": 0,
    "tue": 1,
    "tuesday": 1,
    "wed": 2,
    "wednesday": 2,
    "thu": 3,
    "thursday": 3,
    "fri": 4,
    "friday": 4,
    "sat": 5,
    "saturday": 5,
    "sun": 6,
    "sunday": 6,
}


def _iso_from_timestamp(ts: float | None) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(float(ts)).isoformat(timespec="seconds")


def _channel_from_user_id(user_id: str) -> Dict[str, str]:
    text = str(user_id or "").strip()
    if ":" in text:
        channel, channel_user_id = text.split(":", 1)
        return {
            "channel": channel or "unknown",
            "channel_user_id": channel_user_id or "",
        }
    if text == "debug_user":
        return {"channel": "cli", "channel_user_id": text}
    return {"channel": "unknown", "channel_user_id": text}


class AlarmEngine:
    """Persisted alarm manager with one unified schedule model."""

    def __init__(self, gateway, data_path: str):
        self.gateway = gateway
        self.store = JsonStore(data_path)
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._load()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="weclaw-alarm-loop")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def list_jobs(self) -> List[Dict[str, Any]]:
        with self._lock:
            rows = [deep_copy_dict(job) for job in self._jobs.values()]
        rows.sort(key=lambda row: (row.get("status") != "active", row.get("updated_at", "")), reverse=True)
        return rows

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._jobs.get(str(job_id or "").strip())
            return deep_copy_dict(row) if isinstance(row, dict) else None

    def create_job(
        self,
        *,
        schedule_type: str,
        schedule: Dict[str, Any],
        user_id: str,
        session_name: str,
        prompt: str,
        source: str = "alarm",
    ) -> Dict[str, Any]:
        clean_prompt = str(prompt or "").strip()
        if not clean_prompt:
            raise ValueError("prompt_required")
        clean_user_id = str(user_id or "web:local").strip() or "web:local"
        clean_session_name = str(session_name or "").strip()
        clean_type = str(schedule_type or "").strip().lower()
        clean_schedule = self._normalize_schedule(clean_type, schedule)
        next_run_ts = self._compute_next_run_ts(clean_type, clean_schedule, time.time())
        if next_run_ts is None:
            raise ValueError("next_run_time_required")
        channel_info = _channel_from_user_id(clean_user_id)
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "schedule_type": clean_type,
            "schedule": clean_schedule,
            "user_id": clean_user_id,
            "session_name": clean_session_name,
            "channel": channel_info["channel"],
            "channel_user_id": channel_info["channel_user_id"],
            "prompt": clean_prompt,
            "source": str(source or "alarm").strip() or "alarm",
            "status": "active",
            "paused": False,
            "running": False,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "next_run_ts": float(next_run_ts),
            "next_run_at": _iso_from_timestamp(next_run_ts),
            "last_run_at": "",
            "last_status": "never",
            "last_result": "",
            "run_count": 0,
            "finished_at": "",
        }
        with self._lock:
            self._jobs[job_id] = job
            self._save_locked()
        return deep_copy_dict(job)

    def schedule_tool_alarm(
        self,
        *,
        user_id: str,
        session_name: str,
        schedule_type: str,
        schedule: Dict[str, Any],
        prompt: str,
    ) -> Dict[str, Any]:
        return self.create_job(
            schedule_type=schedule_type,
            schedule=schedule,
            user_id=user_id,
            session_name=session_name,
            prompt=prompt,
            source="alarm_tool",
        )

    def pause_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._update_pause_state(job_id, paused=True)

    def resume_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        clean_job_id = str(job_id or "").strip()
        with self._lock:
            job = self._jobs.get(clean_job_id)
            if not job:
                return None
            if str(job.get("status") or "").strip() == "finished":
                return deep_copy_dict(job)
            job["paused"] = False
            job["status"] = "active"
            job["next_run_ts"] = self._compute_next_run_ts(
                str(job.get("schedule_type") or ""),
                dict(job.get("schedule") or {}),
                time.time(),
            )
            job["next_run_at"] = _iso_from_timestamp(job.get("next_run_ts"))
            job["updated_at"] = now_iso()
            self._save_locked()
            return deep_copy_dict(job)

    def cancel_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        clean_job_id = str(job_id or "").strip()
        with self._lock:
            job = self._jobs.get(clean_job_id)
            if not job:
                return None
            job["paused"] = False
            job["running"] = False
            job["status"] = "finished"
            job["last_status"] = "cancelled"
            job["finished_at"] = now_iso()
            job["next_run_ts"] = 0.0
            job["next_run_at"] = ""
            job["updated_at"] = now_iso()
            self._save_locked()
            return deep_copy_dict(job)

    def _update_pause_state(self, job_id: str, *, paused: bool) -> Optional[Dict[str, Any]]:
        clean_job_id = str(job_id or "").strip()
        with self._lock:
            job = self._jobs.get(clean_job_id)
            if not job:
                return None
            if str(job.get("status") or "").strip() == "finished":
                return deep_copy_dict(job)
            job["paused"] = paused
            job["status"] = "paused" if paused else "active"
            job["updated_at"] = now_iso()
            self._save_locked()
            return deep_copy_dict(job)

    def _loop(self) -> None:
        while self._running:
            due_ids: List[str] = []
            now_ts = time.time()
            with self._lock:
                for job_id, job in self._jobs.items():
                    if str(job.get("status") or "").strip() == "finished":
                        continue
                    if bool(job.get("paused")):
                        continue
                    if bool(job.get("running")):
                        continue
                    next_ts = float(job.get("next_run_ts", 0) or 0)
                    if next_ts and next_ts <= now_ts:
                        due_ids.append(job_id)
            for job_id in due_ids:
                threading.Thread(target=self._execute_job, args=(job_id,), daemon=True).start()
            time.sleep(1.0)

    def _execute_job(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.get("running") or job.get("paused") or job.get("status") == "finished":
                return
            job["running"] = True
            job["updated_at"] = now_iso()
            self._save_locked()
            snap = deep_copy_dict(job)

        status = "completed"
        result = ""
        try:
            dispatch_result = self.gateway.dispatch_background_prompt(
                user_id=snap["user_id"],
                session_name=snap.get("session_name", ""),
                content=snap.get("prompt", ""),
                source="alarm",
            )
            status = "completed" if dispatch_result.get("success") else "failed"
            result = dispatch_result.get("final_text") or dispatch_result.get("error") or ""
        except Exception as exc:
            status = "failed"
            result = f"{exc}"

        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["running"] = False
            job["last_run_at"] = now_iso()
            job["last_status"] = status
            job["last_result"] = str(result or "")[:2000]
            job["run_count"] = int(job.get("run_count", 0) or 0) + 1
            schedule_type = str(job.get("schedule_type") or "").strip()
            schedule = dict(job.get("schedule") or {})
            if schedule_type == "once":
                job["status"] = "finished"
                job["finished_at"] = now_iso()
                job["next_run_ts"] = 0.0
                job["next_run_at"] = ""
            else:
                job["status"] = "active"
                next_run_ts = self._compute_next_run_ts(schedule_type, schedule, time.time())
                job["next_run_ts"] = float(next_run_ts or 0)
                job["next_run_at"] = _iso_from_timestamp(next_run_ts)
            job["updated_at"] = now_iso()
            self._save_locked()

    def _normalize_schedule(self, schedule_type: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
        row = dict(schedule or {})
        if schedule_type == "once":
            run_at = str(row.get("run_at") or "").strip()
            if not run_at:
                raise ValueError("run_at_required")
            dt = self._parse_datetime(run_at)
            if dt is None:
                raise ValueError("invalid_run_at")
            return {"run_at": dt.isoformat(timespec="seconds")}
        if schedule_type == "daily":
            hour = self._coerce_int(row.get("hour"), "hour", minimum=0, maximum=23)
            minute = self._coerce_int(row.get("minute"), "minute", minimum=0, maximum=59)
            second = self._coerce_int(row.get("second", 0), "second", minimum=0, maximum=59)
            return {"hour": hour, "minute": minute, "second": second}
        if schedule_type == "weekly":
            weekdays = self._normalize_weekdays(row.get("weekdays"))
            hour = self._coerce_int(row.get("hour"), "hour", minimum=0, maximum=23)
            minute = self._coerce_int(row.get("minute"), "minute", minimum=0, maximum=59)
            second = self._coerce_int(row.get("second", 0), "second", minimum=0, maximum=59)
            return {"weekdays": weekdays, "hour": hour, "minute": minute, "second": second}
        raise ValueError("unsupported_schedule_type")

    def _normalize_weekdays(self, raw: Any) -> List[int]:
        values = list(raw or [])
        if not values:
            raise ValueError("weekdays_required")
        items: List[int] = []
        for value in values:
            if isinstance(value, int):
                if value < 0 or value > 6:
                    raise ValueError("invalid_weekday")
                items.append(value)
                continue
            text = str(value or "").strip().lower()
            if text.isdigit():
                number = int(text)
                if number < 0 or number > 6:
                    raise ValueError("invalid_weekday")
                items.append(number)
                continue
            if text not in WEEKDAY_MAP:
                raise ValueError("invalid_weekday")
            items.append(WEEKDAY_MAP[text])
        return sorted(set(items))

    def _compute_next_run_ts(self, schedule_type: str, schedule: Dict[str, Any], from_ts: float) -> Optional[float]:
        now = datetime.fromtimestamp(float(from_ts))
        if schedule_type == "once":
            dt = self._parse_datetime(str(schedule.get("run_at") or ""))
            if dt is None or dt <= now:
                return None
            return dt.timestamp()
        if schedule_type == "daily":
            candidate = now.replace(
                hour=int(schedule.get("hour", 0)),
                minute=int(schedule.get("minute", 0)),
                second=int(schedule.get("second", 0)),
                microsecond=0,
            )
            if candidate <= now:
                candidate = candidate + timedelta(days=1)
            return candidate.timestamp()
        if schedule_type == "weekly":
            weekdays = list(schedule.get("weekdays") or [])
            hour = int(schedule.get("hour", 0))
            minute = int(schedule.get("minute", 0))
            second = int(schedule.get("second", 0))
            for day_offset in range(0, 8):
                candidate_day = now + timedelta(days=day_offset)
                if candidate_day.weekday() not in weekdays:
                    continue
                candidate = candidate_day.replace(hour=hour, minute=minute, second=second, microsecond=0)
                if candidate > now:
                    return candidate.timestamp()
            return None
        return None

    def _parse_datetime(self, value: str) -> Optional[datetime]:
        text = str(value or "").strip()
        if not text:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            return None

    def _coerce_int(self, value: Any, field_name: str, *, minimum: int, maximum: int) -> int:
        try:
            number = int(value)
        except Exception as exc:
            raise ValueError(f"{field_name}_invalid") from exc
        if number < minimum or number > maximum:
            raise ValueError(f"{field_name}_invalid")
        return number

    def _load(self) -> None:
        raw = self.store.read({"jobs": []})
        jobs = raw.get("jobs", []) if isinstance(raw, dict) else []
        if not isinstance(jobs, list):
            jobs = []
        with self._lock:
            self._jobs = {}
            for row in jobs:
                if not isinstance(row, dict):
                    continue
                job_id = str(row.get("id") or "").strip()
                if not job_id:
                    continue
                row["running"] = False
                row.setdefault("status", "active")
                row.setdefault("paused", False)
                row.setdefault("next_run_ts", 0.0)
                row.setdefault("next_run_at", _iso_from_timestamp(row.get("next_run_ts")))
                row.setdefault("channel", _channel_from_user_id(str(row.get("user_id") or "")).get("channel", "unknown"))
                row.setdefault("channel_user_id", _channel_from_user_id(str(row.get("user_id") or "")).get("channel_user_id", ""))
                self._jobs[job_id] = row

    def _save_locked(self) -> None:
        payload = {"jobs": list(self._jobs.values())}
        self.store.write(payload)
