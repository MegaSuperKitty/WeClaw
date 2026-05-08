# -*- coding: utf-8 -*-
"""Workspace-scoped Markdown docs routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request


router = APIRouter(prefix="/api/v1/docs", tags=["docs"])


def _runtime(request: Request):
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="runtime_not_ready")
    return runtime


def _docs_root(request: Request) -> Path:
    runtime = _runtime(request)
    return (Path(runtime.agent_root) / "docs").resolve()


def _is_markdown(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".md"


def _build_tree_node(path: Path, root: Path):
    if path.is_dir():
        children = []
        for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
            node = _build_tree_node(child, root)
            if node is not None:
                children.append(node)
        if path != root and not children:
            return None
        relative = "" if path == root else path.relative_to(root).as_posix()
        return {
            "type": "dir",
            "name": path.name if path != root else "docs",
            "path": relative,
            "children": children,
        }
    if not _is_markdown(path):
        return None
    return {
        "type": "file",
        "name": path.name,
        "path": path.relative_to(root).as_posix(),
    }


def _resolve_markdown_path(root: Path, relative_path: str) -> Path:
    clean = str(relative_path or "").strip().replace("\\", "/").lstrip("/")
    if not clean:
        raise HTTPException(status_code=400, detail="path_required")
    target = (root / clean).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="path_outside_docs_root") from exc
    if not _is_markdown(target):
        raise HTTPException(status_code=404, detail="markdown_not_found")
    return target


@router.get("/tree")
def get_docs_tree(request: Request):
    root = _docs_root(request)
    if not root.exists():
        return {
            "success": True,
            "root": str(root),
            "tree": {"type": "dir", "name": "docs", "path": "", "children": []},
        }
    if not root.is_dir():
        raise HTTPException(status_code=500, detail="docs_root_invalid")
    return {"success": True, "root": str(root), "tree": _build_tree_node(root, root)}


@router.get("/content")
def get_docs_content(
    request: Request,
    path: str = Query(..., description="Relative markdown path under the workspace docs root"),
):
    root = _docs_root(request)
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=404, detail="docs_root_not_found")
    target = _resolve_markdown_path(root, path)
    return {
        "success": True,
        "path": target.relative_to(root).as_posix(),
        "content": target.read_text(encoding="utf-8"),
    }
