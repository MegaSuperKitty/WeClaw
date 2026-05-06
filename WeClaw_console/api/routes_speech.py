# -*- coding: utf-8 -*-
"""Local speech transcription routes (offline, no external API)."""

from __future__ import annotations

import os
from pathlib import Path
import time
from typing import Optional
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile


router = APIRouter(prefix="/api/v1/speech", tags=["speech"])


def _transcriber(request: Request):
    transcriber = getattr(request.app.state, "speech_transcriber", None)
    if transcriber is None:
        raise HTTPException(status_code=503, detail="speech_transcriber_not_ready")
    return transcriber


@router.get("/status")
def speech_status(request: Request):
    transcriber = _transcriber(request)
    return {"success": True, "status": transcriber.status()}


@router.post("/transcribe")
async def speech_transcribe(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form(""),
    task: str = Form("transcribe"),
):
    transcriber = _transcriber(request)

    filename = str(getattr(file, "filename", "") or "voice_input.webm")
    suffix = Path(filename).suffix or ".webm"

    tmp_dir = Path(transcriber.cache_dir).parent / ".speech_uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"{int(time.time() * 1000)}_{uuid.uuid4().hex}{suffix}"

    total_size = 0
    max_bytes = transcriber.max_audio_bytes()

    try:
        with tmp_path.open("wb") as handle:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > max_bytes:
                    raise HTTPException(status_code=400, detail=f"audio_too_large(max={max_bytes} bytes)")
                handle.write(chunk)

        if total_size <= 0:
            raise HTTPException(status_code=400, detail="empty_audio")

        result = transcriber.transcribe_file(str(tmp_path), language=language, task=task)
        return {
            "success": True,
            "result": result,
            "audio_size": total_size,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            await file.close()
        except Exception:
            pass
        try:
            if tmp_path.exists():
                os.remove(tmp_path)
        except Exception:
            pass
