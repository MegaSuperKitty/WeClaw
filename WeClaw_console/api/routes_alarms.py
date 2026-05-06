# -*- coding: utf-8 -*-
"""Alarm routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/api/v1/alarms", tags=["alarms"])


def _engine(request: Request):
    engine = getattr(request.app.state, "alarm_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="alarm_not_ready")
    return engine


@router.get("")
def list_alarms(request: Request):
    engine = _engine(request)
    jobs = engine.list_jobs()
    active = [row for row in jobs if str(row.get("status") or "").strip() != "finished"]
    finished = [row for row in jobs if str(row.get("status") or "").strip() == "finished"]
    return {"active_jobs": active, "finished_jobs": finished}


@router.get("/{job_id}")
def get_alarm(job_id: str, request: Request):
    engine = _engine(request)
    job = engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job": job}


@router.post("/{job_id}/pause")
def pause_alarm(job_id: str, request: Request):
    engine = _engine(request)
    job = engine.pause_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job": job}


@router.post("/{job_id}/resume")
def resume_alarm(job_id: str, request: Request):
    engine = _engine(request)
    job = engine.resume_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job": job}


@router.post("/{job_id}/cancel")
def cancel_alarm(job_id: str, request: Request):
    engine = _engine(request)
    job = engine.cancel_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job": job}
