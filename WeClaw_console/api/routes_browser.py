# -*- coding: utf-8 -*-
"""Browser routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/browser", tags=["browser"])


class BrowserTargetPayload(BaseModel):
    target_id: str = ""


class BrowserScreenshotPayload(BrowserTargetPayload):
    full_page: bool = True


class BrowserActPayload(BrowserTargetPayload):
    kind: str = ""
    selector: str = ""
    value: str = ""
    expression: str = ""
    url: str = ""
    key: str = ""
    file_path: str = ""
    timeout_ms: int = 0


class BrowserProfilePayload(BaseModel):
    profile_id: str = ""
    driver: str = "managed"
    channel: str = "chrome"
    executable_path: str = ""
    user_data_dir: str = ""
    profile_directory: str = ""
    cdp_host: str = "127.0.0.1"
    cdp_port: int = 18800
    cdp_url: str = ""
    attach_only: bool = False


class BrowserUserConfigPayload(BaseModel):
    selected_mode: str = ""
    browser_executable_path: str = ""
    browser_family: str = ""
    user_data_dir: str = ""
    profile_directory: str = ""
    remote_debugging_port: int = 0
    preferred_browser_name: str = ""


class BrowserLaunchPayload(BrowserUserConfigPayload):
    pass


class BrowserTabOpenPayload(BaseModel):
    url: str = "about:blank"


class SessionBindingPayload(BaseModel):
    profile_id: str = ""
    session_id: str = ""
    tab_id: str = ""


def _service(request: Request):
    service = getattr(request.app.state, "browser_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="browser_service_not_ready")
    return service


@router.get("/status")
def get_browser_status(request: Request):
    return _service(request).get_status()


@router.get("/user-config")
def get_browser_user_config(request: Request):
    return _service(request).get_user_config()


@router.post("/user-config")
def set_browser_user_config(payload: BrowserUserConfigPayload, request: Request):
    try:
        return _service(request).set_user_config(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/user-config/identity")
def refresh_browser_user_identity(payload: BrowserUserConfigPayload, request: Request):
    try:
        return _service(request).refresh_user_browser_identity(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/user-config/pick-executable")
def pick_browser_executable(request: Request):
    try:
        return _service(request).choose_browser_executable()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/launch")
def launch_browser(payload: BrowserLaunchPayload, request: Request):
    try:
        return _service(request).launch_browser(payload.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/disconnect")
def disconnect_browser(request: Request):
    try:
        return _service(request).disconnect_browser()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/profiles")
def list_browser_profiles(request: Request):
    service = _service(request)
    return {
        "success": True,
        "default_profile": service.profile_manager.config.default_profile,
        "profiles": service.list_profiles(),
    }


@router.post("/profiles")
def create_browser_profile(payload: BrowserProfilePayload, request: Request):
    try:
        return {"success": True, "profile": _service(request).create_profile(payload.model_dump())}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/install/status")
def get_install_status(request: Request):
    return {"success": True, "install": _service(request).get_install_status()}


@router.post("/install/detect")
def detect_install_status(request: Request):
    service = _service(request)
    return {"success": True, "install": service.refresh_install_detection()}


@router.post("/install/managed")
def install_managed_browser(request: Request):
    return {"success": True, "install": _service(request).install_managed_browser()}


@router.post("/install/cancel")
def cancel_install(request: Request):
    return {"success": True, "install": _service(request).cancel_install()}


@router.post("/install/remove")
def remove_managed_browser(request: Request):
    return {"success": True, "install": _service(request).remove_managed_browser()}


@router.post("/install/reinstall")
def reinstall_managed_browser(request: Request):
    return {"success": True, "install": _service(request).reinstall_managed_browser()}


@router.post("/profiles/{profile_id}/start")
def start_profile(profile_id: str, request: Request):
    try:
        status = _service(request).start_profile(profile_id)
        return {"success": True, "status": status}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/profiles/{profile_id}")
def update_browser_profile(profile_id: str, payload: BrowserProfilePayload, request: Request):
    try:
        return {"success": True, "profile": _service(request).update_profile(profile_id, payload.model_dump())}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/profiles/{profile_id}")
def delete_browser_profile(profile_id: str, request: Request):
    try:
        return _service(request).delete_profile(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/set-default")
def set_default_browser_profile(profile_id: str, request: Request):
    try:
        return _service(request).set_default_profile(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/stop")
def stop_profile(profile_id: str, request: Request):
    try:
        status = _service(request).stop_profile(profile_id)
        return {"success": True, "status": status}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/diagnose")
def diagnose_profile(profile_id: str, request: Request):
    try:
        status = _service(request).diagnose_profile(profile_id)
        return {"success": True, "status": status}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/reconnect")
def reconnect_profile(profile_id: str, request: Request):
    try:
        status = _service(request).reconnect_profile(profile_id)
        return {"success": True, "status": status}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/reset")
def reset_profile(profile_id: str, request: Request):
    try:
        return {"success": True, "status": _service(request).reset_profile(profile_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/profiles/{profile_id}/tabs")
def list_profile_tabs(profile_id: str, request: Request):
    try:
        return _service(request).list_profile_tabs(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/tabs/open")
def open_profile_tab(profile_id: str, payload: BrowserTabOpenPayload, request: Request):
    try:
        return _service(request).open_profile_tab(profile_id, payload.url)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/tabs/select")
def select_profile_tab(profile_id: str, payload: BrowserTargetPayload, request: Request):
    try:
        return _service(request).select_profile_tab(profile_id, payload.target_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/tabs/close")
def close_profile_tab(profile_id: str, payload: BrowserTargetPayload, request: Request):
    try:
        return _service(request).close_profile_tab(profile_id, payload.target_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/snapshot")
def snapshot_profile(profile_id: str, payload: BrowserTargetPayload, request: Request):
    try:
        return _service(request).snapshot_profile(profile_id, target_id=payload.target_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/screenshot")
def screenshot_profile(profile_id: str, payload: BrowserScreenshotPayload, request: Request):
    try:
        return _service(request).screenshot_profile(
            profile_id,
            target_id=payload.target_id,
            full_page=payload.full_page,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/profiles/{profile_id}/act")
def act_profile(profile_id: str, payload: BrowserActPayload, request: Request):
    try:
        return _service(request).act_profile(
            profile_id,
            target_id=payload.target_id,
            kind=payload.kind,
            selector=payload.selector,
            value=payload.value,
            expression=payload.expression,
            url=payload.url,
            key=payload.key,
            file_path=payload.file_path,
            timeout_ms=payload.timeout_ms,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/session-binding")
def get_session_binding(request: Request):
    return _service(request).get_session_binding()


@router.post("/session-binding")
def set_session_binding(payload: SessionBindingPayload, request: Request):
    return _service(request).set_session_binding(payload.model_dump())
