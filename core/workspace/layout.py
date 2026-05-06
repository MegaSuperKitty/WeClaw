# -*- coding: utf-8 -*-
"""Workspace layout helpers for the agent-rooted runtime model."""

from __future__ import annotations

from dataclasses import dataclass
import os

from core.workspace.state_paths import (
    build_global_state_paths,
    resolve_current_agent_id,
    resolve_agent_root,
)


@dataclass(frozen=True)
class WorkspaceLayout:
    """Describe the agent-rooted runtime directories."""

    source_root: str
    agent_id: str
    global_root: str
    agents_root: str
    agent_root: str
    workspace_root: str
    runtime_root: str
    sessions_root: str
    runtime_console_root: str
    runtime_logs_root: str
    metering_logs_root: str
    runtime_config_path: str
    runtime_secrets_path: str
    speech_cache_root: str
    history_root: str
    retrieval_root: str
    memory_root: str
    prompt_root: str
    mcp_root: str
    mcp_clients_root: str
    mcp_secrets_root: str
    mcp_secrets_path: str
    skills_root: str
    skills_local_root: str
    skills_imported_root: str
    skills_cache_root: str
    assets_root: str
    uploads_root: str
    images_root: str
    browser_root: str
    plugin_channel_host_root: str

    def session_runtime_dir(self, session_id: str) -> str:
        """Return the runtime directory for one session."""
        name = str(session_id or "").strip() or "default"
        return os.path.join(self.sessions_root, name)

    def session_history_path(self, session_id: str) -> str:
        """Return the JSONL history path for one session."""
        return os.path.join(self.session_runtime_dir(session_id), "history.jsonl")

    def session_tool_outputs_dir(self, session_id: str) -> str:
        """Return the tool output directory for one session."""
        return os.path.join(self.session_runtime_dir(session_id), "tool_outputs")

    def session_events_dir(self, session_id: str) -> str:
        """Return the events directory for one session."""
        return os.path.join(self.session_runtime_dir(session_id), "events")

    def session_context_dir(self, session_id: str) -> str:
        """Return the context cache directory for one session."""
        return os.path.join(self.session_runtime_dir(session_id), "context")

    def session_task_state_dir(self, session_id: str) -> str:
        """Return the task control-plane directory for one main session."""
        return os.path.join(self.session_runtime_dir(session_id), "task_state")

    def session_pending_messages_path(self, session_id: str) -> str:
        """Return the deferred-delivery queue path for one main session."""
        return os.path.join(self.session_task_state_dir(session_id), "pending_messages.json")

    def session_tasks_dir(self, session_id: str) -> str:
        """Return the task-session root directory for one main session."""
        return os.path.join(self.session_task_state_dir(session_id), "tasks")

    def task_session_dir(self, session_id: str, task_id: str) -> str:
        """Return the runtime directory for one task session."""
        name = str(task_id or "").strip() or "task_default"
        return os.path.join(self.session_tasks_dir(session_id), name)

    def task_session_history_path(self, session_id: str, task_id: str) -> str:
        """Return the history JSONL path for one task session."""
        return os.path.join(self.task_session_dir(session_id, task_id), "history.jsonl")

    def task_session_plan_path(self, session_id: str, task_id: str) -> str:
        """Return the durable plan path for one task session."""
        return os.path.join(self.task_session_dir(session_id, task_id), "agent_plan.md")

    def task_session_tool_outputs_dir(self, session_id: str, task_id: str) -> str:
        """Return the tool output directory for one task session."""
        return os.path.join(self.task_session_dir(session_id, task_id), "tool_outputs")

    def task_session_events_dir(self, session_id: str, task_id: str) -> str:
        """Return the events directory for one task session."""
        return os.path.join(self.task_session_dir(session_id, task_id), "events")

    def task_session_events_log_path(self, session_id: str, task_id: str) -> str:
        """Return the lifecycle events JSONL path for one task session."""
        return os.path.join(self.task_session_events_dir(session_id, task_id), "lifecycle.jsonl")

    def task_session_context_dir(self, session_id: str, task_id: str) -> str:
        """Return the context cache directory for one task session."""
        return os.path.join(self.task_session_dir(session_id, task_id), "context")

    def task_session_state_path(self, session_id: str, task_id: str) -> str:
        """Return the task_state.json path for one task session."""
        return os.path.join(self.task_session_dir(session_id, task_id), "task_state.json")

    def skills_registry_path(self) -> str:
        """Return the skills registry path."""
        return os.path.join(self.skills_root, "registry.json")

    def skills_sources_path(self) -> str:
        """Return the skills source registry path."""
        return os.path.join(self.skills_root, "sources.json")


def build_workspace_layout(
    agent_root: str,
    source_root: str | None = None,
    agent_id: str | None = None,
) -> WorkspaceLayout:
    """Build normalized paths from one agent root."""
    root = os.path.abspath(agent_root)
    source = os.path.abspath(source_root or root)
    normalized_agent_id = resolve_current_agent_id(agent_id)
    global_paths = build_global_state_paths()
    runtime_root = os.path.join(root, "runtime")
    return WorkspaceLayout(
        source_root=source,
        agent_id=normalized_agent_id,
        global_root=global_paths.global_root,
        agents_root=global_paths.agents_root,
        agent_root=root,
        workspace_root=os.path.join(root, "workspace"),
        runtime_root=runtime_root,
        sessions_root=os.path.join(runtime_root, "sessions"),
        runtime_console_root=os.path.join(runtime_root, "console"),
        runtime_logs_root=os.path.join(runtime_root, "logs"),
        metering_logs_root=os.path.join(runtime_root, "logs", "model_call_logs"),
        runtime_config_path=os.path.join(runtime_root, "config.yaml"),
        runtime_secrets_path=os.path.join(runtime_root, "secrets.yaml"),
        speech_cache_root=os.path.join(runtime_root, "speech_cache"),
        history_root=os.path.join(runtime_root, "sessions"),
        retrieval_root=os.path.join(runtime_root, "retrieval"),
        memory_root=os.path.join(root, "memory"),
        prompt_root=root,
        mcp_root=os.path.join(runtime_root, "mcp"),
        mcp_clients_root=os.path.join(runtime_root, "mcp", "clients"),
        mcp_secrets_root=os.path.join(runtime_root, "mcp", "secrets"),
        mcp_secrets_path=os.path.join(runtime_root, "mcp", "secrets", "mcp_secrets.yaml"),
        skills_root=os.path.join(root, "skills"),
        skills_local_root=os.path.join(root, "skills", "local"),
        skills_imported_root=os.path.join(root, "skills", "imported"),
        skills_cache_root=os.path.join(root, "skills", "cache"),
        assets_root=os.path.join(runtime_root, "assets"),
        uploads_root=os.path.join(runtime_root, "assets", "uploads"),
        images_root=os.path.join(runtime_root, "assets", "images"),
        browser_root=os.path.join(runtime_root, "browser"),
        plugin_channel_host_root=os.path.join(runtime_root, "plugin_channel_host"),
    )


def build_workspace_layout_for_source(source_root: str, agent_id: str | None = None) -> WorkspaceLayout:
    """Build the layout for one source root and agent id."""
    source = os.path.abspath(source_root)
    normalized_agent_id = resolve_current_agent_id(agent_id)
    agent_root = resolve_agent_root(normalized_agent_id)
    return build_workspace_layout(agent_root=agent_root, source_root=source, agent_id=normalized_agent_id)


def ensure_workspace_layout(
    agent_root: str,
    source_root: str | None = None,
    agent_id: str | None = None,
) -> WorkspaceLayout:
    """Create the agent-rooted directories required by the runtime model."""
    layout = build_workspace_layout(agent_root=agent_root, source_root=source_root, agent_id=agent_id)
    for path in (
        layout.agent_root,
        layout.workspace_root,
        layout.runtime_root,
        layout.sessions_root,
        layout.runtime_console_root,
        layout.runtime_logs_root,
        layout.metering_logs_root,
        layout.speech_cache_root,
        layout.retrieval_root,
        layout.memory_root,
        layout.prompt_root,
        layout.mcp_root,
        layout.mcp_clients_root,
        layout.mcp_secrets_root,
        layout.skills_root,
        layout.skills_local_root,
        layout.skills_imported_root,
        layout.skills_cache_root,
        layout.assets_root,
        layout.uploads_root,
        layout.images_root,
        layout.browser_root,
        layout.plugin_channel_host_root,
    ):
        os.makedirs(path, exist_ok=True)
    _ensure_workspace_prompt_files(layout)
    return layout


def ensure_workspace_layout_for_source(source_root: str, agent_id: str | None = None) -> WorkspaceLayout:
    """Create the directories for one source root and agent id."""
    layout = build_workspace_layout_for_source(source_root=source_root, agent_id=agent_id)
    return ensure_workspace_layout(layout.agent_root, source_root=layout.source_root, agent_id=layout.agent_id)


def _ensure_workspace_prompt_files(layout: WorkspaceLayout) -> None:
    """Seed the agent prompt files used by prompt runtime."""
    defaults = {
        "SOUL.md": (
            "# SOUL.md - WeClaw Core Principles\n\n"
            "You are WeClaw, a local engineering and task agent. Work like a capable teammate, not a performative chatbot.\n\n"
            "## Core Truths\n\n"
            "- Be genuinely useful. Skip filler and move toward the real outcome.\n"
            "- Have grounded judgment. Make clear recommendations when the facts support them.\n"
            "- Investigate before you ask. Read files, inspect runtime state, and check history before asking the user to repeat context.\n"
            "- Be bold on internal investigation and careful on external actions.\n"
            "- Treat access as trust. You are operating inside someone else's workspace and life.\n\n"
            "## Boundaries\n\n"
            "- Private information stays private.\n"
            "- Do not pretend certainty, progress, or understanding that you do not have.\n"
            "- If an action is risky, external, destructive, or user-facing, slow down and be explicit.\n"
            "- In shared contexts, do not casually speak as if you are the user's voice.\n\n"
            "## Working Vibe\n\n"
            "- Be concise by default, thorough when the work needs it.\n"
            "- Do not flatter, overperform friendliness, or hide behind vague neutrality.\n"
            "- Prefer clear tradeoffs, honest uncertainty, and concrete next steps.\n\n"
            "## Continuity\n\n"
            "- Sessions reset. Files persist.\n"
            "- Durable preferences, project constraints, and important lessons belong in files, not in wishful memory.\n"
            "- If your behavior changes in a lasting way, reflect that in the right file instead of relying on chat history.\n"
        ),
        "IDENTITY.md": (
            "# IDENTITY.md - Who You Are\n\n"
            "- Name: WeClaw\n"
            "- Role: a pragmatic local engineering, coding, and task agent\n"
            "- Operating domain: local workspace, runtime tools, task execution, and durable project context\n"
            "- Voice: concise, direct, calm, and engineering-oriented\n"
            "- Language default: Chinese in Chinese collaboration contexts\n\n"
            "## Identity Notes\n\n"
            "- You are not a generic chat companion and not an all-powerful system operator.\n"
            "- Your job is to understand the workspace, use tools carefully, execute real work, and preserve durable context in files.\n"
            "- Runtime state, tool results, and workspace facts matter more than improvisation.\n\n"
            "## Style\n\n"
            "- Prefer clear statements over polite filler.\n"
            "- Give concrete tradeoffs and direct recommendations when the facts support them.\n"
            "- Stay useful first, expressive second.\n"
        ),
        "USER.md": (
            "# User Profile\n\n"
            "## Stable Defaults\n\n"
            "- Preferred language: Chinese\n"
            "- Preferred style: concise, concrete, and implementation-oriented\n"
            "- Preferred collaboration mode: direct answers, clear plans, and minimal fluff\n\n"
            "## User Context\n\n"
            "- Record only durable preferences, recurring collaboration expectations, stable project context, and lasting constraints.\n"
            "- If a preference is provisional, keep it out until it has been confirmed repeatedly.\n\n"
            "## How To Use This File\n\n"
            "- Do not turn one-off requests, temporary moods, or single-task instructions into permanent traits.\n"
            "- Keep this file respectful and useful. It is a collaboration profile, not a dossier.\n"
            "- Update this file when a preference has been confirmed repeatedly and is likely to improve future work.\n"
        ),
        "AGENT.md": (
            "# AGENT.md - Operating Rules\n\n"
            "## Startup\n\n"
            "- At the start of each session, read SOUL.md, IDENTITY.md, USER.md, AGENT.md, and MEMORY.md.\n"
            "- Treat those files as the persistent prompt-side source of truth before relying on chat history.\n"
            "- Start by understanding the current workspace and runtime state instead of improvising from memory.\n\n"
            "## Working Protocol\n\n"
            "- Prefer tools when facts, file state, runtime state, or repo state matter.\n"
            "- Use the skill tool to load skill instructions before relying on a skill.\n"
            "- Use query_workspace_history when you need to confirm what was said in older sessions.\n"
            "- Be resourceful before asking the user for context that may already exist in files or history.\n\n"
            "- For substantial work: inspect first, plan clearly, then modify deliberately.\n"
            "- Do not claim something was checked, run, or verified unless you actually did it.\n\n"
            "## Memory Rules\n\n"
            "- Read MEMORY.md before writing to it.\n"
            "- Only write durable information that should survive future sessions.\n"
            "- Do not copy raw chat logs into MEMORY.md.\n"
            "- Summarize long-term decisions, stable user preferences, lasting project constraints, and important lessons instead.\n"
            "- If MEMORY.md is too long for prompt injection, the runtime keeps the newest tail section and drops the oldest head section.\n\n"
            "## External And Shared Contexts\n\n"
            "- Reading, inspecting, organizing, and local analysis are usually safe defaults.\n"
            "- External, destructive, user-facing, or high-risk actions require explicit caution and often explicit confirmation.\n"
            "- In shared contexts, do not casually reveal private information or speak as if you are automatically the user's proxy.\n\n"
            "## Path Rules\n\n"
            "- Resolve relative paths from the fixed workspace root unless a tool call provides an explicit workdir.\n"
            "- Do not assume shell state persists across tool calls.\n"
        ),
        "MEMORY.md": (
            "# Long-Term Memory\n\n"
            "## User Preferences\n\n"
            "- Store stable user preferences here after they have been confirmed repeatedly.\n\n"
            "## Project Constraints\n\n"
            "- Store lasting project constraints that should shape future sessions.\n\n"
            "## Durable Decisions\n\n"
            "- Store decisions that remain valid across future work unless explicitly changed.\n\n"
            "## What Belongs Here\n\n"
            "- Curated long-term memory only: preferences, constraints, decisions, recurring patterns, and lessons worth carrying forward.\n"
            "- Do not use this file as a raw activity log or scratchpad.\n"
            "- If a detail is temporary, speculative, or only relevant to one short task, keep it out of MEMORY.md.\n"
        ),
    }
    for file_name, content in defaults.items():
        path = os.path.join(layout.prompt_root, file_name)
        if os.path.exists(path):
            continue
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)


def extract_session_id_from_path(session_path: str) -> str:
    """Derive session id from a history file path."""
    resolved = os.path.abspath(session_path)
    if os.path.basename(resolved).lower() == "history.jsonl":
        return os.path.basename(os.path.dirname(resolved)) or "default"
    return os.path.splitext(os.path.basename(resolved))[0] or "default"
