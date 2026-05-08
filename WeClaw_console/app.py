# -*- coding: utf-8 -*-
"""WeClaw Console application entry."""

from __future__ import annotations

from contextlib import asynccontextmanager
import os
from pathlib import Path
import sys
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from gateway import GatewayService
from integrations.browser import BrowserService

# Ensure project root imports work when launching from WeClaw_console/.
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from WeClaw_console.api.routes_chat import router as chat_router
from WeClaw_console.api.routes_billing import router as billing_router
from WeClaw_console.api.routes_bridge import router as bridge_router
from WeClaw_console.api.routes_browser import router as browser_router
from WeClaw_console.api.routes_channels import router as channels_router
from WeClaw_console.api.routes_alarms import router as alarms_router
from WeClaw_console.api.routes_files import router as files_router
from WeClaw_console.api.routes_mcp import router as mcp_router
from WeClaw_console.api.routes_models import router as models_router
from WeClaw_console.api.routes_search import router as search_router
from WeClaw_console.api.routes_sessions import router as sessions_router
from WeClaw_console.api.routes_settings import router as settings_router
from WeClaw_console.api.routes_speech import router as speech_router
from WeClaw_console.api.routes_tasks import router as tasks_router
from WeClaw_console.api.routes_workspace_files import router as workspace_files_router
from WeClaw_console.api.routes_workspace_prompt import router as workspace_prompt_router
from WeClaw_console.api.routes_skills import router as skills_router
from WeClaw_console.core.bot_runtime import BotRuntime
from WeClaw_console.core.channel_config_store import ChannelConfigStore
from WeClaw_console.core.channel_runtime import ChannelRuntimeManager
from WeClaw_console.core.channel_service import ChannelService
from WeClaw_console.core.channel_specs import default_channel_specs
from WeClaw_console.core.model_config import ModelConfigManager
from WeClaw_console.core.runtime_config_store import RuntimeConfigStore
from WeClaw_console.core.speech_transcriber import LocalSpeechTranscriber
from WeClaw_console.core.skills_catalog import SkillsCatalog
from WeClaw_console.sched.alarm_engine import AlarmEngine
from integrations.metering import get_default_engine
from integrations.retrieval.engine import RetrievalEngine
from core.workspace.layout import ensure_workspace_layout_for_source
from core.workspace.state_paths import resolve_current_agent_id


def _resolve_runtime_layout():
    return ensure_workspace_layout_for_source(str(PROJECT_ROOT), agent_id=resolve_current_agent_id())


def _resolve_runtime_secrets_path() -> Path:
    return Path(_resolve_runtime_layout().runtime_secrets_path).resolve()


def _resolve_runtime_config_path() -> Path:
    return Path(_resolve_runtime_layout().runtime_config_path).resolve()


def _load_runtime_secrets(path: Path) -> Dict[str, str]:
    if not path.is_file():
        return {}
    try:
        import yaml

        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            return {}
        out: Dict[str, str] = {}
        for key, value in data.items():
            if value is None:
                continue
            text = str(value).strip()
            if text:
                out[str(key)] = text
        return out
    except Exception:
        return {}


def _apply_runtime_secrets_to_env() -> None:
    secrets = _load_runtime_secrets(_resolve_runtime_secrets_path())
    # Keep behavior aligned with CLI/QQ entries: env wins, local file is fallback.
    keys = [
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "LLM_MODEL",
        "LLM_PROVIDER",
        "LLM_PROFILE_ID",
        "BOTPY_APPID",
        "BOTPY_SECRET",
        "DISCORD_BOT_TOKEN",
        "DISCORD_APP_ID",
        "DISCORD_GUILD_ID",
        "DISCORD_HTTP_PROXY",
        "DISCORD_HTTP_PROXY_AUTH",
        "LLM_MAX_TOKENS",
        "LLM_TIMEOUT",
        "LLM_TEMPERATURE",
        "LLM_TOP_P",
        "RETRIEVAL_EMBED_PROVIDER",
        "RETRIEVAL_EMBED_MODEL",
        "RETRIEVAL_EMBED_DEVICE",
        "RETRIEVAL_EMBED_BATCH_SIZE",
        "RETRIEVAL_EMBED_NORMALIZE",
        "RETRIEVAL_CHUNK_TARGET_TOKENS",
        "RETRIEVAL_CHUNK_OVERLAP_TOKENS",
        "RETRIEVAL_CHARS_PER_TOKEN",
        "MODEL_CALL_LOG_DIR",
        "MODEL_METERING_ENABLED",
        "STT_MODEL",
        "STT_DEVICE",
        "STT_COMPUTE_TYPE",
        "STT_BEAM_SIZE",
        "STT_MAX_AUDIO_MB",
        "STT_VAD_FILTER",
        "STT_CACHE_DIR",
    ]
    for key in keys:
        if os.getenv(key, "").strip():
            continue
        value = secrets.get(key, "").strip()
        if value:
            os.environ[key] = value


_apply_runtime_secrets_to_env()


def _resolve_agent_root() -> str:
    return _resolve_runtime_layout().agent_root


def _resolve_history_dir() -> str:
    return _resolve_runtime_layout().history_root


def _resolve_retrieval_data_dir() -> str:
    return _resolve_runtime_layout().retrieval_root


def _resolve_console_data_dir() -> str:
    return _resolve_runtime_layout().runtime_console_root


def _resolve_metering_log_dir() -> str:
    env_dir = os.getenv("MODEL_CALL_LOG_DIR", "").strip()
    if env_dir:
        return str(Path(env_dir).resolve())
    return str(Path(_resolve_runtime_layout().metering_logs_root).resolve())


@asynccontextmanager
async def lifespan(app: FastAPI):
    history_dir = _resolve_history_dir()
    agent_id = resolve_current_agent_id()
    agent_root = _resolve_agent_root()
    retrieval_data_dir = _resolve_retrieval_data_dir()
    console_data_dir = _resolve_console_data_dir()
    runtime_secrets_path = _resolve_runtime_secrets_path()
    runtime_config_path = _resolve_runtime_config_path()

    model_manager = ModelConfigManager(str(runtime_secrets_path))
    model_manager.apply_active_profile()
    runtime_config_store = RuntimeConfigStore(str(runtime_config_path))
    runtime_config_store.ensure_exists()
    skills_catalog = SkillsCatalog(str(PROJECT_ROOT), agent_root)

    runtime = BotRuntime(
        history_dir=history_dir,
        agent_root=agent_root,
        agent_id=agent_id,
        max_rounds=20,
        max_steps=20,
        web_user_id="web:local",
        runtime_config_store=runtime_config_store,
    )
    gateway = GatewayService(runtime)
    runtime.bot.set_system_handler(
        lambda user_id, content: gateway.dispatch_background_prompt(
            user_id=user_id,
            session_name="",
            content=content,
            source="system",
            wait=False,
        )
    )

    data_dir = Path(console_data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    search_engine = RetrievalEngine(
        history_dir=history_dir,
        data_dir=retrieval_data_dir,
    )
    metering_log_dir = _resolve_metering_log_dir()
    metering_engine = get_default_engine(metering_log_dir)
    speech_cache_dir = os.getenv("STT_CACHE_DIR", "").strip() or str(Path(runtime.bot.workspace_layout.speech_cache_root).resolve())
    speech_transcriber = LocalSpeechTranscriber(speech_cache_dir)

    channel_store = ChannelConfigStore(data_path=str(data_dir / "channels.json"))
    channel_runtime = ChannelRuntimeManager(log_dir=str(data_dir / "channel_logs"))
    channel_service = ChannelService(
        project_root=str(PROJECT_ROOT),
        secrets_path=str(runtime_secrets_path),
        channel_log_dir=str(data_dir / "channel_logs"),
        config_store=channel_store,
        runtime_manager=channel_runtime,
        specs=default_channel_specs(),
    )

    alarm_engine = AlarmEngine(gateway=gateway, data_path=str(data_dir / "alarms.json"))
    runtime.bot.set_alarm_scheduler(alarm_engine.schedule_tool_alarm)
    browser_service = BrowserService(workspace_root=agent_root, source_root=str(PROJECT_ROOT))
    search_engine.start()

    alarm_engine.start()

    app.state.runtime = runtime
    app.state.gateway = gateway
    app.state.alarm_engine = alarm_engine
    app.state.model_manager = model_manager
    app.state.channel_service = channel_service
    app.state.browser_service = browser_service
    app.state.skills_catalog = skills_catalog
    app.state.search_engine = search_engine
    app.state.metering_engine = metering_engine
    app.state.speech_transcriber = speech_transcriber
    app.state.runtime_config_store = runtime_config_store

    try:
        yield
    finally:
        channel_service.shutdown()
        alarm_engine.stop()
        search_engine.stop()


WEB_DIR = HERE / "web"
ASSETS_DIR = WEB_DIR / "assets"
INDEX_HTML = WEB_DIR / "index.html"

def create_app() -> FastAPI:
    app = FastAPI(title="WeClaw Console", version="1.0.0", lifespan=lifespan)

    # Local-only service by default; CORS kept permissive for local tooling.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def no_cache_static(request: Request, call_next):
        response = await call_next(request)
        path = request.url.path or ""
        if path == "/" or path.startswith("/assets/") or path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    app.include_router(sessions_router)
    app.include_router(chat_router)
    app.include_router(bridge_router)
    app.include_router(browser_router)
    app.include_router(channels_router)
    app.include_router(files_router)
    app.include_router(alarms_router)
    app.include_router(skills_router)
    app.include_router(mcp_router)
    app.include_router(models_router)
    app.include_router(search_router)
    app.include_router(settings_router)
    app.include_router(billing_router)
    app.include_router(speech_router)
    app.include_router(tasks_router)
    app.include_router(workspace_files_router)
    app.include_router(workspace_prompt_router)

    @app.get("/api/v1/health")
    def health():
        return {"success": True, "service": "weclaw-console"}

    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

    @app.get("/")
    def web_root():
        if INDEX_HTML.exists():
            return FileResponse(str(INDEX_HTML))
        raise HTTPException(status_code=404, detail="index_not_found")

    @app.get("/{full_path:path}")
    def web_spa(full_path: str):
        # Let API routes pass through.
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="not_found")
        if INDEX_HTML.exists():
            return FileResponse(str(INDEX_HTML))
        raise HTTPException(status_code=404, detail="index_not_found")

    return app


def run_console(host: str = "127.0.0.1", port: int = 7788) -> None:
    import uvicorn

    uvicorn.run("WeClaw_console.app:app", host=host, port=int(port), reload=False)


app = create_app()


if __name__ == "__main__":
    run_console()
