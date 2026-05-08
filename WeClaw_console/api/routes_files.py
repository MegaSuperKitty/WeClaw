# -*- coding: utf-8 -*-
"""File upload routes."""

from __future__ import annotations

import os
from pathlib import Path
import re
import time

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse


router = APIRouter(prefix="/api/v1/files", tags=["files"])


def _runtime(request: Request):
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="runtime_not_ready")
    return runtime


def _safe_name(name: str) -> str:
    base = os.path.basename(name or "")
    base = re.sub(r"[^a-zA-Z0-9._\-\u4e00-\u9fff]", "_", base)
    return base or "upload.bin"


def _safe_user(user_id: str) -> str:
    text = (user_id or "").strip() or "web:local"
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", text)


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Form("web:local"),
):
    runtime = _runtime(request)

    uid = _safe_user(user_id)
    safe_name = _safe_name(file.filename or "upload.bin")

    upload_dir = Path(runtime.agent_root) / "assets" / "uploads" / uid
    upload_dir.mkdir(parents=True, exist_ok=True)

    final_name = f"{int(time.time())}_{safe_name}"
    path = upload_dir / final_name

    size = 0
    try:
        with open(path, "wb") as handle:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                size += len(chunk)
    finally:
        await file.close()

    saved = runtime.register_uploaded_file(user_id, str(path), safe_name, size)
    return {"file": saved}


@router.get("/content")
def get_uploaded_file(
    request: Request,
    path: str = Query(...),
):
    runtime = _runtime(request)
    target = Path(runtime.agent_root) / str(path or "").replace("\\", "/").lstrip("/")
    target = target.resolve()
    root = Path(runtime.agent_root).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="path_outside_workspace_root") from exc
    if not target.is_file():
        raise HTTPException(status_code=404, detail="file_not_found")
    return FileResponse(str(target))
