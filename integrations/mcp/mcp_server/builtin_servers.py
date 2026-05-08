# -*- coding: utf-8 -*-
"""Built-in local MCP server implementations backed by existing tool logic."""

from __future__ import annotations

from typing import List

from integrations.mcp.schema import MCPServerManifest
from tools.local.alarm_tool import AlarmTool
from tools.local.ask_human_tool import AskHumanTool
from tools.local.bash_tool import BashTool
from tools.local.browser_tools import (
    BrowserActTool,
    BrowserDiagnoseTool,
    BrowserInstallManagedTool,
    BrowserInstallReinstallTool,
    BrowserInstallRemoveTool,
    BrowserReconnectTool,
    BrowserScreenshotTool,
    BrowserSnapshotTool,
    BrowserStartTool,
    BrowserStatusTool,
    BrowserStopTool,
    BrowserTabsCloseTool,
    BrowserTabsOpenTool,
    BrowserTabsSelectTool,
    BrowserTabsTool,
)
from tools.local.cite_manager_tool import CiteManagerTool
from tools.local.edit_tool import EditTool
from tools.local.embed_multimodal_tool import EmbedMultimodalTool
from tools.local.embed_text_tool import EmbedTextTool
from tools.local.glob_tool import GlobTool
from tools.local.grep_tool import GrepTool
from tools.local.history_query_tool import WorkspaceHistoryQueryTool
from tools.local.image_generation_tool import ImageGenerationTool
from tools.local.plan_tool import PlanTool
from tools.local.quote_extract_tool import QuoteExtractTool
from tools.local.read_tool import ReadTool
from tools.local.report_template_tool import ReportTemplateTool
from tools.local.skill_init_tool import SkillInitTool
from tools.local.source_compare_tool import SourceCompareTool
from tools.local.speech_to_text_tool import SpeechToTextTool
from tools.local.sub_agent_tool import SubAgentTool
from tools.local.text_to_speech_tool import TextToSpeechTool
from tools.local.thinking_tool import ThinkingTool
from tools.local.time_tool import TimeTool
from tools.local.video_generation_tool import VideoGenerationTool
from tools.local.vision_understand_tool import VisionUnderstandTool
from tools.local.web_fetch_tool import WebFetchTool
from tools.local.web_search_tool import WebSearchTool
from tools.local.write_file_tool import WriteFileTool

from .base import BaseLocalMCPServer


class FilesystemMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="filesystem",
        name="Filesystem Tools",
        description="Local filesystem and shell tools.",
        tools=["bash", "read", "write_file", "glob", "grep", "edit"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            BashTool(target.workspace_root),
            ReadTool(target.workspace_root),
            WriteFileTool(target.workspace_root),
            GlobTool(target.workspace_root),
            GrepTool(target.workspace_root),
            EditTool(target.workspace_root),
        ]


class SystemMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="system",
        name="System Tools",
        description="Local time, reminders, and user input tools.",
        tools=["time", "alarm", "ask_human"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            TimeTool(),
            AlarmTool(target._handle_system_message),
            AskHumanTool(target.ask_human_manager),
        ]


class BrowserMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="browser",
        name="Browser Tools",
        description="Managed browser runtime controls and managed Chromium install fallback.",
        tools=[
            "browser_status",
            "browser_start",
            "browser_stop",
            "browser_diagnose",
            "browser_reconnect",
            "browser_tabs",
            "browser_tabs_open",
            "browser_tabs_select",
            "browser_tabs_close",
            "browser_snapshot",
            "browser_screenshot",
            "browser_act",
            "browser_install_managed",
            "browser_install_remove",
            "browser_install_reinstall",
        ],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            BrowserStatusTool(target),
            BrowserStartTool(target),
            BrowserStopTool(target),
            BrowserDiagnoseTool(target),
            BrowserReconnectTool(target),
            BrowserTabsTool(target),
            BrowserTabsOpenTool(target),
            BrowserTabsSelectTool(target),
            BrowserTabsCloseTool(target),
            BrowserSnapshotTool(target),
            BrowserScreenshotTool(target),
            BrowserActTool(target),
            BrowserInstallManagedTool(target),
            BrowserInstallRemoveTool(target),
            BrowserInstallReinstallTool(target),
        ]


class VisionModelsMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="vision_models",
        name="Vision Models",
        description="Vision understanding tools backed by typed model config.",
        required_model_types=["vision"],
        default_enabled=False,
        tools=["vision_understand"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [VisionUnderstandTool(getattr(target, "project_root", "") or getattr(target, "agent_root", ""))]


class GenerationModelsMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="generation_models",
        name="Generation Models",
        description="Image and video generation tools backed by typed model config.",
        required_model_types=["image_generation", "video_generation"],
        default_enabled=False,
        tools=["generate_image", "generate_video"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        project_root = getattr(target, "project_root", "") or getattr(target, "agent_root", "")
        return [
            ImageGenerationTool(project_root),
            VideoGenerationTool(project_root),
        ]


class SpeechModelsMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="speech_models",
        name="Speech Models",
        description="Speech recognition and speech synthesis tools backed by typed model config.",
        required_model_types=["speech_to_text", "text_to_speech"],
        default_enabled=False,
        tools=["speech_to_text", "text_to_speech"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        project_root = getattr(target, "project_root", "") or getattr(target, "agent_root", "")
        return [
            SpeechToTextTool(project_root),
            TextToSpeechTool(project_root),
        ]


class EmbeddingModelsMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="embedding_models",
        name="Embedding Models",
        description="Text and multimodal embedding tools backed by typed model config.",
        required_model_types=["text_embedding", "multimodal_embedding"],
        default_enabled=False,
        tools=["embed_text", "embed_multimodal"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        project_root = getattr(target, "project_root", "") or getattr(target, "agent_root", "")
        return [
            EmbedTextTool(project_root),
            EmbedMultimodalTool(project_root),
        ]


class ResearchMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="research",
        name="Research Tools",
        description="Local fetch, compare, citation, and report helpers.",
        tools=["web_fetch", "quote_extract", "source_compare", "report_template", "cite_manager"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            WebFetchTool(),
            QuoteExtractTool(),
            SourceCompareTool(),
            ReportTemplateTool(),
            CiteManagerTool(),
        ]


class BraveSearchMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="brave_search",
        name="Brave Search",
        description="Local Brave-backed web search tool.",
        requires_secrets=True,
        required_secrets=["BRAVE_API_KEY"],
        default_enabled=False,
        tools=["web_search"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [WebSearchTool()]


class SkillsMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="skills",
        name="Skills Tools",
        description="Skill loading and skill package management.",
        tools=["skill", "skill_init"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        skills_root = target.workspace_layout.skills_local_root
        return [
            target.skill_tool,
            SkillInitTool(skills_root),
        ]


class AgentMCPServer(BaseLocalMCPServer):
    manifest = MCPServerManifest(
        server_id="agent",
        name="Agent Helpers",
        description="Sub-agent orchestration and reasoning helpers.",
        tools=["sub_agent", "thinking", "query_workspace_history", "plan"],
    )

    def build_tools(self, target, built_tools: List[object]) -> List[object]:
        return [
            SubAgentTool(list(built_tools), target.skill_runtime),
            ThinkingTool(),
            WorkspaceHistoryQueryTool(target.workspace_layout.history_root),
            PlanTool(),
        ]
