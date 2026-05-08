# -*- coding: utf-8 -*-
"""API schemas for the WeClaw console."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    request_id: str = ""
    user_id: str = "web:local"
    session_name: str = ""
    content: str = Field(..., min_length=1)
    continue_mode: str = "in_place"
    source: str = "web"
    inject_uploaded_files: bool = True
    reply_language: str = ""


class CancelRequest(BaseModel):
    request_id: str


class HumanInputRequest(BaseModel):
    user_id: str
    content: str = Field(..., min_length=1)


class SessionNewRequest(BaseModel):
    user_id: str = "web:local"


class SessionSelectRequest(BaseModel):
    user_id: str
    session_name: str


class FileUploadMeta(BaseModel):
    user_id: str = "web:local"


class ModelProfileUpsertRequest(BaseModel):
    model_type: str = "text_generation"
    profile_id: str
    provider: str
    base_url: str = ""
    model: str = ""
    api_key: str
    max_tokens: Optional[int] = None
    timeout: Optional[float] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    clear_api_key: bool = False


class ModelProfileActivateRequest(BaseModel):
    model_type: str = "text_generation"
    profile_id: str


class ChannelUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    bot_prefix: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)


class BrowserProfileActionRequest(BaseModel):
    profile_id: str = ""


class WorkspacePromptSaveRequest(BaseModel):
    name: str
    content: str


class WorkspaceFileSaveRequest(BaseModel):
    path: str
    content: str


class RuntimeSettingsUiPayload(BaseModel):
    language: str = "zh"
    theme_mode: str = "light"


class RuntimeSettingsChatPayload(BaseModel):
    preferred_response_language: str = "zh"


class RuntimeSettingsRequest(BaseModel):
    ui: RuntimeSettingsUiPayload = Field(default_factory=RuntimeSettingsUiPayload)
    chat: RuntimeSettingsChatPayload = Field(default_factory=RuntimeSettingsChatPayload)
