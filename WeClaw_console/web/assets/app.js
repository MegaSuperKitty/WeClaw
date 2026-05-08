(() => {
  const LANG_KEY = "WeClaw_console_lang";

  const I18N = {
    zh: {
      brand_kicker: "WeClaw",
      brand_title: "WeClaw 控制台",
      brand_desc: "",
      nav_chat: "聊天",
      nav_search: "搜索任务",
      nav_channels: "频道",
      nav_browser: "浏览器",
      nav_workspace: "工作区",
      nav_alarms: "定时任务",
      nav_skills: "技能",
      nav_models: "模型",
      nav_billing: "模型计费",
      nav_group_resources: "资源",
      channels_title: "频道",
      channels_subtitle: "管理浏览器、CLI、QQ 与 Discord 连接渠道",
      browser_overview_title: "Browser Runtime",
      browser_user_title: "浏览器",
      browser_user_subtitle: "选择 WeClaw 使用哪一种浏览器方式",
      browser_profiles_title: "Profiles",
      browser_install_title: "Managed Chromium",
      browser_diagnostics_title: "诊断",
      browser_binding_title: "当前绑定",
      browser_advanced_summary: "高级设置",
      browser_launch_btn: "启动浏览器",
      browser_disconnect_btn: "断开连接",
      browser_mode_hint: "WeClaw 会在这套浏览器工作窗口里持续操作，直到你关闭它",
      browser_mode_existing_title: "使用我现有的浏览器",
      browser_mode_existing_desc: "复用你的登录环境，并启动一个由 WeClaw 控制的工作窗口",
      browser_mode_auto_title: "自动准备浏览器",
      browser_mode_auto_desc: "优先使用系统浏览器，没有时自动准备托管浏览器",
      browser_mode_fresh_title: "启动一个全新的浏览器",
      browser_mode_fresh_desc: "使用一个独立、干净的浏览器环境",
      browser_selected_mode: "当前模式",
      browser_launch_state: "浏览器状态",
      browser_launch_profile_source: "启动资料来源",
      browser_connected_state: "连接状态",
      browser_last_strategy: "上次启动策略",
      browser_last_connected_at: "上次连接",
      browser_last_used_browser: "当前浏览器",
      browser_mode_saved: "已记住你的配置，下次只需点击“启动浏览器”",
      browser_started_hint: "浏览器已启动，可以继续在当前 WeClaw 工作窗口中操作。",
      browser_needs_action: "需要你先处理浏览器设置后再重试",
      browser_launch_state_started: "已启动",
      browser_launch_state_starting: "启动中",
      browser_launch_state_failed: "启动失败",
      browser_launch_state_idle: "未启动",
      browser_launch_source_selected_browser_profile: "使用你选中的浏览器资料",
      browser_launch_source_dedicated_work_profile: "使用 WeClaw 的浏览器工作资料目录",
      browser_setup_title: "浏览器接入设置",
      browser_detected_title: "检测到的浏览器",
      browser_choose_program_btn: "选择浏览器程序",
      browser_refresh_identity_btn: "刷新浏览器身份",
      browser_identity_title: "当前浏览器身份",
      browser_identity_empty: "还没有选定浏览器程序。你可以先检测本机浏览器，或者选择一个浏览器程序。",
      browser_identity_family: "浏览器类型",
      browser_identity_data_dir: "资料目录",
      browser_identity_profile: "当前资料",
      browser_identity_profiles: "可用资料",
      browser_identity_detected: "系统会记住这套浏览器身份，后面直接启动 WeClaw 的浏览器工作窗口。",
      browser_pick_profile_btn: "使用这个资料",
      browser_identity_settings_title: "浏览器身份",
      browser_identity_program: "浏览器程序",
      browser_selected_browser: "已选浏览器",
      browser_selection_saved: "已选中，启动时会使用这套浏览器身份。",
      browser_launch_window_result: "窗口结果",
      browser_window_attached_existing_window: "已附着到当前浏览器窗口",
      browser_window_dedicated_window_requested: "已请求打开独立浏览器窗口",
      browser_window_dedicated_window_requested_with_merge_warning: "已请求独立窗口；如果该资料已在运行，浏览器也可能并入现有窗口",
      browser_port_label: "调试端口",
      browser_identity_save_btn: "保存高级设置",
      browser_detect_action_btn: "重新检测浏览器",
      browser_use_detected_btn: "使用这个浏览器",
      browser_detected_empty: "暂未检测到可直接使用的浏览器，你也可以选择一个浏览器程序。",
      workspace_title: "工作区",
      workspace_subtitle: "浏览工作区目录，仅支持预览 Markdown 文件。",
      workspace_tree_title: "工作区目录",
      workspace_tree_search_placeholder: "按文件名搜索...",
      workspace_preview_title: "预览",
      workspace_edit: "编辑",
      workspace_root_label: "工作区根目录",
      workspace_loading: "正在加载工作区...",
      workspace_empty: "当前工作区还没有可显示的文件。",
      workspace_open_hint: "从左侧目录选择一个 Markdown 文件开始预览。",
      workspace_saved: "文件已保存。",
      browser_detect_btn: "重新探测",
      browser_install_btn: "安装托管 Chromium",
      browser_install_reinstall_btn: "重装",
      browser_install_remove_btn: "移除",
      browser_install_cancel_btn: "取消安装",
      browser_start_btn: "启动",
      browser_stop_btn: "停止",
      browser_diagnose_btn: "诊断",
      browser_reconnect_btn: "重连",
      browser_tabs_btn: "标签页",
      browser_snapshot_btn: "快照",
      browser_screenshot_btn: "截图",
      browser_act_btn: "动作",
      browser_set_default_btn: "设为默认",
      browser_reset_btn: "重置",
      browser_open_tab_btn: "新开标签页",
      browser_default_profile: "默认 Profile",
      browser_workspace_root: "状态目录",
      browser_install_state: "安装状态",
      browser_no_profiles: "暂无 Browser Profile。",
      browser_system_browsers: "系统浏览器",
      browser_offer_install: "可安装托管 Chromium",
      browser_last_error: "最近错误",
      browser_running: "运行中",
      browser_stopped: "已停止",
      browser_idle: "空闲",
      browser_install_optional: "可选安装",
      browser_install_required: "建议安装",
      browser_install_not_needed: "系统浏览器可用",
      browser_no_diagnostics: "暂无诊断结果。",
      browser_existing_hint: "这是高级附着模式。先让浏览器自行暴露远程调试，再点重连。",
      browser_tabs_empty: "暂无可附着标签页。",
      channel_enabled_label: "启用",
      channel_prefix_label: "Bot 前缀",
      channel_prefix_placeholder: "可选前缀（例如 @bot）",
      sessions_title: "会话",
      new_web_session: "新建 Web 会话",
      filter_all: "全部",
      filter_qq: "QQ",
      filter_cli: "CLI",
      filter_web: "WEB",
      chat_subtitle_default: "请选择一个会话继续。",
      btn_cancel: "取消任务",
      btn_refresh: "刷新",
      btn_upload: "上传文件",
      btn_voice_start: "开始语音",
      btn_voice_stop: "停止录音",
      btn_send: "发送",
      chat_blocked_local_mcp: "本地MCP服务正在启动中，请稍候再发送...",
      chat_blocked_local_mcp_short: "本地MCP服务启动中",
      voice_idle: "待机",
      voice_recording: "录音中...",
      voice_transcribing: "转写中...",
      voice_unsupported: "浏览器不支持录音",
      voice_permission_denied: "麦克风权限被拒绝",
      voice_empty: "未采集到语音",
      voice_transcribed: "已转写",
      task_board_title: "任务看板",
      task_board_empty: "当前主会话下还没有任务。",
      task_board_count_summary: "活跃 {active} / 总计 {total}",
      btn_back_to_tasks: "返回任务列表",
      task_board_plan_title: "任务计划",
      task_board_activity_title: "最近动态",
      task_board_messages_title: "执行消息",
      task_board_progress_label: "最近进度",
      task_board_no_progress: "暂无进度摘要。",
      task_board_pending_label: "待处理问题",
      task_board_plan_empty: "当前还没有任务计划。",
      input_message_placeholder: "输入消息，Ctrl/Cmd + Enter 发送...",
      search_title: "搜索任务",
      search_subtitle: "在历史会话中检索，并跳转到最相关上下文。",
      search_placeholder: "输入关键词或问题",
      search_limit_placeholder: "条数",
      search_status_ready: "索引就绪",
      search_status_indexing: "索引中",
      search_status_last_index: "上次索引",
      search_status_chunks: "分片数",
      search_status_files: "文件数",
      search_status_embedder: "嵌入模型",
      search_no_results: "没有命中结果。",
      search_open_session: "打开会话",
      search_score: "相关度",
      btn_search: "搜索",
      btn_reindex: "重建索引",
      filter_all_channels: "全部频道",
      alarms_title: "定时任务",
      alarms_subtitle: "这里只能查看、暂停、恢复和取消已有任务。创建任务必须通过对话里的统一闹钟工具完成。",
      alarms_active_title: "当前任务",
      alarms_finished_title: "已结束任务",
      btn_reload: "刷新",
      cron_create_title: "新建任务",
      cron_expr_placeholder: "cron 表达式，例如 */5 * * * *",
      user_id_placeholder: "用户 ID",
      session_optional_placeholder: "会话名（可选）",
      prompt_placeholder: "提示词",
      btn_create: "创建",
      btn_save: "保存",
      btn_close: "关闭",
      btn_run_once: "立即执行",
      skills_title: "技能",
      skills_subtitle: "从本地工作目录 skills 读取。",
      skills_store_btn: "技能商店",
      skills_store_panel_title: "技能商店预览区",
      skills_store_panel_desc: "未来的 source、marketplace、安装与同步入口会统一放在这里。",
      skills_store_capability_1_title: "规划中的来源中心",
      skills_store_capability_1_desc: "后续会把本地、导入和远程来源收敛到同一个入口里。",
      skills_store_capability_2_title: "安装流程壳层",
      skills_store_capability_2_desc: "后续安装、更新和同步进度都会沿用这块页面内扩展区。",
      skills_store_capability_3_title: "Registry 优先",
      skills_store_capability_3_desc: "Store 动作会继续沿 registry 激活模型扩展，而不是再长出独立旁路。",
      skills_activated_title: "已启用技能",
      skills_inactivated_title: "未启用技能",
      skills_enable: "启用",
      skills_disable: "停用",
      skills_enabled: "已启用",
      skills_disabled: "已停用",
      models_title: "模型配置",
      models_subtitle: "管理 provider、密钥、profile，并切换当前工作模型。",
      providers_title: "提供商",
      profile_editor_title: "Profile 编辑器",
      profiles_title: "Profiles",
      runtime_title: "当前运行配置",
      field_profile_id: "Profile ID",
      field_provider: "提供商",
      field_base_url: "Base URL",
      field_model_name: "模型名",
      field_api_key: "API Key",
      field_max_tokens: "Max Tokens",
      field_timeout: "超时（秒）",
      field_temperature: "Temperature",
      field_top_p: "Top-p（核采样）",
      profile_id_placeholder: "profile_id",
      base_url_placeholder: "base_url",
      model_name_placeholder: "model",
      api_key_placeholder: "api_key（必填）",
      max_tokens_placeholder: "max_tokens（可选）",
      timeout_placeholder: "timeout 秒（可选）",
      temperature_placeholder: "temperature（可选）",
      top_p_placeholder: "top_p（可选）",
      clear_api_key: "清空已有 API Key",
      btn_new: "新建",
      btn_save_profile: "保存 Profile",
      btn_activate: "设为工作模型",
      btn_delete: "删除",
      btn_edit: "编辑",
      service_checking: "服务：检查中...",
      service_online: "服务：在线",
      service_offline: "服务：离线",
      no_channels: "暂无频道配置。",
      no_sessions: "暂无会话。",
      no_skills: "未检测到 skills。",
      no_profiles: "暂无 profile。",
      waiting_input: "等待你的输入...",
      human_input_submitted: "已提交",
      action_failed: "操作失败",
      upload_failed: "上传失败",
      init_failed: "初始化失败",
      notice_title_error: "操作提醒",
      notice_title_info: "界面提醒",
      notice_title_success: "结果已生成",
      notice_badge_error: "错误",
      notice_badge_info: "提示",
      notice_badge_success: "结果",
      stream_failed: "流式请求失败",
      btn_pause: "暂停",
      btn_resume: "恢复",
      btn_run: "执行",
      cron_expr_label: "表达式",
      target_label: "目标",
      status_label: "状态",
      paused_label: "暂停",
      next_run_label: "下次执行",
      last_run_label: "上次执行",
      last_result_label: "结果",
      hb_state_last_run: "上次执行",
      hb_state_last_status: "上次状态",
      hb_state_last_result: "上次结果",
      lang_toggle_button: "EN",
      lang_toggle_title: "Switch to English",
      payload_tool: "工具",
      payload_args: "参数",
      payload_state: "状态",
      payload_phase: "阶段",
      payload_error: "错误",
      event_connected: "已连接",
      event_run_started: "任务开始",
      event_assistant_reason: "调用理由",
      event_tool_before: "工具调用前",
      event_tool_after: "工具调用后",
      event_ask_human: "等待人工输入",
      event_status: "状态",
      event_assistant_delta: "回复流",
      event_run_done: "任务结束",
      event_cancel: "取消",
      event_human_input: "人工输入",
      event_file_uploaded: "文件上传",
      event_task_created: "任务已创建",
      event_task_updated: "任务已更新",
      event_task_status_changed: "任务状态变更",
      event_task_message_enqueued: "任务消息已入队",
      event_task_result_received: "任务结果",
      event_task_waiting_human: "任务需要你的输入",
      event_task_closed: "任务已关闭",
      event_subagent_result_received: "Subagent 结果",
      skill_path: "路径",
      provider_authorized: "已授权",
      provider_unauthorized: "未授权",
      profile_active: "工作中",
      profile_inactive: "未激活",
      runtime_provider: "Provider",
      runtime_model: "Model",
      runtime_base_url: "Base URL",
      runtime_key: "API Key",
      runtime_valid: "可用性",
      runtime_valid_yes: "可用",
      runtime_valid_no: "不可用",
      runtime_error: "错误",
      runtime_empty: "暂无运行配置。",
      select_profile_placeholder: "选择已有 profile",
      billing_title: "模型计费",
      billing_subtitle: "查看调用量、Token 消耗、失败率和单次调用详情。",
      billing_range_12h: "最近 12 小时",
      billing_range_24h: "最近 24 小时",
      billing_range_7d: "最近 7 天",
      billing_range_30d: "最近 30 天",
      billing_range_custom: "自定义",
      billing_bucket_auto: "自动粒度",
      billing_provider_placeholder: "provider",
      billing_model_placeholder: "model",
      billing_profile_placeholder: "profile_id",
      billing_keyword_placeholder: "关键词",
      billing_status_all: "全部",
      billing_status_success: "成功",
      billing_status_failed: "失败",
      billing_apply_filters: "应用筛选",
      billing_calls_total: "总调用",
      billing_success_calls: "成功",
      billing_failed_calls: "失败",
      billing_failure_rate: "失败率",
      billing_prompt_tokens: "输入 Token",
      billing_completion_tokens: "输出 Token",
      billing_tokens_total: "总 Token",
      billing_latency_p95: "P95 耗时",
      billing_chart_calls: "调用次数趋势",
      billing_chart_tokens: "Token 趋势",
      billing_call_list: "调用明细",
      billing_prev_page: "上一页",
      billing_next_page: "下一页",
      billing_detail_title: "调用详情",
      billing_no_data: "暂无数据",
      billing_status_box: "日志目录",
    },
    en: {
      brand_kicker: "WeClaw",
      brand_title: "WeClaw Console",
      brand_desc: "",
      nav_chat: "Chat",
      nav_search: "Search Tasks",
      nav_channels: "Channels",
      nav_browser: "Browser",
      nav_workspace: "Workspace",
      nav_alarms: "Alarms",
      nav_skills: "Skills",
      nav_models: "Models",
      nav_billing: "Billing",
      nav_group_resources: "Resources",
      channels_title: "Channels",
      channels_subtitle: "Manage browser, cli, qq and discord channel connections.",
      browser_overview_title: "Browser Runtime",
      browser_user_title: "Browser",
      browser_user_subtitle: "Choose how WeClaw should use a browser.",
      browser_profiles_title: "Profiles",
      browser_install_title: "Managed Chromium",
      browser_diagnostics_title: "Diagnostics",
      browser_binding_title: "Session Binding",
      browser_advanced_summary: "Advanced Settings",
      browser_launch_btn: "Launch Browser",
      browser_disconnect_btn: "Disconnect",
      browser_mode_hint: "WeClaw keeps working inside this browser work window until you close it.",
      browser_mode_existing_title: "Use My Existing Browser",
      browser_mode_existing_desc: "Reuse your login environment and launch a WeClaw-controlled work window.",
      browser_mode_auto_title: "Prepare a Browser for Me",
      browser_mode_auto_desc: "Use a system browser first, then fall back to a managed browser if needed.",
      browser_mode_fresh_title: "Start a Fresh Browser",
      browser_mode_fresh_desc: "Use a separate, clean browser environment.",
      browser_selected_mode: "Current Mode",
      browser_launch_state: "Browser State",
      browser_launch_profile_source: "Launch Profile Source",
      browser_connected_state: "Connection",
      browser_last_strategy: "Last Launch Strategy",
      browser_last_connected_at: "Last Connected",
      browser_last_used_browser: "Current Browser",
      browser_mode_saved: "Your choice is remembered. Next time you can just launch the browser.",
      browser_started_hint: "The browser has started. You can continue in the current WeClaw work window.",
      browser_needs_action: "You need to adjust browser settings before retrying.",
      browser_launch_state_started: "Started",
      browser_launch_state_starting: "Starting",
      browser_launch_state_failed: "Launch Failed",
      browser_launch_state_idle: "Not Started",
      browser_launch_source_selected_browser_profile: "Use the selected browser profile",
      browser_launch_source_dedicated_work_profile: "Use the WeClaw browser work profile directory",
      browser_setup_title: "Browser Access Setup",
      browser_detected_title: "Detected Browsers",
      browser_choose_program_btn: "Choose Browser Program",
      browser_refresh_identity_btn: "Refresh Browser Identity",
      browser_identity_title: "Current Browser Identity",
      browser_identity_empty: "No browser program has been selected yet. Detect a local browser or choose a browser program first.",
      browser_identity_family: "Browser Family",
      browser_identity_data_dir: "User Data Directory",
      browser_identity_profile: "Current Profile",
      browser_identity_profiles: "Available Profiles",
      browser_identity_detected: "WeClaw will remember this browser identity and relaunch it as a browser work window.",
      browser_pick_profile_btn: "Use This Profile",
      browser_identity_settings_title: "Browser Identity",
      browser_identity_program: "Browser Program",
      browser_selected_browser: "Selected Browser",
      browser_selection_saved: "Selected. This browser identity will be used when launching.",
      browser_launch_window_result: "Window Result",
      browser_window_attached_existing_window: "Attached to your current browser window",
      browser_window_dedicated_window_requested: "Requested a dedicated browser window",
      browser_window_dedicated_window_requested_with_merge_warning: "Requested a dedicated window; if this profile was already running, the browser may still merge into an existing window",
      browser_port_label: "Debug Port",
      browser_identity_save_btn: "Save Advanced Settings",
      browser_detect_action_btn: "Detect Browsers Again",
      browser_use_detected_btn: "Use This Browser",
      browser_detected_empty: "No browser was detected yet. You can still choose a browser program.",
      workspace_title: "Workspace",
      workspace_subtitle: "Browse the workspace tree. Only Markdown files are previewable.",
      workspace_tree_title: "Workspace Tree",
      workspace_tree_search_placeholder: "Search filenames...",
      workspace_preview_title: "Preview",
      workspace_edit: "Edit",
      workspace_root_label: "Workspace Root",
      workspace_loading: "Loading workspace...",
      workspace_empty: "No files are available in the current workspace.",
      workspace_open_hint: "Select a Markdown file from the left tree to preview it.",
      workspace_saved: "File saved.",
      browser_detect_btn: "Detect",
      browser_install_btn: "Install Managed Chromium",
      browser_install_reinstall_btn: "Reinstall",
      browser_install_remove_btn: "Remove",
      browser_install_cancel_btn: "Cancel Install",
      browser_start_btn: "Start",
      browser_stop_btn: "Stop",
      browser_diagnose_btn: "Diagnose",
      browser_reconnect_btn: "Reconnect",
      browser_tabs_btn: "Tabs",
      browser_snapshot_btn: "Snapshot",
      browser_screenshot_btn: "Screenshot",
      browser_act_btn: "Act",
      browser_set_default_btn: "Set Default",
      browser_reset_btn: "Reset",
      browser_open_tab_btn: "Open Tab",
      browser_default_profile: "Default Profile",
      browser_workspace_root: "State Root",
      browser_install_state: "Install State",
      browser_no_profiles: "No browser profiles found.",
      browser_system_browsers: "System Browsers",
      browser_offer_install: "Managed Install Available",
      browser_last_error: "Last Error",
      browser_running: "Running",
      browser_stopped: "Stopped",
      browser_idle: "Idle",
      browser_install_optional: "Optional install",
      browser_install_required: "Install recommended",
      browser_install_not_needed: "System browser available",
      browser_no_diagnostics: "No diagnostics yet.",
      browser_existing_hint: "This is the advanced attach path. Expose remote debugging from the browser first, then reconnect.",
      browser_tabs_empty: "No attachable tabs yet.",
      channel_enabled_label: "Enabled",
      channel_prefix_label: "Bot Prefix",
      channel_prefix_placeholder: "optional prefix, e.g. @bot",
      sessions_title: "Sessions",
      new_web_session: "New Web Session",
      filter_all: "All",
      filter_qq: "QQ",
      filter_cli: "CLI",
      filter_web: "WEB",
      chat_subtitle_default: "Select a session to continue.",
      btn_cancel: "Cancel",
      btn_refresh: "Refresh",
      btn_upload: "Upload",
      btn_voice_start: "Start Voice",
      btn_voice_stop: "Stop Recording",
      btn_send: "Send",
      chat_blocked_local_mcp: "Local MCP services are still starting. Please wait before sending.",
      chat_blocked_local_mcp_short: "Local MCP starting",
      voice_idle: "Idle",
      voice_recording: "Recording...",
      voice_transcribing: "Transcribing...",
      voice_unsupported: "Browser does not support recording",
      voice_permission_denied: "Microphone permission denied",
      voice_empty: "No audio captured",
      voice_transcribed: "Transcribed",
      task_board_title: "Task",
      task_board_empty: "No tasks under the current main session yet.",
      task_board_count_summary: "Active {active} / Total {total}",
      btn_back_to_tasks: "Back to Tasks",
      task_board_plan_title: "Plan",
      task_board_activity_title: "Recent Activity",
      task_board_messages_title: "Execution Messages",
      task_board_progress_label: "Latest Progress",
      task_board_no_progress: "No progress summary yet.",
      task_board_pending_label: "Pending Questions",
      task_board_plan_empty: "No task plan yet.",
      input_message_placeholder: "Type your message, Ctrl/Cmd + Enter to send...",
      search_title: "Search Tasks",
      search_subtitle: "Search historical sessions and jump to the best match.",
      search_placeholder: "Type query or question",
      search_limit_placeholder: "limit",
      search_status_ready: "Index ready",
      search_status_indexing: "Indexing",
      search_status_last_index: "Last indexed",
      search_status_chunks: "Chunks",
      search_status_files: "Files",
      search_status_embedder: "Embedder",
      search_no_results: "No relevant results.",
      search_open_session: "Open session",
      search_score: "Score",
      btn_search: "Search",
      btn_reindex: "Reindex",
      filter_all_channels: "All Channels",
      alarms_title: "Alarms",
      alarms_subtitle: "This page only lets you inspect, pause, resume, or cancel existing alarms. New alarms must be created by the unified alarm tool in chat.",
      alarms_active_title: "Active Alarms",
      alarms_finished_title: "Finished Alarms",
      btn_reload: "Reload",
      cron_create_title: "Create Job",
      cron_expr_placeholder: "cron expression, e.g. */5 * * * *",
      user_id_placeholder: "user_id",
      session_optional_placeholder: "session_name (optional)",
      prompt_placeholder: "Prompt",
      btn_create: "Create",
      btn_save: "Save",
      btn_close: "Close",
      btn_run_once: "Run Once",
      skills_title: "Skills",
      skills_subtitle: "Loaded from local workspace skills directory.",
      skills_store_btn: "Skills Store",
      skills_store_panel_title: "Skills Store Preview",
      skills_store_panel_desc: "Future source, marketplace, install and sync actions will live here.",
      skills_store_capability_1_title: "Planned Source Hub",
      skills_store_capability_1_desc: "Bring local, imported and future remote sources into one place.",
      skills_store_capability_2_title: "Install Shell",
      skills_store_capability_2_desc: "Future install, update and sync progress will reuse this in-page extension zone.",
      skills_store_capability_3_title: "Registry First",
      skills_store_capability_3_desc: "Store actions will extend the registry-driven activation model instead of growing side paths.",
      skills_activated_title: "Activated Skills",
      skills_inactivated_title: "Inactivated Skills",
      skills_enable: "Enable",
      skills_disable: "Disable",
      skills_enabled: "Enabled",
      skills_disabled: "Disabled",
      models_title: "Model Config",
      models_subtitle: "Manage providers, keys, profiles and active runtime model.",
      providers_title: "Providers",
      profile_editor_title: "Profile Editor",
      profiles_title: "Profiles",
      runtime_title: "Runtime Config",
      field_profile_id: "Profile ID",
      field_provider: "Provider",
      field_base_url: "Base URL",
      field_model_name: "Model",
      field_api_key: "API Key",
      field_max_tokens: "Max Tokens",
      field_timeout: "Timeout (s)",
      field_temperature: "Temperature",
      field_top_p: "Top-p",
      profile_id_placeholder: "profile_id",
      base_url_placeholder: "base_url",
      model_name_placeholder: "model",
      api_key_placeholder: "api_key (required)",
      max_tokens_placeholder: "max_tokens (optional)",
      timeout_placeholder: "timeout seconds (optional)",
      temperature_placeholder: "temperature (optional)",
      top_p_placeholder: "top_p (optional)",
      clear_api_key: "Clear existing API key",
      btn_new: "New",
      btn_save_profile: "Save Profile",
      btn_activate: "Activate",
      btn_delete: "Delete",
      btn_edit: "Edit",
      lang_toggle_button: "中文",
      lang_toggle_title: "切换到中文",
      service_checking: "Service: checking...",
      service_online: "Service: online",
      service_offline: "Service: offline",
      no_channels: "No channel config.",
      no_sessions: "No sessions.",
      no_skills: "No skills found.",
      no_profiles: "No profiles.",
      waiting_input: "Waiting for your input...",
      human_input_submitted: "submitted",
      action_failed: "Action failed",
      upload_failed: "Upload failed",
      init_failed: "Failed to initialize console",
      notice_title_error: "Action Notice",
      notice_title_info: "Notice",
      notice_title_success: "Result Ready",
      notice_badge_error: "Error",
      notice_badge_info: "Info",
      notice_badge_success: "Result",
      stream_failed: "stream_failed",
      btn_pause: "Pause",
      btn_resume: "Resume",
      btn_run: "Run",
      cron_expr_label: "expr",
      target_label: "target",
      status_label: "status",
      paused_label: "paused",
      next_run_label: "next_run_ts",
      last_run_label: "last_run_at",
      last_result_label: "last_result",
      hb_state_last_run: "last_run_at",
      hb_state_last_status: "last_status",
      hb_state_last_result: "last_result",
      payload_tool: "tool",
      payload_args: "args",
      payload_state: "state",
      payload_phase: "phase",
      payload_error: "error",
      event_connected: "connected",
      event_run_started: "run_started",
      event_assistant_reason: "assistant_reason",
      event_tool_before: "tool_before",
      event_tool_after: "tool_after",
      event_ask_human: "ask_human",
      event_status: "status",
      event_assistant_delta: "assistant_delta",
      event_run_done: "run_done",
      event_cancel: "cancel",
      event_human_input: "human_input",
      event_file_uploaded: "file_uploaded",
      event_task_created: "Task Created",
      event_task_updated: "Task Updated",
      event_task_status_changed: "Task Status Changed",
      event_task_message_enqueued: "Task Message Enqueued",
      event_task_result_received: "Task Result",
      event_task_waiting_human: "Task Needs Your Input",
      event_task_closed: "Task Closed",
      event_subagent_result_received: "Subagent Result",
      skill_path: "path",
      provider_authorized: "authorized",
      provider_unauthorized: "unauthorized",
      profile_active: "active",
      profile_inactive: "inactive",
      runtime_provider: "Provider",
      runtime_model: "Model",
      runtime_base_url: "Base URL",
      runtime_key: "API Key",
      runtime_valid: "Valid",
      runtime_valid_yes: "yes",
      runtime_valid_no: "no",
      runtime_error: "Error",
      runtime_empty: "No runtime info.",
      select_profile_placeholder: "Select existing profile",
      billing_title: "Model Billing",
      billing_subtitle: "Inspect call volume, token usage, failures and per-call details.",
      billing_range_12h: "Last 12h",
      billing_range_24h: "Last 24h",
      billing_range_7d: "Last 7d",
      billing_range_30d: "Last 30d",
      billing_range_custom: "Custom",
      billing_bucket_auto: "Auto Bucket",
      billing_provider_placeholder: "provider",
      billing_model_placeholder: "model",
      billing_profile_placeholder: "profile_id",
      billing_keyword_placeholder: "keyword",
      billing_status_all: "all",
      billing_status_success: "success",
      billing_status_failed: "failed",
      billing_apply_filters: "Apply",
      billing_calls_total: "Total Calls",
      billing_success_calls: "Success",
      billing_failed_calls: "Failed",
      billing_failure_rate: "Failure Rate",
      billing_prompt_tokens: "Prompt Tokens",
      billing_completion_tokens: "Completion Tokens",
      billing_tokens_total: "Total Tokens",
      billing_latency_p95: "P95 Latency",
      billing_chart_calls: "Call Volume",
      billing_chart_tokens: "Token Volume",
      billing_call_list: "Call Details",
      billing_prev_page: "Prev",
      billing_next_page: "Next",
      billing_detail_title: "Call Detail",
      billing_no_data: "No data",
      billing_status_box: "Log Dir",
    },
  };

  const MCP_I18N = {
    zh: {
      nav_mcp: "MCP",
      mcp_title: "\u004d\u0043\u0050 \u5ba2\u6237\u7aef",
      mcp_subtitle: "\u53d1\u73b0\u53ef\u7528\u7684\u672c\u5730\u670d\u52a1\uff0c\u5e76\u7ba1\u7406\u672c\u5730\u6216\u8fdc\u7a0b\u5ba2\u6237\u7aef\u3002",
      mcp_btn_new_local: "\u65b0\u5efa\u672c\u5730\u5ba2\u6237\u7aef",
      mcp_btn_new_remote: "\u65b0\u5efa\u8fdc\u7a0b\u5ba2\u6237\u7aef",
      mcp_discovered_title: "\u53ef\u7528\u7684\u672c\u5730\u670d\u52a1",
      mcp_discovered_subtitle: "\u8fd9\u91cc\u5c55\u793a\u68c0\u6d4b\u5230\u7684 server\uff0c\u4f46\u53ea\u6709\u5df2\u542f\u7528\u7684 client \u624d\u4f1a\u6210\u4e3a\u53ef\u7528\u5de5\u5177\u3002",
      mcp_clients_title: "\u5df2\u914d\u7f6e\u5ba2\u6237\u7aef",
      mcp_clients_subtitle: "\u53ef\u4ee5\u5728\u8fd0\u884c\u65f6\u521b\u5efa\u3001\u7f16\u8f91\u3001\u542f\u7528\u3001\u7981\u7528\u6216\u5220\u9664 MCP \u5ba2\u6237\u7aef\u3002",
      mcp_modal_create: "\u521b\u5efa MCP \u5ba2\u6237\u7aef",
      mcp_modal_edit: "\u7f16\u8f91 MCP \u5ba2\u6237\u7aef",
      mcp_field_client_id: "\u5ba2\u6237\u7aef ID",
      mcp_field_name: "\u540d\u79f0",
      mcp_field_description: "\u63cf\u8ff0",
      mcp_field_mode: "\u6a21\u5f0f",
      mcp_field_local_server: "\u672c\u5730\u670d\u52a1",
      mcp_field_local_command: "\u672c\u5730\u547d\u4ee4",
      mcp_field_local_args: "\u547d\u4ee4\u53c2\u6570",
      mcp_field_local_cwd: "\u5de5\u4f5c\u76ee\u5f55",
      mcp_field_remote_provider: "\u8fdc\u7a0b\u63d0\u4f9b\u65b9",
      mcp_field_endpoint: "\u63a5\u53e3\u5730\u5740",
      mcp_field_secret_refs: "\u5bc6\u94a5\u5f15\u7528",
      mcp_client_id_placeholder: "client_id",
      mcp_client_name_placeholder: "\u5c55\u793a\u540d\u79f0",
      mcp_client_description_placeholder: "\u53ef\u9009\u63cf\u8ff0",
      mcp_local_command_placeholder: "python",
      mcp_local_args_placeholder: "-m\\nexample_mcp_server",
      mcp_local_cwd_placeholder: "\u53ef\u9009\uff0c\u9ed8\u8ba4\u4e3a\u5f53\u524d\u5de5\u4f5c\u76ee\u5f55",
      mcp_endpoint_placeholder: "https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp",
      mcp_secret_refs_placeholder: "api_key:ZHIPU_API_KEY",
      mcp_mode_local: "\u672c\u5730",
      mcp_mode_remote: "\u8fdc\u7a0b",
      mcp_no_server_selected: "\u8bf7\u5148\u9009\u62e9\u8981\u914d\u7f6e\u7684\u672c\u5730 server\u3002",
      mcp_no_secret_needed: "\u8fd9\u4e2a\u672c\u5730 server \u4e0d\u9700\u8981 secret\u3002",
      mcp_required_secret_refs: "\u9700\u8981\u7684 secret \u5f15\u7528",
      mcp_remote_secret_help: "\u8fdc\u7a0b client \u901a\u5e38\u9700\u8981 secret \u5f15\u7528\uff0c\u4f8b\u5982 api_key:ZHIPU_API_KEY\u3002",
      mcp_error_client_id_required: "client_id \u4e0d\u80fd\u4e3a\u7a7a",
      mcp_error_server_id_required: "\u672c\u5730 client \u9700\u8981\u9009\u62e9 server_id \u6216\u586b\u5199\u672c\u5730\u547d\u4ee4",
      mcp_error_endpoint_required: "\u8fdc\u7a0b client \u5fc5\u987b\u586b\u5199 endpoint",
      mcp_summary_discovered: "\u53d1\u73b0\u7684\u672c\u5730 server",
      mcp_summary_configured: "\u5df2\u914d\u7f6e\u5ba2\u6237\u7aef",
      mcp_summary_enabled: "\u5df2\u542f\u7528\u5ba2\u6237\u7aef",
      mcp_summary_active_tools: "\u5f53\u524d\u542f\u7528\u5de5\u5177",
      mcp_empty_discovered: "\u672a\u53d1\u73b0\u672c\u5730 MCP server\u3002",
      mcp_empty_clients: "\u8fd8\u6ca1\u6709 MCP client \u914d\u7f6e\u3002",
      mcp_status_available_unconfigured: "\u53ef\u7528\u672a\u914d\u7f6e",
      mcp_status_configured_enabled: "\u5df2\u914d\u7f6e\u5e76\u542f\u7528",
      mcp_status_configured_disabled: "\u5df2\u914d\u7f6e\u4f46\u672a\u542f\u7528",
      mcp_status_enabled: "\u5df2\u542f\u7528",
      mcp_status_disabled: "\u5df2\u7981\u7528",
      mcp_status_ready: "\u5df2\u5c31\u7eea",
      mcp_status_starting: "\u542f\u52a8\u4e2d",
      mcp_status_configured: "\u5df2\u914d\u7f6e",
      mcp_status_error: "\u5f02\u5e38",
      mcp_label_server_id: "server_id",
      mcp_label_transport: "\u4f20\u8f93",
      mcp_label_secrets: "\u5bc6\u94a5",
      mcp_label_tools: "\u5de5\u5177",
      mcp_label_client_id: "client_id",
      mcp_label_mode: "\u6a21\u5f0f",
      mcp_label_source: "\u6765\u6e90",
      mcp_label_provider: "\u63d0\u4f9b\u65b9",
      mcp_label_active_tools: "\u5f53\u524d\u5de5\u5177",
      mcp_source_builtin: "\u5185\u7f6e",
      mcp_source_user: "\u7528\u6237",
      mcp_secret_required: "\u5fc5\u586b",
      mcp_secret_none: "\u65e0",
      mcp_btn_edit_config: "\u7f16\u8f91\u914d\u7f6e",
      mcp_btn_create_local: "\u521b\u5efa\u672c\u5730\u5ba2\u6237\u7aef",
      mcp_btn_edit: "\u7f16\u8f91",
      mcp_btn_enable: "\u542f\u7528",
      mcp_btn_disable: "\u7981\u7528",
      mcp_builtin_filesystem_name: "\u6587\u4ef6\u7cfb\u7edf\u5de5\u5177",
      mcp_builtin_filesystem_desc: "\u672c\u5730\u6587\u4ef6\u7cfb\u7edf\u548c\u547d\u4ee4\u884c\u5de5\u5177\u3002",
      mcp_builtin_system_name: "\u7cfb\u7edf\u5de5\u5177",
      mcp_builtin_system_desc: "\u672c\u5730\u65f6\u95f4\u3001\u63d0\u9192\u548c\u7528\u6237\u8f93\u5165\u5de5\u5177\u3002",
      mcp_builtin_research_name: "\u7814\u7a76\u5de5\u5177",
      mcp_builtin_research_desc: "\u672c\u5730\u6293\u53d6\u3001\u5f15\u7528\u3001\u5bf9\u6bd4\u548c\u62a5\u544a\u8f85\u52a9\u5de5\u5177\u3002",
      mcp_builtin_skills_name: "\u6280\u80fd\u5de5\u5177",
      mcp_builtin_skills_desc: "\u6280\u80fd\u52a0\u8f7d\u548c\u6280\u80fd\u5305\u7ba1\u7406\u5de5\u5177\u3002",
      mcp_builtin_agent_name: "Agent \u8f85\u52a9\u5de5\u5177",
      mcp_builtin_agent_desc: "\u5b50\u4ee3\u7406\u7f16\u6392\u548c\u63a8\u7406\u8f85\u52a9\u5de5\u5177\u3002",
      mcp_builtin_brave_search_name: "Brave \u641c\u7d22",
      mcp_builtin_brave_search_desc: "\u57fa\u4e8e Brave \u7684\u672c\u5730 Web \u641c\u7d22\u5de5\u5177\u3002",
      mcp_builtin_zhipu_web_search_name: "\u667a\u8c31 Web \u641c\u7d22",
      mcp_builtin_zhipu_web_search_desc: "\u901a\u8fc7 streamable HTTP MCP \u8c03\u7528\u667a\u8c31 Web \u641c\u7d22\u3002",
      // Settings
      nav_group_main: "\u4e3b\u8981",
      nav_group_system: "\u7cfb\u7edf",
      nav_group_settings: "\u8bbe\u7f6e",
      nav_settings: "\u8bbe\u7f6e",
      settings_title: "\u8bbe\u7f6e",
      settings_theme_mode: "\u4e3b\u9898\u6a21\u5f0f",
      settings_reply_language: "\u56de\u590d\u8bed\u8a00",
      settings_reply_language_zh: "\u4e2d\u6587",
      settings_reply_language_en: "English",
      settings_reply_language_hint: "\u5f53\u524d\u4ec5\u4f5c\u4e3a\u524d\u7aef\u8bbe\u7f6e\u4fdd\u5b58\uff0c\u6682\u4e0d\u63a5\u5165\u6a21\u578b\u56de\u590d\u94fe\u8def\u3002",
      settings_color_scheme: "\u914d\u8272\u65b9\u6848",
      settings_about: "\u5173\u4e8e",
      settings_about_text: "WeClaw Console - AI Agent \u7ba1\u7406\u754c\u9762",
      theme_light: "\u767d\u663c",
      theme_dark: "\u9ed1\u591c",
      theme_auto: "\u81ea\u52a8",
      color_blue: "\u84dd\u8272",
      color_green: "\u7eff\u8272",
      color_red: "\u7ea2\u8272",
      color_yellow: "\u9ec4\u8272",
      color_purple: "\u7d2b\u8272",
      service_online: "\u670d\u52a1\u5728\u7ebf",
    },
    en: {
      nav_mcp: "MCP",
      mcp_title: "MCP Clients",
      mcp_subtitle: "Discover available local servers and manage local or remote clients.",
      mcp_btn_new_local: "New Local Client",
      mcp_btn_new_remote: "New Remote Client",
      mcp_discovered_title: "Available Local Servers",
      mcp_discovered_subtitle: "Detected servers are shown here, but only enabled clients become active tools.",
      mcp_clients_title: "Configured Clients",
      mcp_clients_subtitle: "Create, edit, enable, disable, or remove MCP clients at runtime.",
      mcp_modal_create: "Create MCP Client",
      mcp_modal_edit: "Edit MCP Client",
      mcp_field_client_id: "Client ID",
      mcp_field_name: "Name",
      mcp_field_description: "Description",
      mcp_field_mode: "Mode",
      mcp_field_local_server: "Local Server",
      mcp_field_local_command: "Local Command",
      mcp_field_local_args: "Command Args",
      mcp_field_local_cwd: "Working Directory",
      mcp_field_remote_provider: "Remote Provider",
      mcp_field_endpoint: "Endpoint",
      mcp_field_secret_refs: "Secret Refs",
      mcp_client_id_placeholder: "client_id",
      mcp_client_name_placeholder: "display name",
      mcp_client_description_placeholder: "optional description",
      mcp_local_command_placeholder: "python",
      mcp_local_args_placeholder: "-m\\nexample_mcp_server",
      mcp_local_cwd_placeholder: "optional cwd path",
      mcp_endpoint_placeholder: "https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp",
      mcp_secret_refs_placeholder: "api_key:ZHIPU_API_KEY",
      mcp_mode_local: "Local",
      mcp_mode_remote: "Remote",
      mcp_no_server_selected: "Select a local server to configure this client.",
      mcp_no_secret_needed: "This local server does not require secrets.",
      mcp_required_secret_refs: "Required secret refs",
      mcp_remote_secret_help: "Remote clients usually require secret refs such as api_key:ZHIPU_API_KEY.",
      mcp_error_client_id_required: "client_id is required",
      mcp_error_server_id_required: "server_id or local command is required for local clients",
      mcp_error_endpoint_required: "endpoint is required for remote clients",
      mcp_summary_discovered: "Discovered local servers",
      mcp_summary_configured: "Configured clients",
      mcp_summary_enabled: "Enabled clients",
      mcp_summary_active_tools: "Active tools",
      mcp_empty_discovered: "No local MCP servers discovered.",
      mcp_empty_clients: "No MCP clients configured.",
      mcp_status_available_unconfigured: "available_unconfigured",
      mcp_status_configured_enabled: "configured_enabled",
      mcp_status_configured_disabled: "configured_disabled",
      mcp_status_enabled: "enabled",
      mcp_status_disabled: "disabled",
      mcp_status_ready: "ready",
      mcp_status_starting: "starting",
      mcp_status_configured: "configured",
      mcp_status_error: "error",
      mcp_label_server_id: "server_id",
      mcp_label_transport: "transport",
      mcp_label_secrets: "secrets",
      mcp_label_tools: "tools",
      mcp_label_client_id: "client_id",
      mcp_label_mode: "mode",
      mcp_label_source: "source",
      mcp_label_provider: "provider",
      mcp_label_active_tools: "active tools",
      mcp_source_builtin: "builtin",
      mcp_source_user: "user",
      mcp_secret_required: "required",
      mcp_secret_none: "none",
      mcp_btn_edit_config: "Edit Config",
      mcp_btn_create_local: "Create Local Client",
      mcp_btn_edit: "Edit",
      mcp_btn_enable: "Enable",
      mcp_btn_disable: "Disable",
      mcp_builtin_filesystem_name: "Filesystem Tools",
      mcp_builtin_filesystem_desc: "Local filesystem and shell tools.",
      mcp_builtin_system_name: "System Tools",
      mcp_builtin_system_desc: "Local time, reminders, and user input tools.",
      mcp_builtin_research_name: "Research Tools",
      mcp_builtin_research_desc: "Local fetch, compare, citation, and report helpers.",
      mcp_builtin_skills_name: "Skills Tools",
      mcp_builtin_skills_desc: "Skill loading and skill package management.",
      mcp_builtin_agent_name: "Agent Helpers",
      mcp_builtin_agent_desc: "Sub-agent orchestration and reasoning helpers.",
      mcp_builtin_brave_search_name: "Brave Search",
      mcp_builtin_brave_search_desc: "Local Brave-backed web search tool.",
      mcp_builtin_zhipu_web_search_name: "Zhipu Web Search",
      mcp_builtin_zhipu_web_search_desc: "Remote Zhipu web search via streamable HTTP MCP.",
      // Settings
      nav_group_main: "Main",
      nav_group_system: "System",
      nav_group_settings: "Settings",
      nav_settings: "Settings",
      settings_title: "Settings",
      settings_theme_mode: "Theme Mode",
      settings_reply_language: "Reply Language",
      settings_reply_language_zh: "Chinese",
      settings_reply_language_en: "English",
      settings_reply_language_hint: "Saved in frontend settings only for now.",
      settings_color_scheme: "Color Scheme",
      settings_about: "About",
      settings_about_text: "WeClaw Console - AI Agent Management Interface",
      theme_light: "Light",
      theme_dark: "Dark",
      theme_auto: "Auto",
      color_blue: "Blue",
      color_green: "Green",
      color_red: "Red",
      color_yellow: "Yellow",
      color_purple: "Purple",
      service_online: "Service Online",
    },
  };

  const EVENT_LABEL_KEYS = {
    connected: "event_connected",
    run_started: "event_run_started",
    assistant_thinking_delta: "event_assistant_reason",
    assistant_thinking_done: "event_assistant_reason",
    tool_before: "event_tool_before",
    tool_after: "event_tool_after",
    ask_human: "event_ask_human",
    status: "event_status",
    assistant_delta: "event_assistant_delta",
    run_done: "event_run_done",
    cancel: "event_cancel",
    human_input: "event_human_input",
    file_uploaded: "event_file_uploaded",
    task_created: "event_task_created",
    task_updated: "event_task_updated",
    task_status_changed: "event_task_status_changed",
    task_message_enqueued: "event_task_message_enqueued",
    task_result_received: "event_task_result_received",
    task_waiting_human: "event_task_waiting_human",
    task_closed: "event_task_closed",
    subagent_result_received: "event_subagent_result_received",
  };
  const TASK_EVENT_TYPES = new Set([
    "task_created",
    "task_updated",
    "task_status_changed",
    "task_message_enqueued",
    "task_result_received",
    "task_waiting_human",
    "task_closed",
  ]);
  const SUBAGENT_EVENT_TYPES = new Set(["subagent_result_received"]);

  const state = {
    view: "",
    hasExplicitView: false,
    lang: localStorage.getItem(LANG_KEY) === "en" ? "en" : "zh",
    themeMode: ["dark", "auto"].includes(localStorage.getItem("themeMode")) ? localStorage.getItem("themeMode") : "light",
    replyLanguage: localStorage.getItem("WeClaw_reply_language") === "en" ? "en" : "zh",
    sessions: [],
    filter: "all",
    selected: null,
    selectedSessionMsgSig: "",
    messages: [],
    events: [],
    tasks: [],
    selectedTaskId: "",
    selectedTaskDetail: null,
    selectedTaskMessages: [],
    taskBoardModalOpen: false,
    healthOnline: null,
    alarms: [],
    channels: [],
    channelEditor: null,
    skills: [],
    skillsStoreOpen: false,
    mcpDiscovered: [],
    mcpClients: [],
    mcpActiveTools: [],
    mcpEditor: null,
    mcpChatGuard: { blocked: false, reason: "", client_ids: [] },
    modelState: null,
    selectedModelType: "text_generation",
    modelProfileId: "",
    modelEditor: null,
    currentRequestId: "",
    waitingHuman: false,
    liveToolCardByStep: {},
    pendingThinkingByType: {},
    searchStatus: null,
    searchResults: [],
    searchQuery: "",
    searchLoading: false,
    browserStatus: null,
    browserProfiles: [],
    browserInstall: null,
    browserRecentCaptures: [],
    browserSessionBinding: null,
    browserUserConfig: null,
    workspaceRoot: "",
    workspaceTree: null,
    workspaceTreeSearch: "",
    workspaceExpandedPaths: {},
    workspaceSelectedPath: "",
    workspaceContent: "",
    workspaceContentKind: "markdown",
    workspaceEditable: false,
    workspaceDirty: false,
    workspaceLoading: false,
    workspaceMode: "preview",
    workspaceError: "",
    billingStatus: null,
    billingOverview: null,
    billingCalls: [],
    billingPage: 1,
    billingPageSize: 20,
    billingTotal: 0,
    billingFilters: {
      from_ts: 0,
      to_ts: 0,
      status: "all",
    },
    billingAutoRefreshTimer: null,
    billingAutoRefreshMs: 10000,
    sessionAutoRefreshTimer: null,
    sessionAutoRefreshMs: 1500,
    voiceRecording: false,
    voiceStatusKey: "voice_idle",
    voiceMediaRecorder: null,
    voiceStream: null,
    voiceChunks: [],
    imagePreview: {
      open: false,
      src: "",
      alt: "",
      title: "",
      meta: "",
    },
    noticeModal: {
      open: false,
      variant: "info",
      titleKey: "notice_title_info",
      title: "",
      body: "",
    },
  };

  const refs = {
    shellGrid: document.getElementById("shellGrid"),
    langToggleBtn: document.getElementById("langToggleBtn"),
    replyLanguageSelect: document.getElementById("replyLanguageSelect"),
    navItems: document.querySelectorAll(".nav-item[data-view]"),
    views: {
      chat: document.getElementById("view-chat"),
      search: document.getElementById("view-search"),
      channels: document.getElementById("view-channels"),
      browser: document.getElementById("view-browser"),
      workspace: document.getElementById("view-workspace"),
      alarms: document.getElementById("view-alarms"),
      skills: document.getElementById("view-skills"),
      mcp: document.getElementById("view-mcp"),
      models: document.getElementById("view-models"),
      billing: document.getElementById("view-billing"),
    },
    serviceHealth: document.getElementById("serviceHealth"),
    sessionFilters: document.querySelectorAll(".session-filter"),
    sessionList: document.getElementById("sessionList"),
    newSessionBtn: document.getElementById("newSessionBtn"),
    refreshSessionsBtn: document.getElementById("refreshSessionsBtn"),
    chatMessages: document.getElementById("chatMessages"),
    taskBoardCount: document.getElementById("taskBoardCount"),
    taskBoardEmpty: document.getElementById("taskBoardEmpty"),
    taskBoardList: document.getElementById("taskBoardList"),
    taskBoardModal: document.getElementById("taskBoardModal"),
    taskBoardModalCard: document.getElementById("taskBoardModalCard"),
    taskBoardModalTitle: document.getElementById("taskBoardModalTitle"),
    closeTaskBoardModalBtn: document.getElementById("closeTaskBoardModalBtn"),
    taskBoardDetail: document.getElementById("taskBoardDetail"),
    taskBoardSummary: document.getElementById("taskBoardSummary"),
    taskBoardPlan: document.getElementById("taskBoardPlan"),
    taskBoardMessages: document.getElementById("taskBoardMessages"),
    eventTimeline: document.getElementById("eventTimeline"),
    chatInput: document.getElementById("chatInput"),
    sendBtn: document.getElementById("sendBtn"),
    voiceInputBtn: document.getElementById("voiceInputBtn"),
    voiceInputStatus: document.getElementById("voiceInputStatus"),
    cancelBtn: document.getElementById("cancelBtn"),
    fileInput: document.getElementById("fileInput"),
    reloadChannelsBtn: document.getElementById("reloadChannelsBtn"),
    channelsGrid: document.getElementById("channelsGrid"),
    reloadBrowserBtn: document.getElementById("reloadBrowserBtn"),
    detectBrowserInstallBtn: document.getElementById("detectBrowserInstallBtn"),
    launchBrowserBtn: document.getElementById("launchBrowserBtn"),
    disconnectBrowserBtn: document.getElementById("disconnectBrowserBtn"),
    installManagedBrowserBtn: document.getElementById("installManagedBrowserBtn"),
    reinstallManagedBrowserBtn: document.getElementById("reinstallManagedBrowserBtn"),
    removeManagedBrowserBtn: document.getElementById("removeManagedBrowserBtn"),
    cancelManagedBrowserBtn: document.getElementById("cancelManagedBrowserBtn"),
    browserUserModesGrid: document.getElementById("browserUserModesGrid"),
    browserUserStatusPanel: document.getElementById("browserUserStatusPanel"),
    browserUserSetupPanel: document.getElementById("browserUserSetupPanel"),
    browserModeHint: document.getElementById("browserModeHint"),
    browserAdvancedDetails: document.getElementById("browserAdvancedDetails"),
    browserIdentityPanel: document.getElementById("browserIdentityPanel"),
    browserOverview: document.getElementById("browserOverview"),
    browserProfilesGrid: document.getElementById("browserProfilesGrid"),
    browserInstallPanel: document.getElementById("browserInstallPanel"),
    browserDiagnosticsPanel: document.getElementById("browserDiagnosticsPanel"),
    browserBindingPanel: document.getElementById("browserBindingPanel"),
    reloadDocsBtn: document.getElementById("reloadDocsBtn"),
    reloadWorkspaceTreeBtn: document.getElementById("reloadWorkspaceTreeBtn"),
    workspaceRootLabel: document.getElementById("workspaceRootLabel"),
    workspaceTreeSearch: document.getElementById("workspaceTreeSearch"),
    workspaceTreeList: document.getElementById("workspaceTreeList"),
    workspaceCurrentPath: document.getElementById("workspaceCurrentPath"),
    workspaceEditBtn: document.getElementById("workspaceEditBtn"),
    workspaceCancelBtn: document.getElementById("workspaceCancelBtn"),
    workspaceSaveBtn: document.getElementById("workspaceSaveBtn"),
    workspaceEditor: document.getElementById("workspaceEditor"),
    workspacePreview: document.getElementById("workspacePreview"),
    channelDrawer: document.getElementById("channelDrawer"),
    channelDrawerTitle: document.getElementById("channelDrawerTitle"),
    closeChannelDrawerBtn: document.getElementById("closeChannelDrawerBtn"),
    channelEnabledInput: document.getElementById("channelEnabledInput"),
    channelPrefixInput: document.getElementById("channelPrefixInput"),
    channelFields: document.getElementById("channelFields"),
    channelDrawerHint: document.getElementById("channelDrawerHint"),
    saveChannelBtn: document.getElementById("saveChannelBtn"),
    cancelChannelBtn: document.getElementById("cancelChannelBtn"),
    reloadAlarmsBtn: document.getElementById("reloadAlarmsBtn"),
    alarmsSummary: document.getElementById("alarmsSummary"),
    activeAlarmsList: document.getElementById("activeAlarmsList"),
    finishedAlarmsList: document.getElementById("finishedAlarmsList"),
  openSkillsStoreBtn: document.getElementById("openSkillsStoreBtn"),
  closeSkillsStoreBtn: document.getElementById("closeSkillsStoreBtn"),
  reloadSkillsBtn: document.getElementById("reloadSkillsBtn"),
  skillsContent: document.getElementById("skillsContent"),
  skillsStorePanel: document.getElementById("skillsStorePanel"),
  skillsEmptyState: document.getElementById("skillsEmptyState"),
  skillsPopulatedState: document.getElementById("skillsPopulatedState"),
  activatedSkillsGrid: document.getElementById("activatedSkillsGrid"),
  inactivatedSkillsGrid: document.getElementById("inactivatedSkillsGrid"),
    newLocalMcpBtn: document.getElementById("newLocalMcpBtn"),
    newRemoteMcpBtn: document.getElementById("newRemoteMcpBtn"),
    refreshMcpBtn: document.getElementById("refreshMcpBtn"),
    mcpSummary: document.getElementById("mcpSummary"),
    mcpDiscoveredGrid: document.getElementById("mcpDiscoveredGrid"),
    mcpClientsGrid: document.getElementById("mcpClientsGrid"),
    mcpModal: document.getElementById("mcpModal"),
    mcpModalTitle: document.getElementById("mcpModalTitle"),
    closeMcpModalBtn: document.getElementById("closeMcpModalBtn"),
    mcpClientIdInput: document.getElementById("mcpClientIdInput"),
    mcpClientNameInput: document.getElementById("mcpClientNameInput"),
    mcpClientDescriptionInput: document.getElementById("mcpClientDescriptionInput"),
    mcpClientEnabledInput: document.getElementById("mcpClientEnabledInput"),
    mcpClientModeSelect: document.getElementById("mcpClientModeSelect"),
    mcpClientServerField: document.getElementById("mcpClientServerField"),
    mcpClientServerSelect: document.getElementById("mcpClientServerSelect"),
    mcpClientCommandField: document.getElementById("mcpClientCommandField"),
    mcpClientCommandInput: document.getElementById("mcpClientCommandInput"),
    mcpClientArgsField: document.getElementById("mcpClientArgsField"),
    mcpClientArgsInput: document.getElementById("mcpClientArgsInput"),
    mcpClientCwdField: document.getElementById("mcpClientCwdField"),
    mcpClientCwdInput: document.getElementById("mcpClientCwdInput"),
    mcpClientEndpointField: document.getElementById("mcpClientEndpointField"),
    mcpClientEndpointInput: document.getElementById("mcpClientEndpointInput"),
    mcpSecretSlots: document.getElementById("mcpSecretSlots"),
    mcpToolsPanel: document.getElementById("mcpToolsPanel"),
    mcpToolsList: document.getElementById("mcpToolsList"),
    mcpSecretHelp: document.getElementById("mcpSecretHelp"),
    saveMcpClientBtn: document.getElementById("saveMcpClientBtn"),
    cancelMcpModalBtn: document.getElementById("cancelMcpModalBtn"),
    newModelBtn: document.getElementById("newModelBtn"),
    reloadModelsBtn: document.getElementById("reloadModelsBtn"),
    modelTypeGrid: document.getElementById("modelTypeGrid"),
    modelModal: document.getElementById("modelModal"),
    modelModalTitle: document.getElementById("modelModalTitle"),
    closeModelModalBtn: document.getElementById("closeModelModalBtn"),
    cancelModelModalBtn: document.getElementById("cancelModelModalBtn"),
    modelTypeSelect: document.getElementById("modelTypeSelect"),
    modelProfileIdInput: document.getElementById("modelProfileIdInput"),
    modelProviderSelect: document.getElementById("modelProviderSelect"),
    modelBaseUrlInput: document.getElementById("modelBaseUrlInput"),
    modelNameInput: document.getElementById("modelNameInput"),
    modelApiKeyInput: document.getElementById("modelApiKeyInput"),
    modelClearApiKeyInput: document.getElementById("modelClearApiKeyInput"),
    modelMaxTokensInput: document.getElementById("modelMaxTokensInput"),
    modelTimeoutInput: document.getElementById("modelTimeoutInput"),
    modelTemperatureInput: document.getElementById("modelTemperatureInput"),
    modelTopPInput: document.getElementById("modelTopPInput"),
    saveModelProfileBtn: document.getElementById("saveModelProfileBtn"),
    modelProfilesGrid: document.getElementById("modelProfilesGrid"),
    modelRuntimeState: document.getElementById("modelRuntimeState"),
    searchInput: document.getElementById("searchInput"),
    searchChannelFilter: document.getElementById("searchChannelFilter"),
    searchLimitInput: document.getElementById("searchLimitInput"),
    runSearchBtn: document.getElementById("runSearchBtn"),
    reindexSearchBtn: document.getElementById("reindexSearchBtn"),
    refreshSearchStatusBtn: document.getElementById("refreshSearchStatusBtn"),
    searchStatusBox: document.getElementById("searchStatusBox"),
    searchResults: document.getElementById("searchResults"),
    refreshBillingBtn: document.getElementById("refreshBillingBtn"),
    billingQuickRange: document.getElementById("billingQuickRange"),
    billingFromInput: document.getElementById("billingFromInput"),
    billingToInput: document.getElementById("billingToInput"),
    billingStatusSelect: document.getElementById("billingStatusSelect"),
    applyBillingFiltersBtn: document.getElementById("applyBillingFiltersBtn"),
    billingStatusBox: document.getElementById("billingStatusBox"),
    billingTotalCalls: document.getElementById("billingTotalCalls"),
    billingSuccessCalls: document.getElementById("billingSuccessCalls"),
    billingFailedCalls: document.getElementById("billingFailedCalls"),
    billingFailureRate: document.getElementById("billingFailureRate"),
    billingPromptTokens: document.getElementById("billingPromptTokens"),
    billingCompletionTokens: document.getElementById("billingCompletionTokens"),
    billingTokensTotal: document.getElementById("billingTokensTotal"),
    billingP95Latency: document.getElementById("billingP95Latency"),
    billingCallsTable: document.getElementById("billingCallsTable"),
    billingPrevBtn: document.getElementById("billingPrevBtn"),
    billingNextBtn: document.getElementById("billingNextBtn"),
    billingPageInfo: document.getElementById("billingPageInfo"),
    billingDetailModal: document.getElementById("billingDetailModal"),
    closeBillingDetailBtn: document.getElementById("closeBillingDetailBtn"),
    billingDetailPre: document.getElementById("billingDetailPre"),
    imagePreviewModal: document.getElementById("imagePreviewModal"),
    imagePreviewCard: document.getElementById("imagePreviewCard"),
    imagePreviewTitle: document.getElementById("imagePreviewTitle"),
    imagePreviewMeta: document.getElementById("imagePreviewMeta"),
    imagePreviewImg: document.getElementById("imagePreviewImg"),
    closeImagePreviewBtn: document.getElementById("closeImagePreviewBtn"),
    noticeModal: document.getElementById("noticeModal"),
    noticeModalCard: document.getElementById("noticeModalCard"),
    noticeModalBadge: document.getElementById("noticeModalBadge"),
    noticeModalTitle: document.getElementById("noticeModalTitle"),
    noticeModalBody: document.getElementById("noticeModalBody"),
    closeNoticeModalBtn: document.getElementById("closeNoticeModalBtn"),
    confirmNoticeModalBtn: document.getElementById("confirmNoticeModalBtn"),
  };

  const t = (key) => I18N[state.lang]?.[key] || MCP_I18N[state.lang]?.[key] || I18N.en?.[key] || MCP_I18N.en?.[key] || key;
  const zhen = (zh, en) => (state.lang === "zh" ? zh : en);
  const formatTaskBoardCount = (active, total) =>
    String(t("task_board_count_summary") || "")
      .replace("{active}", String(active))
      .replace("{total}", String(total));
  const taskToolResultTitle = (toolName) =>
    (
      {
        task_create: zhen("任务创建", "Task Create"),
        task_list: zhen("任务列表", "Task List"),
        task_query: zhen("任务查询", "Task Query"),
        task_update: zhen("任务更新", "Task Update"),
        task_finish: zhen("任务结束", "Task Finish"),
      }[String(toolName || "").trim()] || toolSummaryLabel(toolName)
    );
  const observationLabel = (kind) =>
    (
      {
        task: zhen("任务", "Task"),
        title: zhen("标题", "Title"),
        status: zhen("状态", "Status"),
        priority: zhen("优先级", "Priority"),
        kind: zhen("类型", "Kind"),
        worker_kind: zhen("类型", "Kind"),
        update: zhen("更新类型", "Update Kind"),
        update_kind: zhen("更新类型", "Update Kind"),
        finish: zhen("结束方式", "Finish Mode"),
        finish_mode: zhen("结束方式", "Finish Mode"),
        query: zhen("查询类型", "Query Kind"),
        query_kind: zhen("查询类型", "Query Kind"),
        source: zhen("回答来源", "Answer Source"),
        answer_source: zhen("回答来源", "Answer Source"),
        messageKind: zhen("消息类型", "Message Kind"),
        message_kind: zhen("消息类型", "Message Kind"),
        queued: zhen("队列消息", "Queued"),
        queued_count: zhen("队列消息", "Queued"),
        transition: zhen("状态变更", "Transition"),
        completed: zhen("已完成", "Completed"),
        remaining: zhen("未完成", "Remaining"),
        nextStep: zhen("下一步", "Next Step"),
        next_step: zhen("下一步", "Next Step"),
        taskSummary: zhen("任务摘要", "Task Summary"),
        task_summary: zhen("任务摘要", "Task Summary"),
        executionSummary: zhen("执行摘要", "Execution Summary"),
        execution_summary: zhen("执行摘要", "Execution Summary"),
        questionPrompt: zhen("请先回答这个问题", "Please answer this question"),
        question_prompt: zhen("请先回答这个问题", "Please answer this question"),
        runtimeEvent: zhen("运行时事件", "Runtime Event"),
        subagent: zhen("Subagent", "Subagent"),
      }[kind] || String(kind || "")
    );
  const observationValue = (kind, value) => {
    const clean = String(value || "").trim();
    if (!clean) return "";
    const maps = {
      status: {
        active: zhen("进行中", "Active"),
        waiting: zhen("等待中", "Waiting"),
        paused: zhen("已暂停", "Paused"),
        finished: zhen("已结束", "Finished"),
        failed: zhen("失败", "Failed"),
        completed: zhen("已完成", "Completed"),
        cancelled: zhen("已取消", "Cancelled"),
        running: zhen("运行中", "Running"),
        created: zhen("已创建", "Created"),
        finalizing: zhen("收尾中", "Finalizing"),
      },
      priority: {
        low: zhen("低", "Low"),
        normal: zhen("普通", "Normal"),
        high: zhen("高", "High"),
      },
      update: {
        append_requirement: zhen("追加要求", "Append Requirement"),
        append_note: zhen("追加备注", "Append Note"),
        resume: zhen("恢复执行", "Resume"),
      },
      finish: {
        complete: zhen("完成", "Complete"),
        cancel: zhen("取消", "Cancel"),
        force_stop: zhen("强制停止", "Force Stop"),
      },
      query: {
        progress: zhen("进度", "Progress"),
      },
      source: {
        snapshot_agent: zhen("快照代理", "Snapshot Agent"),
      },
      kind: {
        worker: zhen("执行型", "Worker"),
        explorer: zhen("探索型", "Explorer"),
      },
      messageKind: {
        task_create: zhen("任务创建", "Task Create"),
        task_update: zhen("任务更新", "Task Update"),
        task_human_reply: zhen("人工回复", "Human Reply"),
        task_result: zhen("任务结果", "Task Result"),
        task_waiting_human: zhen("任务需要你的输入", "Task Needs Your Input"),
        append_requirement: zhen("追加要求", "Append Requirement"),
        append_note: zhen("追加备注", "Append Note"),
        resume: zhen("恢复执行", "Resume"),
      },
    };
    const key = String(kind || "").trim();
    return (maps[key] && maps[key][clean]) || clean;
  };
  const observationTransition = (fromValue, toValue) =>
    `${observationValue("status", fromValue || "-")} -> ${observationValue("status", toValue || "-")}`;
  const NOTICE_VARIANTS = new Set(["error", "info", "success"]);
  const formatNoticeText = (value) => {
    if (value instanceof Error) return value.message || String(value);
    if (typeof value === "string") return value;
    if (value === undefined || value === null) return "";
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  };
  const syncNoticeModal = () => {
    if (!refs.noticeModal || !refs.noticeModalCard || !refs.noticeModalTitle || !refs.noticeModalBody || !refs.noticeModalBadge) return;
    const noticeState = state.noticeModal || {};
    const variant = NOTICE_VARIANTS.has(noticeState.variant) ? noticeState.variant : "info";
    refs.noticeModalCard.classList.remove("notice-modal--error", "notice-modal--info", "notice-modal--success");
    refs.noticeModalCard.classList.add(`notice-modal--${variant}`);
    refs.noticeModalTitle.textContent = noticeState.title || t(noticeState.titleKey || "notice_title_info");
    refs.noticeModalBody.textContent = formatNoticeText(noticeState.body);
    refs.noticeModalBadge.textContent = t(`notice_badge_${variant}`);
    refs.noticeModal.classList.toggle("hidden", !noticeState.open);
  };
  const showNoticeModal = ({ title = "", titleKey = "notice_title_info", body = "", variant = "info" } = {}) => {
    state.noticeModal = {
      open: true,
      variant: NOTICE_VARIANTS.has(variant) ? variant : "info",
      titleKey,
      title: String(title || ""),
      body: formatNoticeText(body),
    };
    syncNoticeModal();
  };
  const closeNoticeModal = () => {
    state.noticeModal = {
      open: false,
      variant: "info",
      titleKey: "notice_title_info",
      title: "",
      body: "",
    };
    syncNoticeModal();
  };
  const syncImagePreviewModal = () => {
    if (!refs.imagePreviewModal || !refs.imagePreviewImg || !refs.imagePreviewTitle || !refs.imagePreviewMeta) return;
    const preview = state.imagePreview || {};
    refs.imagePreviewModal.classList.toggle("hidden", !preview.open);
    refs.imagePreviewImg.src = preview.open ? String(preview.src || "") : "";
    refs.imagePreviewImg.alt = String(preview.alt || "");
    refs.imagePreviewTitle.textContent = preview.title || preview.alt || "Image Preview";
    refs.imagePreviewMeta.textContent = preview.meta || "";
  };
  const openImagePreview = ({ src = "", alt = "", title = "", meta = "" } = {}) => {
    if (!src) return;
    state.imagePreview = {
      open: true,
      src: String(src),
      alt: String(alt || ""),
      title: String(title || alt || ""),
      meta: String(meta || ""),
    };
    syncImagePreviewModal();
  };
  const closeImagePreview = () => {
    state.imagePreview = {
      open: false,
      src: "",
      alt: "",
      title: "",
      meta: "",
    };
    syncImagePreviewModal();
  };
  const syncTaskBoardModal = () => {
    if (!refs.taskBoardModal || !refs.taskBoardModalTitle) return;
    const task = state.selectedTaskDetail;
    const shouldOpen = Boolean(state.taskBoardModalOpen && state.selectedTaskId && task);
    refs.taskBoardModal.classList.toggle("hidden", !shouldOpen);
    refs.taskBoardModalTitle.textContent = shouldOpen
      ? String(task?.title || task?.task_id || t("task_board_title"))
      : t("task_board_title");
  };
  const openTaskBoardModal = async (taskId) => {
    const cleanTaskId = String(taskId || "").trim();
    if (!cleanTaskId) return;
    state.selectedTaskId = cleanTaskId;
    state.taskBoardModalOpen = true;
    await refreshSelectedTaskDetail(cleanTaskId);
    syncTaskBoardModal();
  };
  const closeTaskBoardModal = () => {
    state.taskBoardModalOpen = false;
    syncTaskBoardModal();
  };
  const showActionError = (err, prefixKey = "action_failed") => {
    const detail = formatNoticeText(err).trim();
    showNoticeModal({
      titleKey: "notice_title_error",
      body: detail ? `${t(prefixKey)}: ${detail}` : t(prefixKey),
      variant: "error",
    });
  };
  const providerDisplayName = (provider, fallback = "") => {
    const map = {
      openai: zhen("OpenAI", "OpenAI"),
      anthropic: zhen("Anthropic", "Anthropic"),
      dashscope: zhen("DashScope", "DashScope"),
      openai_custom: zhen("OpenAI \u517c\u5bb9\u7aef\u70b9", "OpenAI Compatible Endpoint"),
      anthropic_custom: zhen("Anthropic \u517c\u5bb9\u7aef\u70b9", "Anthropic Compatible Endpoint"),
    };
    return map[provider] || fallback || provider || "-";
  };
  const channelDisplayName = (name, fallback = "") => {
    const key = String(name || "").trim().toLowerCase();
    const map = {
      web: zhen("浏览器", "Browser"),
      cli: zhen("CLI", "CLI"),
      qq: zhen("QQ", "QQ"),
      discord: zhen("Discord", "Discord"),
    };
    return map[key] || fallback || key || "-";
  };
  const channelFieldLabel = (key) => {
    const map = {
      base_url: zhen("访问地址", "Base URL"),
      bind_host: zhen("绑定主机", "Bind Host"),
      port: zhen("端口", "Port"),
      command: zhen("启动命令", "Launch Command"),
      app_id: zhen("App ID", "App ID"),
      client_secret: zhen("Client Secret", "Client Secret"),
      bot_token: zhen("Bot Token", "Bot Token"),
      http_proxy: zhen("HTTP 代理", "HTTP Proxy"),
      http_proxy_auth: zhen("代理认证", "Proxy Auth"),
      application_id: zhen("Application ID", "Application ID"),
      guild_id: zhen("Guild ID", "Guild ID"),
    };
    return map[key] || key;
  };
  const channelRequiredHint = (keys) => {
    const labels = (Array.isArray(keys) ? keys : []).map((k) => channelFieldLabel(k));
    if (!labels.length) return "";
    return zhen(`缺少必填项：${labels.join("、")}`, `Missing required: ${labels.join(", ")}`);
  };
  const mcpBuiltinKey = (row) => {
    const key = String(row?.server_id || row?.client_id || "").trim();
    if (key) return key;
    return "";
  };
  const mcpDisplayName = (row) => {
    return String(row?.name || row?.client_id || row?.server_id || "server").trim() || "server";
  };
  const mcpDisplayDescription = (row) => {
      return String(row?.description || "").trim() || "-";
    };
  const mcpSourceText = (row) => {
    const source = String(row?.metadata?.source || "").trim().toLowerCase();
    if (source === "builtin") return t("mcp_source_builtin");
    if (source === "user") return t("mcp_source_user");
    return source || "-";
  };
  const mcpStatusText = (statusKey) => {
    const key = `mcp_status_${String(statusKey || "").trim()}`;
    const translated = t(key);
    return translated !== key ? translated : String(statusKey || "");
  };
  const mcpStatusToneClass = (statusKey) => {
    const value = String(statusKey || "").trim().toLowerCase();
    if (["ready", "connected", "running", "active", "healthy"].includes(value)) return "ok";
    if (["error", "failed", "unavailable", "stopped", "blocked"].includes(value)) return "error";
    return "untested";
  };
  const channelToneClass = (statusKey) => {
    if (statusKey === "enabled") return "ok";
    if (statusKey === "error") return "error";
    return "untested";
  };
  const localMcpChatGuardMessage = () => t("chat_blocked_local_mcp");
  const esc = (text) =>
    String(text || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  const escapeRegex = (text) => String(text || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const markdownToSafeHtml = (text) => {
    const raw = String(text || "");
    if (typeof window !== "undefined" && window.marked) {
      try {
        if (window.marked.setOptions) {
          window.marked.setOptions({ gfm: true, breaks: true });
        }
        const html = window.marked.parse(raw);
        if (window.DOMPurify && window.DOMPurify.sanitize) {
          return window.DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
        }
      } catch {
        // Fall through to escaped plain text below.
      }
    }
    return esc(raw).replaceAll("\n", "<br>");
  };

  const tryParseJson = (value) => {
    try {
      return JSON.parse(value);
    } catch {
      return null;
    }
  };

  const normalizeToolPayload = (raw) => {
    const text = String(raw || "").trim();
    if (!text) return "";

    let parsed = tryParseJson(text);
    if (parsed !== null && typeof parsed === "string") {
      const nested = tryParseJson(parsed);
      parsed = nested === null ? parsed : nested;
    }
    if (parsed === null) return text;

    if (typeof parsed === "string") return parsed;
    try {
      return JSON.stringify(parsed, null, 2);
    } catch {
      return String(parsed);
    }
  };

  const parseToolCalls = (value) => {
    if (Array.isArray(value)) return value;
    if (value && typeof value === "object") return [value];
    if (typeof value === "string") {
      const parsed = tryParseJson(value);
      if (Array.isArray(parsed)) return parsed;
      if (parsed && typeof parsed === "object") return [parsed];
    }
    return [];
  };

  const HIDDEN_CHAT_PREFIXES = [
    "[system message]",
    "[recap plan]",
    "[recap update]",
    "[recap reinject]",
    "[subtask]",
  ];

  const shouldHideConsoleMessage = (value) => {
    const text = String(value || "");
    if (!text.trim()) return false;
    const lowered = text.trimStart().toLowerCase();
    return HIDDEN_CHAT_PREFIXES.some((prefix) => lowered.startsWith(prefix));
  };
  const toolSummaryLabel = (toolName) => `${zhen("\u8c03\u7528\u5de5\u5177", "Tool Call")}: ${toolName || "tool"}`;

  async function api(path, options = {}) {
    const requestOptions = { ...(options || {}) };
    const method = String(requestOptions.method || "GET").trim().toUpperCase();
    requestOptions.cache = "no-store";
    const headers = { ...(requestOptions.headers || {}) };
    headers["Cache-Control"] = "no-cache";
    headers.Pragma = "no-cache";
    requestOptions.headers = headers;

    let finalPath = String(path || "");
    if (method === "GET") {
      const sep = finalPath.includes("?") ? "&" : "?";
      finalPath = `${finalPath}${sep}_ts=${Date.now()}`;
    }

    const response = await fetch(finalPath, requestOptions);
    if (!response.ok) {
      throw new Error((await response.text()) || `${response.status} ${response.statusText}`);
    }
    return response.headers.get("content-type")?.includes("application/json") ? response.json() : response.text();
  }

  function setView(view, options = {}) {
    if (options.explicit) {
      state.hasExplicitView = true;
    }
    state.view = view;
    refs.navItems.forEach((btn) => btn.classList.toggle("active", btn.dataset.view === view));
    Object.entries(refs.views).forEach(([name, el]) => el.classList.toggle("active", name === view));
    refs.shellGrid.classList.toggle("no-sessions", view !== "chat");

    // Update dynamic page title in brand area
    updatePageTitle(view);

    if (view === "chat") {
      startSessionAutoRefresh();
    } else {
      stopSessionAutoRefresh();
    }
    if (view === "billing") {
      startBillingAutoRefresh();
    } else {
      stopBillingAutoRefresh();
    }
  }

  // Page title mapping for dynamic brand subtitle
  const PAGE_TITLES = {
    chat: { zh: "聊天", en: "Chat" },
    search: { zh: "搜索任务", en: "Search" },
    channels: { zh: "频道", en: "Channels" },
    browser: { zh: "浏览器", en: "Browser" },
    workspace: { zh: "工作区", en: "Workspace" },
    alarms: { zh: "定时任务", en: "Alarms" },
    skills: { zh: "技能", en: "Skills" },
    mcp: { zh: "MCP 客户端", en: "MCP Clients" },
    models: { zh: "模型配置", en: "Models" },
    billing: { zh: "模型计费", en: "Model Billing" },
  };

  function updatePageTitle(view) {
    const titleEl = document.getElementById("pageTitle");
    if (!titleEl) return;

    const titleMap = PAGE_TITLES[view];
    if (titleMap) {
      const newTitle = state.lang === "zh" ? titleMap.zh : titleMap.en;
      // Fade out, change text, fade in
      titleEl.style.opacity = "0";
      titleEl.style.transform = "translateY(-4px)";
      setTimeout(() => {
        titleEl.textContent = newTitle;
        titleEl.style.opacity = "1";
        titleEl.style.transform = "translateY(0)";
      }, 150);
    }
  }

  async function loadViewDataOnEnter(view) {
    const name = String(view || "").trim();
    if (!name) return;
    if (name === "search") {
      await loadSearchStatus();
      return;
    }
    if (name === "channels") {
      await loadChannels();
      return;
    }
    if (name === "browser") {
      await loadBrowser();
      return;
    }
    if (name === "workspace") {
      await loadWorkspaceTree();
      return;
    }
    if (name === "alarms") {
      await loadAlarms();
      return;
    }
    if (name === "skills") {
      await loadSkills();
      return;
    }
    if (name === "mcp") {
      await loadMcp();
      return;
    }
    if (name === "models") {
      await loadModels();
      return;
    }
    if (name === "chat") {
      await refreshSelectedSessionMessages(true);
      return;
    }
    if (name === "billing") {
      // Entering billing should always force latest data and return to page 1.
      await reloadBilling(true);
    }
  }

  function applyI18n() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (key) el.setAttribute("placeholder", t(key));
    });
    refs.langToggleBtn.textContent = t("lang_toggle_button");
    refs.langToggleBtn.title = t("lang_toggle_title");
    renderHealth();
    refreshChatHeader();
    renderChannels();
    renderBrowser();
    renderWorkspaceBrowser();
    renderSearchStatus();
    renderSearchResults();
    renderMcp();
    renderBillingStatus();
    renderBillingOverview();
    renderBillingCalls();
    updateVoiceUi();
    updateChatInputGuard();
    renderTaskBoard();
    syncTaskBoardModal();
    syncNoticeModal();
    // Update current page title when language changes
    if (state.view) {
      const titleEl = document.getElementById("pageTitle");
      if (titleEl) {
        const titleMap = PAGE_TITLES[state.view];
        if (titleMap) {
          titleEl.textContent = state.lang === "zh" ? titleMap.zh : titleMap.en;
        }
      }
    }
    if (state.channelEditor && state.channelEditor.name) {
      openChannelDrawer(state.channelEditor.name);
    }
    if (state.mcpEditor) {
      if (refs.mcpModalTitle) {
        refs.mcpModalTitle.textContent = state.mcpEditor.editingId ? t("mcp_modal_edit") : t("mcp_modal_create");
      }
      refreshMcpEditorUi();
    }
  }

  function refreshChatHeader() {
    // Chat header info is now displayed in the brand area via updatePageTitle
    // This function is kept for compatibility but no longer updates DOM elements
  }

  function renderHealth() {
    refs.serviceHealth.textContent =
      state.healthOnline === null ? t("service_checking") : state.healthOnline ? t("service_online") : t("service_offline");
  }

  const normalizeThinkingPayload = (thinking = "", reasoningType = "general") => {
    const text = String(thinking || "").trim();
    if (!text) return "";
    return {
      content: text,
      reasoning_type: String(reasoningType || "general"),
    };
  };

  const createTextMessageRow = (
    role,
    content,
    streaming = false,
    allowEmpty = false,
    ts = "",
    attachments = [],
    thinking = "",
    reasoningType = "general"
  ) => {
    const text = String(content || "");
    const normalizedAttachments = Array.isArray(attachments) ? attachments.filter(Boolean) : [];
    if (!allowEmpty && !text.trim() && !normalizedAttachments.length) return null;
    if (text.trim() && shouldHideConsoleMessage(text)) return null;
    const normalizedRole = String(role || "assistant").trim().toLowerCase() || "assistant";
    return {
      role: normalizedRole === "tool" ? "system" : normalizedRole,
      kind: "text",
      content: text,
      streaming: Boolean(streaming),
      ts: String(ts || ""),
      attachments: normalizedAttachments,
      thinking: normalizeThinkingPayload(thinking, reasoningType),
    };
  };

  const createToolCardMessageRow = (
    toolName,
    toolCallId = "",
    inputText = "",
    outputText = "",
    streaming = false,
    thinking = "",
    reasoningType = "tool"
  ) => ({
    role: "system",
    kind: "tool_card",
    tool_name: String(toolName || "tool"),
    tool_call_id: String(toolCallId || ""),
    input_text: normalizeToolPayload(inputText),
    output_text: normalizeToolPayload(outputText),
    streaming: Boolean(streaming),
    thinking: normalizeThinkingPayload(thinking, reasoningType),
  });

  const createEventCardMessageRow = (
    eventSource,
    eventKind,
    title,
    content = "",
    ts = "",
    taskRef = {},
    subagentRef = {}
  ) => ({
    role: "system",
    kind: "event_card",
    event_source: String(eventSource || ""),
    event_kind: String(eventKind || ""),
    title: String(title || ""),
    content: String(content || ""),
    ts: String(ts || ""),
    task_ref: taskRef && typeof taskRef === "object" ? { ...taskRef } : {},
    subagent_ref: subagentRef && typeof subagentRef === "object" ? { ...subagentRef } : {},
  });

  const pushMessageRow = (rows, row, pendingToolCardsById) => {
    if (!row) return null;
    rows.push(row);
    if (row.kind === "tool_card" && row.tool_call_id) {
      pendingToolCardsById.set(row.tool_call_id, row);
    }
    return row;
  };

  const normalizeRenderMessageRow = (msg) => {
    const kind = String(msg?.kind || "").trim().toLowerCase();
    if (!kind) return null;
    if (kind === "text") {
      return createTextMessageRow(
        msg.role || "assistant",
        msg.content || "",
        Boolean(msg.streaming),
        Boolean(msg.streaming),
        msg.ts || "",
        msg.attachments || [],
        msg.thinking?.content || msg.thinking || "",
        msg.thinking?.reasoning_type || msg.reasoning_type || "general"
      );
    }
    if (kind === "tool_card") {
      return createToolCardMessageRow(
        msg.tool_name || msg.name || "tool",
        msg.tool_call_id || msg.toolCallId || "",
        msg.input_text || msg.input || "",
        msg.output_text || msg.output || msg.result || "",
        Boolean(msg.streaming),
        msg.thinking?.content || msg.thinking || "",
        msg.thinking?.reasoning_type || msg.reasoning_type || "tool"
      );
    }
    if (kind === "event_card") {
      return createEventCardMessageRow(
        msg.event_source || msg.eventSource || "",
        msg.event_kind || msg.eventKind || "",
        msg.title || "",
        msg.content || "",
        msg.ts || "",
        msg.task_ref || msg.taskRef || {},
        msg.subagent_ref || msg.subagentRef || {}
      );
    }
    if (kind === "thinking") {
      return null;
    }
    return null;
  };

  const coerceRenderMessageRow = (msg) => {
    if (!msg || typeof msg !== "object") return null;
    const renderRow = normalizeRenderMessageRow(msg);
    if (renderRow) return renderRow;
    const role = String(msg.role || "assistant").trim().toLowerCase() || "assistant";
    const attachments = role === "user" ? ((msg.user_turn_meta || {}).attachments || msg.attachments || []) : [];
    return createTextMessageRow(
      role,
      msg.content || "",
      Boolean(msg.streaming),
      Boolean(msg.streaming && role === "assistant"),
      msg.ts || "",
      attachments
    );
  };

  function normalizeMessages(messages) {
    const rows = Array.isArray(messages) ? messages : [];
    const normalized = [];
    const pendingToolCardsById = new Map();

    rows.forEach((msg) => {
      if (!msg || typeof msg !== "object") return;
      const kind = String(msg?.kind || "").trim().toLowerCase();
      if (kind === "thinking") return;

      const renderRow = normalizeRenderMessageRow(msg);
      if (renderRow) {
        pushMessageRow(normalized, renderRow, pendingToolCardsById);
        return;
      }

      const role = String(msg.role || "").trim().toLowerCase();

      if (role === "assistant") {
        const calls = parseToolCalls(msg.tool_calls ?? msg.toolCalls ?? msg.toolcalls);
        pushMessageRow(normalized, createTextMessageRow("assistant", msg.content || "", false, false, msg.ts || ""), pendingToolCardsById);

        const toolThinking = String(msg.reasoning_content || "").trim();
        let attachedToolThinking = false;
        calls.forEach((call) => {
          const fn = call && call.function ? call.function : call && call.func ? call.func : {};
          pushMessageRow(
            normalized,
            createToolCardMessageRow(
              fn.name || call.name || call.tool_name || "tool",
              call.id || call.tool_call_id || call.toolCallId || "",
              fn.arguments || "",
              "",
              false,
              !attachedToolThinking ? toolThinking : "",
              "tool"
            ),
            pendingToolCardsById
          );
          if (toolThinking && !attachedToolThinking) attachedToolThinking = true;
        });
        return;
      }

      const isToolLike = role === "tool" || Boolean(msg.tool_call_id || msg.toolCallId);
      if (isToolLike) {
        const callId = String(msg.tool_call_id || msg.toolCallId || "");
        const toolName = String(msg.name || msg.tool_name || "tool");
        const output = normalizeToolPayload(msg.content || msg.result || msg.output || "");

        if (callId && pendingToolCardsById.has(callId)) {
          const existing = pendingToolCardsById.get(callId);
          existing.output_text = output;
          if (!existing.tool_name || existing.tool_name === "tool") {
            existing.tool_name = toolName;
          }
        } else {
          pushMessageRow(normalized, createToolCardMessageRow(toolName, callId, "", output, false), pendingToolCardsById);
        }
        return;
      }

      if (role === "user" || role === "system") {
        pushMessageRow(
          normalized,
          createTextMessageRow(
            role,
            msg.content || "",
            false,
            false,
            msg.ts || "",
            role === "user" ? ((msg.user_turn_meta || {}).attachments || []) : []
          ),
          pendingToolCardsById
        );
      }
    });

    return normalized;
  }

  function buildMessageSignature(messages) {
    const rows = Array.isArray(messages) ? messages : [];
    if (!rows.length) return "0";
    const tail = rows.slice(-3).map((row) => {
      const role = String(row?.role || "");
      const kind = String(row?.kind || "");
      const content = String(row?.content || row?.output_text || row?.input_text || "");
      const thinking = String(row?.thinking?.content || row?.thinking || "");
      const key = String(row?.tool_call_id || row?.tool_name || "");
      const ts = String(row?.ts || "");
      const attachments = Array.isArray(row?.attachments) ? row.attachments.length : 0;
      return `${role}/${kind}/${key}/${attachments}/${ts}/${content.length}/${thinking.length}/${content.slice(-80)}/${thinking.slice(-80)}`;
    });
    return `${rows.length}|${tail.join("||")}`;
  }

  function renderSessions() {
    refs.sessionList.innerHTML = "";
    const filtered = (state.sessions || []).filter((row) => state.filter === "all" || row.channel_prefix === state.filter);
    if (!filtered.length) {
      refs.sessionList.innerHTML = `<div class="session-item">${esc(t("no_sessions"))}</div>`;
      return;
    }
    filtered.forEach((session) => {
      const active =
        state.selected &&
        state.selected.user_id === session.user_id &&
        state.selected.session_name === session.session_name;
      const badge = ["qq", "cli", "web"].includes(session.channel_prefix) ? session.channel_prefix : "unknown";
      const item = document.createElement("div");
      item.className = `session-item${active ? " active" : ""}`;
      item.innerHTML = `
        <div><span class="badge ${badge}">${esc(session.channel_prefix)}</span> ${esc(session.session_name)}</div>
        <div class="session-meta"><span>${esc(session.user_id)}</span><span>${esc(session.updated_at || "-")}</span></div>
      `;
      item.addEventListener("click", () => selectSession(session));
      refs.sessionList.appendChild(item);
    });
  }

  function updateChatInputGuard() {
    if (!refs.chatInput || !refs.sendBtn) return;
    const blocked = Boolean(state.mcpChatGuard && state.mcpChatGuard.blocked);
    refs.chatInput.disabled = blocked;
    refs.sendBtn.disabled = blocked;
    refs.chatInput.classList.toggle("blocked", blocked);
    if (blocked) {
      refs.chatInput.setAttribute("placeholder", localMcpChatGuardMessage());
      refs.chatInput.title = localMcpChatGuardMessage();
      return;
    }
    refs.chatInput.removeAttribute("title");
    const key = refs.chatInput.getAttribute("data-i18n-placeholder");
    refs.chatInput.setAttribute("placeholder", key ? t(key) : "");
  }

  function renderThinkingBlock(thinking) {
    const payload = thinking && typeof thinking === "object" ? thinking : normalizeThinkingPayload(thinking || "");
    if (!payload || !payload.content) return null;

    const block = document.createElement("div");
    block.className = "msg-thinking";

    const label = document.createElement("div");
    label.className = "thinking-label";
    label.textContent = "Thinking:";

    const content = document.createElement("div");
    content.className = "thinking-content";
    content.textContent = payload.content;

    block.appendChild(label);
    block.appendChild(content);
    return block;
  }

  function parseTaskToolOutput(msg) {
    const toolName = String(msg?.tool_name || "").trim();
    if (!toolName.startsWith("task_")) return null;
    const outputText = String(msg?.output_text || "").trim();
    if (!outputText.startsWith("{")) return null;
    try {
      const parsed = JSON.parse(outputText);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
      return { toolName, data: parsed };
    } catch {
      return null;
    }
  }

  function appendTaskToolStructuredOutput(body, msg) {
    const parsed = parseTaskToolOutput(msg);
    if (!parsed) return false;

    const { toolName, data } = parsed;
    const wrap = document.createElement("div");
    wrap.className = "task-tool-output";

    const title = document.createElement("div");
    title.className = "task-tool-output-title";
    title.textContent = taskToolResultTitle(toolName);
    wrap.appendChild(title);

    const summaryText = String(data.summary || data.answer || data.error || "").trim();
    if (summaryText) {
      const summary = document.createElement("div");
      summary.className = "task-tool-output-summary";
      summary.textContent = summaryText;
      wrap.appendChild(summary);
    }

    const facts = [];
    if (data.task_id) facts.push([observationLabel("task"), String(data.task_id)]);
    if (data.title) facts.push([observationLabel("title"), String(data.title)]);
    if (data.status) facts.push([observationLabel("status"), observationValue("status", data.status)]);
    if (data.priority) facts.push([observationLabel("priority"), observationValue("priority", data.priority)]);
    if (data.update_kind) facts.push([observationLabel("update"), observationValue("update", data.update_kind)]);
    if (data.finish_mode) facts.push([observationLabel("finish"), observationValue("finish", data.finish_mode)]);
    if (data.query_kind) facts.push([observationLabel("query"), observationValue("query", data.query_kind)]);
    if (data.answer_source) facts.push([observationLabel("source"), observationValue("source", data.answer_source)]);
    if (facts.length) {
      const grid = document.createElement("div");
      grid.className = "task-tool-output-facts";
      facts.forEach(([labelText, valueText]) => {
        const item = document.createElement("div");
        item.className = "task-tool-output-fact";
        const label = document.createElement("div");
        label.className = "task-tool-output-fact-label";
        label.textContent = labelText;
        const value = document.createElement("div");
        value.className = "task-tool-output-fact-value";
        value.textContent = valueText;
        item.appendChild(label);
        item.appendChild(value);
        grid.appendChild(item);
      });
      wrap.appendChild(grid);
    }

    if (Array.isArray(data.tasks) && data.tasks.length) {
      const list = document.createElement("div");
      list.className = "task-tool-output-task-list";
      data.tasks.forEach((task) => {
        if (!task || typeof task !== "object") return;
        const item = document.createElement("div");
        item.className = "task-tool-output-task-item";
        const head = document.createElement("div");
        head.className = "task-tool-output-task-head";
        head.textContent = `${String(task.title || task.task_id || observationLabel("task"))}`;
        item.appendChild(head);

        const metaParts = [];
        if (task.task_id) metaParts.push(String(task.task_id));
        if (task.status) metaParts.push(observationValue("status", task.status));
        if (task.priority) metaParts.push(observationValue("priority", task.priority));
        if (metaParts.length) {
          const meta = document.createElement("div");
          meta.className = "task-tool-output-task-meta";
          meta.textContent = metaParts.join("  ·  ");
          item.appendChild(meta);
        }
        if (task.latest_progress_summary) {
          const detail = document.createElement("div");
          detail.className = "task-tool-output-task-detail";
          detail.textContent = String(task.latest_progress_summary);
          item.appendChild(detail);
        }
        list.appendChild(item);
      });
      wrap.appendChild(list);
    }

    if (String(data.answer || "").trim()) {
      const answer = document.createElement("div");
      answer.className = "task-tool-output-answer";
      answer.textContent = String(data.answer);
      wrap.appendChild(answer);
    }

    body.appendChild(wrap);
    return true;
  }

  function renderToolCardMessage(msg) {
    const toolName = String(msg.tool_name || "tool");
    const details = document.createElement("details");
    details.className = "msg system tool-collapse";

    const summary = document.createElement("summary");
    summary.className = "tool-collapse-summary";
    summary.innerHTML = `
      <span class="tool-collapse-title">${esc(toolSummaryLabel(toolName))}</span>
      <span class="tool-collapse-arrow"></span>
    `;
    details.appendChild(summary);

    const body = document.createElement("div");
    body.className = "tool-collapse-body";
    const thinking = renderThinkingBlock(msg.thinking);
    if (thinking) body.appendChild(thinking);
    const hasStructuredTaskOutput = appendTaskToolStructuredOutput(body, msg);
    if (msg.input_text) {
      body.innerHTML += `
        <div class="tool-collapse-section">
          <div class="tool-collapse-label">${esc(zhen("\u8f93\u5165", "Input"))}</div>
          <div class="tool-scroll"><pre>${esc(msg.input_text)}</pre></div>
        </div>
      `;
    }
    if (msg.output_text) {
      const outputLabel = hasStructuredTaskOutput ? zhen("\u539f\u59cb\u8f93\u51fa", "Raw Output") : zhen("\u8f93\u51fa", "Output");
      body.innerHTML += `
        <div class="tool-collapse-section">
          <div class="tool-collapse-label">${esc(outputLabel)}</div>
          <div class="tool-scroll"><pre>${esc(msg.output_text)}</pre></div>
        </div>
      `;
    }
    details.appendChild(body);
    return details;
  }

  function renderEventCardMessage(msg) {
    const node = document.createElement("div");
    const source = String(msg.event_source || "runtime").trim().toLowerCase() || "runtime";
    const kind = String(msg.event_kind || "event").trim().toLowerCase() || "event";
    node.className = `msg system event-card event-source-${source} event-kind-${kind}`;
    if (kind === "task_waiting_human") node.classList.add("event-card-waiting-human");
    if (kind === "task_result_received") node.classList.add("event-card-task-result");
    if (kind === "subagent_result_received") node.classList.add("event-card-subagent-result");

    const header = document.createElement("div");
    header.className = "event-card-header";

    const badge = document.createElement("div");
    badge.className = "event-card-badge";
    badge.textContent = msg.title || observationLabel("runtimeEvent");
    header.appendChild(badge);

    const meta = document.createElement("div");
    meta.className = "event-card-meta";
    const metaItems = [];
    if (msg.task_ref?.task_id) metaItems.push(`${observationLabel("task")} · ${String(msg.task_ref.task_id)}`);
    if (msg.task_ref?.task_title) metaItems.push(`${observationLabel("title")} · ${String(msg.task_ref.task_title)}`);
    if (msg.task_ref?.status) metaItems.push(`${observationLabel("status")} · ${observationValue("status", msg.task_ref.status)}`);
    if (msg.subagent_ref?.subagent_id) metaItems.push(`${observationLabel("subagent")} · ${String(msg.subagent_ref.subagent_id)}`);
    if (msg.subagent_ref?.status) metaItems.push(`${observationLabel("status")} · ${observationValue("status", msg.subagent_ref.status)}`);
    if (msg.subagent_ref?.worker_kind) metaItems.push(`${observationLabel("kind")} · ${observationValue("kind", msg.subagent_ref.worker_kind)}`);
    if (metaItems.length) {
      meta.textContent = metaItems.join("  ");
      header.appendChild(meta);
    }

    node.appendChild(header);

    const body = document.createElement("div");
    body.className = "event-card-body";

    if (kind === "task_waiting_human" && String(msg.content || "").trim()) {
      const prompt = document.createElement("div");
      prompt.className = "event-card-question-label";
      prompt.textContent = observationLabel("questionPrompt");
      body.appendChild(prompt);

      const question = document.createElement("div");
      question.className = "event-card-question";
      question.textContent = msg.content;
      body.appendChild(question);
    } else if (kind === "task_result_received" && String(msg.content || "").trim()) {
      const summaryLabel = document.createElement("div");
      summaryLabel.className = "event-card-summary-label";
      summaryLabel.textContent = observationLabel("taskSummary");
      body.appendChild(summaryLabel);

      const summary = document.createElement("div");
      summary.className = "event-card-summary";
      summary.textContent = msg.content;
      body.appendChild(summary);
    } else if (kind === "subagent_result_received") {
      const result = msg.subagent_ref?.result && typeof msg.subagent_ref.result === "object" ? msg.subagent_ref.result : {};
      if (String(msg.content || "").trim()) {
        const summaryLabel = document.createElement("div");
        summaryLabel.className = "event-card-summary-label";
        summaryLabel.textContent = observationLabel("executionSummary");
        body.appendChild(summaryLabel);

        const summary = document.createElement("div");
        summary.className = "event-card-summary";
        summary.textContent = msg.content;
        body.appendChild(summary);
      }

      const sections = [
        { key: "completed_work", label: observationLabel("completed"), kind: "list" },
        { key: "remaining_work", label: observationLabel("remaining"), kind: "list" },
        { key: "next_step", label: observationLabel("nextStep"), kind: "text" },
      ];
      sections.forEach((section) => {
        const value = result?.[section.key];
        if (section.kind === "list") {
          const items = Array.isArray(value) ? value.filter((item) => String(item || "").trim()) : [];
          if (!items.length) return;
          const block = document.createElement("div");
          block.className = "event-card-detail-block";
          const label = document.createElement("div");
          label.className = "event-card-detail-label";
          label.textContent = section.label;
          const list = document.createElement("ul");
          list.className = "event-card-detail-list";
          items.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = String(item);
            list.appendChild(li);
          });
          block.appendChild(label);
          block.appendChild(list);
          body.appendChild(block);
          return;
        }
        const text = String(value || "").trim();
        if (!text) return;
        const block = document.createElement("div");
        block.className = "event-card-detail-block";
        const label = document.createElement("div");
        label.className = "event-card-detail-label";
        label.textContent = section.label;
        const content = document.createElement("div");
        content.className = "event-card-detail-text";
        content.textContent = text;
        block.appendChild(label);
        block.appendChild(content);
        body.appendChild(block);
      });
    } else if (String(msg.content || "").trim()) {
      body.textContent = msg.content;
    }

    if (body.childNodes.length || String(msg.content || "").trim()) {
      node.appendChild(body);
    }

    if (msg.ts) {
      const footer = document.createElement("div");
      footer.className = "msg-footer event-card-footer";
      footer.textContent = msg.ts;
      node.appendChild(footer);
    }

    return node;
  }

  function eventSequenceKey(row) {
    if (!row || row.kind !== "event_card") return "";
    if (row.task_ref?.task_id) return `task:${String(row.task_ref.task_id)}`;
    if (row.subagent_ref?.subagent_id) return `subagent:${String(row.subagent_ref.subagent_id)}`;
    return "";
  }

  function eventSequencePosition(rows, index) {
    const row = rows[index];
    const key = eventSequenceKey(row);
    if (!key) return "single";
    const prevKey = index > 0 ? eventSequenceKey(rows[index - 1]) : "";
    const nextKey = index + 1 < rows.length ? eventSequenceKey(rows[index + 1]) : "";
    const samePrev = prevKey && prevKey === key;
    const sameNext = nextKey && nextKey === key;
    if (samePrev && sameNext) return "middle";
    if (samePrev) return "end";
    if (sameNext) return "start";
    return "single";
  }

  function renderTextMessage(msg) {
    const role = msg.role === "tool" ? "system" : msg.role;
    const node = document.createElement("div");
    node.className = `msg ${role}`;
    const body = document.createElement("div");
    body.className = "msg-body";
    if (role === "assistant" && !msg.streaming) {
      body.classList.add("markdown");
      body.innerHTML = markdownToSafeHtml(msg.content || "");
    } else if (String(msg.content || "").trim()) {
      body.textContent = msg.content;
    }
    if (String(msg.content || "").trim() || role === "assistant") {
      const thinking = renderThinkingBlock(msg.thinking);
      if (thinking) node.appendChild(thinking);
      node.appendChild(body);
    }
    const attachments = Array.isArray(msg.attachments) ? msg.attachments : [];
    if (attachments.length) {
      const wrap = document.createElement("div");
      wrap.className = "msg-attachments";
      attachments.forEach((item) => {
        const card = document.createElement("div");
        const kind = String(item?.kind || "file");
        card.className = `msg-attachment ${kind}`;
        const title = document.createElement("div");
        title.className = "msg-attachment-name";
        title.textContent = String(item?.name || "attachment");
        const meta = document.createElement("div");
        meta.className = "msg-attachment-meta";
        const parts = [];
        if (item?.mime_type) parts.push(String(item.mime_type));
        if (item?.size_bytes) parts.push(`${item.size_bytes} B`);
        if (item?.width && item?.height) parts.push(`${item.width}x${item.height}`);
        meta.textContent = parts.join(" · ");
        if (kind === "image" && item?.local_path) {
          const imageUrl = `/api/v1/files/content?path=${encodeURIComponent(String(item.local_path).replace(/^\/+/, ""))}`;
          const button = document.createElement("button");
          button.type = "button";
          button.className = "msg-attachment-image-button";
          const img = document.createElement("img");
          img.className = "msg-attachment-image";
          img.src = imageUrl;
          img.alt = String(item?.name || "image");
          button.title = String(item?.name || "image");
          button.setAttribute("aria-label", String(item?.name || "image"));
          button.addEventListener("click", () => {
            openImagePreview({
              src: imageUrl,
              alt: String(item?.name || "image"),
              title: String(item?.name || "image"),
              meta: meta.textContent,
            });
          });
          button.appendChild(img);
          card.appendChild(button);
        }
        card.appendChild(title);
        if (meta.textContent) card.appendChild(meta);
        wrap.appendChild(card);
      });
      node.appendChild(wrap);
    }
    if (msg.ts) {
      const footer = document.createElement("div");
      footer.className = "msg-footer";
      footer.textContent = msg.ts;
      node.appendChild(footer);
    }
    return node;
  }

  function renderRowsIntoContainer(container, sourceRows, { keepBottom = true } = {}) {
    if (!container) return;
    container.innerHTML = "";
    const rows = (sourceRows || []).map((msg) => coerceRenderMessageRow(msg)).filter(Boolean);
    rows.forEach((row, index) => {
      if (row.kind === "tool_card") {
        container.appendChild(renderToolCardMessage(row));
        return;
      }

      if (row.kind === "event_card") {
        const node = renderEventCardMessage(row);
        const sequencePosition = eventSequencePosition(rows, index);
        node.classList.add(`event-card-seq-${sequencePosition}`);
        if (sequencePosition !== "single") node.classList.add("event-card-seq-connected");
        container.appendChild(node);
        return;
      }

      container.appendChild(renderTextMessage(row));
    });
    if (keepBottom) container.scrollTop = container.scrollHeight;
  }

  function renderMessages() {
    renderRowsIntoContainer(refs.chatMessages, state.messages || [], { keepBottom: true });
  }

  function taskStatusClass(status) {
    return `status-${String(status || "active").trim().toLowerCase() || "active"}`;
  }

  function renderTaskBoardSummary() {
    if (!refs.taskBoardSummary) return;
    const task = state.selectedTaskDetail;
    refs.taskBoardSummary.innerHTML = "";
    if (!task) return;

    const title = document.createElement("div");
    title.className = "task-board-summary-title";
    title.textContent = String(task.title || task.task_id || "");
    refs.taskBoardSummary.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "task-board-summary-meta";
    const metaParts = [];
    if (task.task_id) metaParts.push(`ID · ${String(task.task_id)}`);
    if (task.status) metaParts.push(`${observationLabel("status")} · ${observationValue("status", task.status)}`);
    if (task.priority) metaParts.push(`${observationLabel("priority")} · ${observationValue("priority", task.priority)}`);
    if (task.updated_at) metaParts.push(`${observationLabel("updated")} · ${String(task.updated_at)}`);
    meta.textContent = metaParts.join("   ");
    refs.taskBoardSummary.appendChild(meta);

    const summary = document.createElement("div");
    summary.className = "task-board-summary-progress";
    summary.textContent = String(task.latest_progress_summary || "").trim() || t("task_board_no_progress");
    refs.taskBoardSummary.appendChild(summary);

    const pending = Array.isArray(task.pending_questions) ? task.pending_questions : [];
    if (pending.length) {
      const block = document.createElement("div");
      block.className = "task-board-summary-progress";
      const lines = pending
        .map((item) => String(item?.question || item?.content || "").trim())
        .filter(Boolean);
      block.textContent = `${t("task_board_pending_label")} · ${lines.join(" / ")}`;
      refs.taskBoardSummary.appendChild(block);
    }
  }

  function renderTaskBoard() {
    const tasks = Array.isArray(state.tasks) ? state.tasks : [];
    const selectedId = String(state.selectedTaskId || "");
    if (refs.taskBoardCount) {
      const activeCount = tasks.filter((item) => ["active", "waiting"].includes(String(item?.status || "").trim())).length;
      const summaryText = formatTaskBoardCount(activeCount, tasks.length);
      refs.taskBoardCount.textContent = summaryText;
      refs.taskBoardCount.title = summaryText;
    }
    if (refs.taskBoardEmpty) refs.taskBoardEmpty.classList.toggle("hidden", tasks.length > 0);
    if (refs.taskBoardList) refs.taskBoardList.innerHTML = "";

    tasks.forEach((task) => {
      const item = document.createElement("div");
      item.className = `task-board-card${String(task.task_id || "") === selectedId ? " is-active" : ""}`;
      item.innerHTML = `
        <div class="task-board-card-head">
          <div>
            <div class="task-board-card-title">${esc(String(task.title || task.task_id || ""))}</div>
            <div class="task-board-card-meta">
              <span>${esc(String(task.task_id || ""))}</span>
              <span>${esc(String(task.updated_at || ""))}</span>
            </div>
          </div>
          <span class="task-board-status ${taskStatusClass(task.status)}">${esc(observationValue("status", task.status || ""))}</span>
        </div>
        <div class="task-board-card-summary">${esc(String(task.latest_progress_summary || "").trim() || t("task_board_no_progress"))}</div>
      `;
      item.addEventListener("click", () => {
        openTaskBoardModal(task.task_id).catch((err) => showActionError(err));
      });
      refs.taskBoardList.appendChild(item);
    });

    const hasSelected = Boolean(state.selectedTaskDetail && selectedId);
    if (hasSelected) {
      renderTaskBoardSummary();
      if (refs.taskBoardPlan) {
        const planContent = String(state.selectedTaskDetail?.plan_content || "").trim();
        refs.taskBoardPlan.innerHTML = planContent ? markdownToSafeHtml(planContent) : esc(t("task_board_plan_empty"));
      }
      renderRowsIntoContainer(refs.taskBoardMessages, state.selectedTaskMessages || [], { keepBottom: false });
    } else {
      if (refs.taskBoardSummary) refs.taskBoardSummary.innerHTML = "";
      if (refs.taskBoardPlan) refs.taskBoardPlan.innerHTML = "";
      if (refs.taskBoardMessages) refs.taskBoardMessages.innerHTML = "";
      if (refs.eventTimeline) refs.eventTimeline.innerHTML = "";
    }
    syncTaskBoardModal();
  }

  function clearEvents() {
    state.events = [];
    state.liveToolCardByStep = {};
    state.pendingThinkingByType = {};
    renderEvents();
  }

  function formatPayload(payload) {
    if (!payload) return "";
    if (typeof payload === "string") return payload;
    if (payload.task_id || payload.summary || payload.message_kind || payload.queued_count || payload.finish_mode) {
      const lines = [];
      if (payload.task_id) lines.push(`${observationLabel("task")}: ${payload.task_id}`);
      if (payload.status) lines.push(`${observationLabel("status")}: ${observationValue("status", payload.status)}`);
      if (payload.summary) lines.push(String(payload.summary));
      if (payload.message_kind) lines.push(`${observationLabel("messageKind")}: ${observationValue("messageKind", payload.message_kind)}`);
      if (payload.queued_count) lines.push(`${observationLabel("queued")}: ${payload.queued_count}`);
      if (payload.finish_mode) lines.push(`${observationLabel("finish")}: ${observationValue("finish", payload.finish_mode)}`);
      if (payload.from_status || payload.to_status) {
        lines.push(`${observationLabel("transition")}: ${observationTransition(payload.from_status, payload.to_status)}`);
      }
      if (lines.length) return lines.join("\n");
    }
    if (payload.arguments) {
      const args = typeof payload.arguments === "string" ? payload.arguments : JSON.stringify(payload.arguments);
      return `${t("payload_tool")}=${payload.tool_name || ""}\n${t("payload_args")}=${args}`;
    }
    if (payload.state || payload.phase || payload.error) {
      const lines = [];
      if (payload.state) lines.push(`${t("payload_state")}: ${payload.state}`);
      if (payload.phase) lines.push(`${t("payload_phase")}: ${payload.phase}`);
      if (payload.error) lines.push(`${t("payload_error")}: ${payload.error}`);
      if (lines.length) return lines.join("\n");
    }
    if (payload.content) return payload.content;
    if (payload.question) return payload.question;
    return JSON.stringify(payload, null, 2);
  }

  function buildTaskEventBody(payload) {
    const data = payload && typeof payload === "object" ? payload : {};
    const node = document.createElement("div");
    node.className = "event-task-body";

    const summaryText = String(data.summary || data.content || data.question || "").trim();
    if (summaryText) {
      const summary = document.createElement("div");
      summary.className = "event-task-summary";
      summary.textContent = summaryText;
      node.appendChild(summary);
    }

    const facts = [];
    if (data.task_id) facts.push([observationLabel("task"), String(data.task_id)]);
    if (data.status) facts.push([observationLabel("status"), observationValue("status", data.status)]);
    if (data.message_kind) facts.push([observationLabel("messageKind"), observationValue("messageKind", data.message_kind)]);
    if (data.queued_count) facts.push([observationLabel("queued"), String(data.queued_count)]);
    if (data.finish_mode) facts.push([observationLabel("finish"), observationValue("finish", data.finish_mode)]);
    if (data.from_status || data.to_status) {
      facts.push([observationLabel("transition"), observationTransition(data.from_status, data.to_status)]);
    }
    if (facts.length) {
      const grid = document.createElement("div");
      grid.className = "event-task-facts";
      facts.forEach(([labelText, valueText]) => {
        const item = document.createElement("div");
        item.className = "event-task-fact";
        const label = document.createElement("div");
        label.className = "event-task-fact-label";
        label.textContent = labelText;
        const value = document.createElement("div");
        value.className = "event-task-fact-value";
        value.textContent = valueText;
        item.appendChild(label);
        item.appendChild(value);
        grid.appendChild(item);
      });
      node.appendChild(grid);
    }

    return node;
  }

  function buildSubagentEventBody(payload) {
    const data = payload && typeof payload === "object" ? payload : {};
    const node = document.createElement("div");
    node.className = "event-subagent-body";

    const summaryText = String(data.summary || data.error || data.content || "").trim();
    if (summaryText) {
      const summary = document.createElement("div");
      summary.className = "event-subagent-summary";
      summary.textContent = summaryText;
      node.appendChild(summary);
    }

    const facts = [];
    if (data.subagent_id) facts.push([observationLabel("subagent"), String(data.subagent_id)]);
    if (data.status) facts.push([observationLabel("status"), observationValue("status", data.status)]);
    if (data.worker_kind) facts.push([observationLabel("kind"), observationValue("kind", data.worker_kind)]);
    if (facts.length) {
      const grid = document.createElement("div");
      grid.className = "event-subagent-facts";
      facts.forEach(([labelText, valueText]) => {
        const item = document.createElement("div");
        item.className = "event-subagent-fact";
        const label = document.createElement("div");
        label.className = "event-subagent-fact-label";
        label.textContent = labelText;
        const value = document.createElement("div");
        value.className = "event-subagent-fact-value";
        value.textContent = valueText;
        item.appendChild(label);
        item.appendChild(value);
        grid.appendChild(item);
      });
      node.appendChild(grid);
    }

    const result = data.result && typeof data.result === "object" ? data.result : {};
    const sections = [
      { key: "completed_work", label: observationLabel("completed"), kind: "list" },
      { key: "remaining_work", label: observationLabel("remaining"), kind: "list" },
      { key: "next_step", label: observationLabel("nextStep"), kind: "text" },
    ];
    sections.forEach((section) => {
      if (section.kind === "list") {
        const items = Array.isArray(result?.[section.key]) ? result[section.key].filter((item) => String(item || "").trim()) : [];
        if (!items.length) return;
        const block = document.createElement("div");
        block.className = "event-subagent-detail-block";
        const label = document.createElement("div");
        label.className = "event-subagent-detail-label";
        label.textContent = section.label;
        const list = document.createElement("ul");
        list.className = "event-subagent-detail-list";
        items.forEach((item) => {
          const li = document.createElement("li");
          li.textContent = String(item);
          list.appendChild(li);
        });
        block.appendChild(label);
        block.appendChild(list);
        node.appendChild(block);
        return;
      }
      const text = String(result?.[section.key] || "").trim();
      if (!text) return;
      const block = document.createElement("div");
      block.className = "event-subagent-detail-block";
      const label = document.createElement("div");
      label.className = "event-subagent-detail-label";
      label.textContent = section.label;
      const content = document.createElement("div");
      content.className = "event-subagent-detail-text";
      content.textContent = text;
      block.appendChild(label);
      block.appendChild(content);
      node.appendChild(block);
    });

    return node;
  }

  function buildEventBodyNode(type, payload) {
    if (TASK_EVENT_TYPES.has(String(type || ""))) return buildTaskEventBody(payload);
    if (SUBAGENT_EVENT_TYPES.has(String(type || ""))) return buildSubagentEventBody(payload);
    const node = document.createElement("div");
    node.className = "trace-content event-body";
    node.textContent = formatPayload(payload);
    return node;
  }

  function eventLabel(type) {
    const key = EVENT_LABEL_KEYS[type];
    return key ? t(key) : type;
  }

  function renderEvents(keepBottom = false) {
    refs.eventTimeline.innerHTML = "";
    (state.events || []).forEach((row) => {
      const item = document.createElement("div");
      const type = String(row?.type || "");
      item.className = `trace-item event-item ${row.isError ? "error" : ""} ${TASK_EVENT_TYPES.has(type) ? "event-item-task" : ""} ${SUBAGENT_EVENT_TYPES.has(type) ? "event-item-subagent" : ""}`;
      const title = document.createElement("div");
      title.className = "trace-type event-type";
      title.textContent = eventLabel(type);
      item.appendChild(title);
      item.appendChild(buildEventBodyNode(type, row.payload));
      refs.eventTimeline.appendChild(item);
    });
    if (keepBottom) refs.eventTimeline.scrollTop = refs.eventTimeline.scrollHeight;
  }

  function appendEvent(type, payload, isError = false) {
    state.events.push({ type, payload, isError });
    renderEvents(true);
  }

  function appendMessage(role, content, streaming = false) {
    const row = createTextMessageRow(role, content, streaming, Boolean(streaming));
    if (!row) return;
    state.messages.push(row);
    renderMessages();
  }

  function appendThinkingDelta(content, reasoningType = "general") {
    const text = String(content || "");
    if (!text) return;
    const key = String(reasoningType || "general");
    const current = state.pendingThinkingByType[key] || { content: "", reasoning_type: key, keep: false };
    current.content = String(current.content || "") + text;
    current.reasoning_type = key;
    state.pendingThinkingByType[key] = current;
    const last = state.messages[state.messages.length - 1];
    if (!last || last.kind !== "text" || last.role !== "assistant" || !last.streaming) {
      state.messages.push(createTextMessageRow("assistant", "", true, true));
    }
    state.messages[state.messages.length - 1].thinking = {
      content: String(current.content || ""),
      reasoning_type: key,
    };
    renderMessages();
  }

  function finalizeThinking(reasoningType = "general", keep = false) {
    const key = String(reasoningType || "general");
    const current = state.pendingThinkingByType[key];
    if (!current) return;
    current.keep = Boolean(keep);
    state.pendingThinkingByType[key] = current;
    if (!keep) delete state.pendingThinkingByType[key];
  }

  function consumePendingThinking(reasoningType = "general", { preserve = false } = {}) {
    const key = String(reasoningType || "general");
    const current = state.pendingThinkingByType[key];
    if (!current || !String(current.content || "").trim()) return "";
    const payload = { content: String(current.content || "").trim(), reasoning_type: key };
    if (!preserve) delete state.pendingThinkingByType[key];
    return payload;
  }

  function appendToolCardFromEvent(payload) {
    const step = String(payload?.step ?? "");
    const attachedThinking = consumePendingThinking(payload?.reasoning_type || "tool", { preserve: false });
    const msg = createToolCardMessageRow(
      payload?.tool_name || "tool",
      "",
      payload?.arguments || "",
      "",
      false,
      attachedThinking?.content || "",
      attachedThinking?.reasoning_type || "tool"
    );
    state.messages.push(msg);
    if (step) state.liveToolCardByStep[step] = state.messages.length - 1;
    renderMessages();
  }

  function updateToolCardFromEvent(payload) {
    const step = String(payload?.step ?? "");
    const index = step && Number.isInteger(state.liveToolCardByStep[step]) ? state.liveToolCardByStep[step] : -1;

    let target = null;
    if (index >= 0 && state.messages[index] && state.messages[index].kind === "tool_card") {
      target = state.messages[index];
    } else {
      for (let i = state.messages.length - 1; i >= 0; i -= 1) {
        const row = state.messages[i];
        if (row.kind === "tool_card" && !row.output_text) {
          target = row;
          break;
        }
      }
    }
    if (!target) return;

    const outputValue = payload?.result_preview || payload?.result || payload?.output || payload?.content || payload?.error || "";
    target.output_text = normalizeToolPayload(outputValue);
    renderMessages();
  }

  function mergeStreamingAssistantContent(currentContent, incomingDelta) {
    const current = String(currentContent || "");
    const incoming = String(incomingDelta || "");
    if (!incoming) return current;
    if (!current) return incoming;
    if (incoming.startsWith(current)) return incoming;
    if (current.startsWith(incoming)) return current;
    return current + incoming;
  }

  function appendAssistantDelta(delta) {
    const last = state.messages[state.messages.length - 1];
    if (!last || last.kind !== "text" || last.role !== "assistant" || !last.streaming) {
      state.messages.push(createTextMessageRow("assistant", "", true, true));
    }
    if (!state.messages[state.messages.length - 1].thinking) {
      const attachedThinking = consumePendingThinking("general", { preserve: false });
      if (attachedThinking) state.messages[state.messages.length - 1].thinking = attachedThinking;
    }
    // Some upstream providers stream true deltas, while others resend the
    // cumulative text so far. Merge both forms into the current bubble safely.
    state.messages[state.messages.length - 1].content = mergeStreamingAssistantContent(
      state.messages[state.messages.length - 1].content,
      delta
    );
    renderMessages();
  }

  function finalizeStreamingAssistant() {
    const last = state.messages[state.messages.length - 1];
    if (last && last.kind === "text" && last.role === "assistant" && last.streaming) {
      last.streaming = false;
      renderMessages();
    }
  }

  async function loadHealth() {
    try {
      const data = await api("/api/v1/health");
      state.healthOnline = data.success !== false;
    } catch {
      state.healthOnline = false;
    }
    renderHealth();
  }

  async function loadSessions(autoSelect = true) {
    const data = await api("/api/v1/sessions");
    state.sessions = data.sessions || [];
    renderSessions();
    if (autoSelect && !state.selected && state.sessions.length) {
      const preferred = state.sessions.find((s) => s.user_id === "web:local") || state.sessions[0];
      await selectSession(preferred);
    }
  }

  async function selectSession(session) {
    state.selected = {
      user_id: session.user_id,
      session_name: session.session_name,
      channel_prefix: session.channel_prefix,
    };
    state.selectedTaskId = "";
    state.selectedTaskDetail = null;
    state.selectedTaskMessages = [];
    state.taskBoardModalOpen = false;
    state.waitingHuman = false;
    state.pendingThinkingByType = {};
    clearEvents();
    refreshChatHeader();

    await api("/api/v1/sessions/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: session.user_id, session_name: session.session_name }),
    });

    state.selectedSessionMsgSig = "";
    await refreshSelectedSessionMessages(true);
    await refreshSelectedSessionTasks(true);
    renderSessions();
  }

  async function refreshSelectedSessionTasks(force = false) {
    if (!state.selected) return false;
    const userId = String(state.selected.user_id || "");
    const sessionName = String(state.selected.session_name || "");
    if (!userId || !sessionName) return false;
    const qs = new URLSearchParams({ user_id: userId, session_name: sessionName });
    const data = await api(`/api/v1/tasks?${qs.toString()}`);
    const tasks = Array.isArray(data.tasks) ? data.tasks : [];
    const previousSelectedId = String(state.selectedTaskId || "");
    state.tasks = tasks;
    renderTaskBoard();
    const selectedStillExists = tasks.some((item) => String(item.task_id || "") === previousSelectedId);
    const nextSelectedId = selectedStillExists
      ? previousSelectedId
      : String((tasks.find((item) => ["active", "waiting"].includes(String(item?.status || ""))) || tasks[0] || {}).task_id || "");
    if (!nextSelectedId) {
      state.selectedTaskId = "";
      state.selectedTaskDetail = null;
      state.selectedTaskMessages = [];
      state.taskBoardModalOpen = false;
      clearEvents();
      renderTaskBoard();
      return true;
    }
    if (force || nextSelectedId !== previousSelectedId) {
      await selectTask(nextSelectedId, { openModal: false });
      return true;
    }
    await refreshSelectedTaskDetail(nextSelectedId);
    return true;
  }

  async function selectTask(taskId, options = {}) {
    const cleanTaskId = String(taskId || "").trim();
    if (!cleanTaskId) return;
    state.selectedTaskId = cleanTaskId;
    state.taskBoardModalOpen = Boolean(options.openModal);
    await refreshSelectedTaskDetail(cleanTaskId);
    syncTaskBoardModal();
  }

  async function refreshSelectedTaskDetail(taskId) {
    if (!state.selected) return;
    const cleanTaskId = String(taskId || state.selectedTaskId || "").trim();
    if (!cleanTaskId) return;
    const userId = String(state.selected.user_id || "");
    const sessionName = String(state.selected.session_name || "");
    const qs = new URLSearchParams({ user_id: userId, session_name: sessionName });
    const [detail, messages, taskEvents] = await Promise.all([
      api(`/api/v1/tasks/${encodeURIComponent(cleanTaskId)}?${qs.toString()}`),
      api(`/api/v1/tasks/${encodeURIComponent(cleanTaskId)}/messages?${qs.toString()}`),
      api(`/api/v1/sessions/task-events?${new URLSearchParams({ user_id: userId, session_name: sessionName, task_id: cleanTaskId }).toString()}`),
    ]);
    state.selectedTaskId = cleanTaskId;
    state.selectedTaskDetail = detail.task || null;
    state.selectedTaskMessages = Array.isArray(messages.render_messages) ? messages.render_messages : [];
    state.events = Array.isArray(taskEvents.events)
      ? taskEvents.events.map((row) => ({
          type: String(row?.type || ""),
          payload: row?.payload && typeof row.payload === "object" ? row.payload : {},
          isError: false,
        }))
      : [];
    renderEvents(false);
    renderTaskBoard();
  }

  async function ensureSelectedSession() {
    if (state.selected) return;
    const created = await api("/api/v1/sessions/new", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "web:local" }),
    });
    await loadSessions(false);
    const target = (state.sessions || []).find(
      (s) => s.user_id === created.session.user_id && s.session_name === created.session.session_name
    );
    if (target) await selectSession(target);
  }

  function onSseEvent(eventName, data) {
    if (eventName === "connected") {
      state.currentRequestId = data.request_id || "";
      appendEvent("connected", data);
      return;
    }
    const payload = data.payload || data;
    switch (eventName) {
      case "run_started":
        state.currentRequestId = payload.request_id || state.currentRequestId;
        appendEvent("run_started", payload);
        break;
      case "assistant_thinking_delta":
        appendEvent("assistant_thinking_delta", payload);
        appendThinkingDelta(payload.content || payload.reasoning_content || "", payload.reasoning_type || "general");
        break;
      case "assistant_thinking_done":
        appendEvent("assistant_thinking_done", payload);
        finalizeThinking(payload.reasoning_type || "general", Boolean(payload.keep));
        break;
      case "tool_before":
        appendEvent("tool_before", payload);
        appendToolCardFromEvent(payload);
        break;
      case "tool_after":
        appendEvent("tool_after", payload, Boolean(payload.error));
        updateToolCardFromEvent(payload);
        break;
      case "ask_human":
        state.waitingHuman = true;
        appendEvent("ask_human", payload);
        appendMessage("system", payload.question || t("waiting_input"));
        break;
      case "status":
        appendEvent("status", payload, payload.state === "failed");
        break;
      case "assistant_delta":
        appendAssistantDelta(payload.delta || "");
        break;
      case "run_done":
        finalizeStreamingAssistant();
        state.currentRequestId = "";
        state.pendingThinkingByType = {};
        appendEvent("run_done", payload, payload.success === false);
        refreshSelectedSessionTasks(true).catch((err) => console.warn("task board refresh failed", err));
        break;
      default:
        appendEvent(eventName, payload);
        break;
    }
  }

  function handleSseBlock(block) {
    if (!block) return;
    const lines = block.split("\n");
    let eventName = "message";
    let dataRaw = "";
    for (const line of lines) {
      if (line.startsWith("event:")) eventName = line.slice(6).trim();
      if (line.startsWith("data:")) dataRaw += line.slice(5).trim();
    }
    let data = {};
    try {
      data = dataRaw ? JSON.parse(dataRaw) : {};
    } catch {
      data = { raw: dataRaw };
    }
    onSseEvent(eventName, data);
  }

  function normalizeUiLanguage(value) {
    return String(value || "").trim().toLowerCase() === "en" ? "en" : "zh";
  }

  function normalizeThemeMode(value) {
    const text = String(value || "").trim().toLowerCase();
    return ["dark", "auto"].includes(text) ? text : "light";
  }

  function buildRuntimeSettingsPayload() {
    return {
      ui: {
        language: state.lang,
        theme_mode: state.themeMode,
      },
      chat: {
        preferred_response_language: state.replyLanguage,
      },
    };
  }

  function applyRuntimeSettings(payload) {
    const ui = payload && payload.ui ? payload.ui : {};
    const chat = payload && payload.chat ? payload.chat : {};
    state.lang = normalizeUiLanguage(ui.language);
    state.themeMode = normalizeThemeMode(ui.theme_mode);
    state.replyLanguage = normalizeUiLanguage(chat.preferred_response_language);
    localStorage.setItem(LANG_KEY, state.lang);
    localStorage.setItem("themeMode", state.themeMode);
    localStorage.setItem("WeClaw_reply_language", state.replyLanguage);
  }

  async function loadRuntimeSettings() {
    const payload = await api("/api/v1/settings");
    applyRuntimeSettings(payload || {});
    return payload;
  }

  async function saveRuntimeSettings() {
    const payload = buildRuntimeSettingsPayload();
    const saved = await api("/api/v1/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    applyRuntimeSettings(saved || payload);
    return saved;
  }

  async function streamChat(content) {
    const response = await fetch("/api/v1/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        request_id: "",
        user_id: state.selected.user_id,
        session_name: state.selected.session_name,
        content,
        continue_mode: "in_place",
        source: "web",
        inject_uploaded_files: true,
        reply_language: state.replyLanguage,
      }),
    });
    if (!response.ok || !response.body) {
      throw new Error((await response.text()) || t("stream_failed"));
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";
      blocks.forEach((block) => handleSseBlock(block.trim()));
    }
    if (buffer.trim()) handleSseBlock(buffer.trim());
    finalizeStreamingAssistant();
    await loadSessions(false);
    await refreshSelectedSessionMessages(true);
  }

  async function sendMessage() {
    if (state.mcpChatGuard && state.mcpChatGuard.blocked) {
      throw new Error(localMcpChatGuardMessage());
    }
    const content = refs.chatInput.value.trim();
    if (!content) return;
    await ensureSelectedSession();
    if (!state.selected) return;
    refs.chatInput.value = "";

    if (state.waitingHuman) {
      await api("/api/v1/chat/human-input", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: state.selected.user_id, content }),
      });
      appendMessage("user", content);
      state.waitingHuman = false;
      appendEvent("human_input", { content: t("human_input_submitted") });
      return;
    }

    appendMessage("user", content);
    await streamChat(content);
  }

  async function cancelCurrent() {
    if (!state.currentRequestId) return;
    await api("/api/v1/chat/cancel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request_id: state.currentRequestId }),
    });
    appendEvent("cancel", { request_id: state.currentRequestId });
  }

  async function uploadFile(file) {
    await ensureSelectedSession();
    const form = new FormData();
    form.append("file", file);
    form.append("user_id", state.selected ? state.selected.user_id : "web:local");
    const response = await fetch("/api/v1/files/upload", { method: "POST", body: form });
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    appendEvent("file_uploaded", data.file || {});
  }

  function pickVoiceMimeType() {
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
    ];
    if (typeof MediaRecorder === "undefined" || typeof MediaRecorder.isTypeSupported !== "function") {
      return "";
    }
    for (const mime of candidates) {
      try {
        if (MediaRecorder.isTypeSupported(mime)) return mime;
      } catch {
        // Ignore and continue.
      }
    }
    return "";
  }

  function updateVoiceUi() {
    if (refs.voiceInputBtn) {
      refs.voiceInputBtn.textContent = state.voiceRecording ? t("btn_voice_stop") : t("btn_voice_start");
      refs.voiceInputBtn.classList.toggle("voice-recording", Boolean(state.voiceRecording));
    }
    if (refs.voiceInputStatus) {
      refs.voiceInputStatus.textContent = t(state.voiceStatusKey || "voice_idle");
      refs.voiceInputStatus.classList.toggle("recording", Boolean(state.voiceRecording));
    }
  }

  function cleanupVoiceStream() {
    const stream = state.voiceStream;
    state.voiceStream = null;
    if (!stream) return;
    try {
      stream.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // Ignore cleanup errors.
        }
      });
    } catch {
      // Ignore cleanup errors.
    }
  }

  async function transcribeVoiceBlob(blob, mimeType) {
    if (!blob || !blob.size) {
      state.voiceStatusKey = "voice_empty";
      updateVoiceUi();
      return;
    }
    state.voiceStatusKey = "voice_transcribing";
    updateVoiceUi();

    const ext = mimeType && mimeType.includes("ogg") ? "ogg" : mimeType && mimeType.includes("mp4") ? "m4a" : "webm";
    const form = new FormData();
    form.append("file", blob, `voice_input.${ext}`);
    form.append("language", "auto");
    form.append("task", "transcribe");

    const response = await fetch("/api/v1/speech/transcribe", {
      method: "POST",
      body: form,
    });
    if (!response.ok) {
      throw new Error((await response.text()) || "speech transcribe failed");
    }
    const data = await response.json();
    const text = String((data.result || {}).text || "").trim();
    if (!text) {
      state.voiceStatusKey = "voice_empty";
      updateVoiceUi();
      return;
    }

    const current = String(refs.chatInput?.value || "");
    refs.chatInput.value = current ? `${current}\n${text}` : text;
    state.voiceStatusKey = "voice_transcribed";
    updateVoiceUi();
  }

  async function startVoiceInput() {
    if (state.voiceRecording) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || typeof MediaRecorder === "undefined") {
      state.voiceStatusKey = "voice_unsupported";
      updateVoiceUi();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = pickVoiceMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      state.voiceStream = stream;
      state.voiceMediaRecorder = recorder;
      state.voiceChunks = [];

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          state.voiceChunks.push(event.data);
        }
      };

      recorder.onerror = () => {
        state.voiceRecording = false;
        state.voiceStatusKey = "voice_idle";
        cleanupVoiceStream();
        updateVoiceUi();
      };

      recorder.onstop = async () => {
        const chunks = Array.isArray(state.voiceChunks) ? state.voiceChunks.slice() : [];
        state.voiceChunks = [];
        const finalMime = recorder.mimeType || mimeType || "audio/webm";
        state.voiceMediaRecorder = null;
        cleanupVoiceStream();
        state.voiceRecording = false;
        updateVoiceUi();

        try {
          const blob = new Blob(chunks, { type: finalMime });
          await transcribeVoiceBlob(blob, finalMime);
        } catch (err) {
          state.voiceStatusKey = "voice_idle";
          updateVoiceUi();
          showActionError(err);
        }
      };

      recorder.start(250);
      state.voiceRecording = true;
      state.voiceStatusKey = "voice_recording";
      updateVoiceUi();
    } catch (err) {
      const message = String(err || "").toLowerCase();
      state.voiceStatusKey = message.includes("denied") || message.includes("notallowed") ? "voice_permission_denied" : "voice_idle";
      updateVoiceUi();
      if (state.voiceStatusKey === "voice_permission_denied") {
        showNoticeModal({ titleKey: "notice_title_error", body: t("voice_permission_denied"), variant: "error" });
      } else {
        showActionError(err);
      }
    }
  }

  function stopVoiceInput() {
    const recorder = state.voiceMediaRecorder;
    if (!recorder) return;
    try {
      if (recorder.state === "recording") {
        recorder.stop();
      }
    } catch (err) {
      cleanupVoiceStream();
      state.voiceRecording = false;
      state.voiceStatusKey = "voice_idle";
      updateVoiceUi();
      throw err;
    }
  }

  function toggleVoiceInput() {
    if (state.voiceRecording) {
      stopVoiceInput();
      return;
    }
    startVoiceInput().catch((err) => {
      state.voiceStatusKey = "voice_idle";
      updateVoiceUi();
      showActionError(err);
    });
  }

  function buildAlarmMetaRows(job) {
    const targetSession = job.session_name || "-";
    const channel = job.channel || "unknown";
    return `
      <div><b>${esc(job.id)}</b></div>
      <div>${zhen("调度类型", "Schedule")}: ${esc(job.schedule_type || "-")}</div>
      <div>${zhen("关联会话", "Session")}: ${esc(targetSession)}</div>
      <div>${zhen("关联频道", "Channel")}: ${esc(channel)}</div>
      <div>${zhen("目标用户", "User")}: ${esc(job.user_id || "-")}</div>
      <div>${zhen("下一次触发", "Next Run")}: ${esc(job.next_run_at || "-")}</div>
      <div>${zhen("最近一次执行", "Last Run")}: ${esc(job.last_run_at || "-")}</div>
      <div>${zhen("最近状态", "Last Status")}: ${esc(job.last_status || "-")}</div>
      <div>${zhen("最近结果", "Last Result")}: ${esc(job.last_result || "")}</div>
    `;
  }

  function renderAlarmRows(container, jobs, { actionable = false } = {}) {
    if (!container) return;
    container.innerHTML = "";
    if (!Array.isArray(jobs) || !jobs.length) {
      container.textContent = zhen("暂无任务。", "No alarms.");
      return;
    }
    jobs.forEach((job) => {
      const row = document.createElement("div");
      row.className = "table-row";
      row.innerHTML = buildAlarmMetaRows(job);
      const actions = document.createElement("div");
      actions.className = "row-actions";
      if (job.session_name) {
        actions.append(
          makeActionBtn(zhen("打开会话", "Open Session"), async () => {
            await setView("chat");
            await selectSession({
              user_id: job.user_id || "web:local",
              session_name: job.session_name,
              channel_prefix: job.channel || "unknown",
            });
          }),
        );
      }
      if (actionable) {
        if (job.paused) {
          actions.append(
            makeActionBtn(t("btn_resume"), async () => {
              await api(`/api/v1/alarms/${encodeURIComponent(job.id)}/resume`, { method: "POST" });
              await loadAlarms();
            }),
          );
        } else {
          actions.append(
            makeActionBtn(t("btn_pause"), async () => {
              await api(`/api/v1/alarms/${encodeURIComponent(job.id)}/pause`, { method: "POST" });
              await loadAlarms();
            }),
          );
        }
        actions.append(
          makeActionBtn(zhen("取消", "Cancel"), async () => {
            await api(`/api/v1/alarms/${encodeURIComponent(job.id)}/cancel`, { method: "POST" });
            await loadAlarms();
          }),
        );
      }
      row.appendChild(actions);
      container.appendChild(row);
    });
  }

  function renderAlarms() {
    const alarms = state.alarms || [];
    const active = alarms.filter((job) => String(job.status || "") !== "finished");
    const finished = alarms.filter((job) => String(job.status || "") === "finished");
    const paused = active.filter((job) => Boolean(job.paused));
    if (refs.alarmsSummary) {
      refs.alarmsSummary.textContent =
        `${zhen("活动任务", "Active")}: ${active.length}\n` +
        `${zhen("暂停任务", "Paused")}: ${paused.length}\n` +
        `${zhen("已结束任务", "Finished")}: ${finished.length}`;
    }
    renderAlarmRows(refs.activeAlarmsList, active, { actionable: true });
    renderAlarmRows(refs.finishedAlarmsList, finished, { actionable: false });
  }

  async function loadAlarms() {
    const payload = await api("/api/v1/alarms");
    state.alarms = [...(payload.active_jobs || []), ...(payload.finished_jobs || [])];
    renderAlarms();
  }

  function channelStatusText(row) {
    if (!row || !row.enabled) return zhen("已禁用", "Disabled");
    if (row.ready) return zhen("已启用", "Enabled");
    return zhen("配置不完整", "Config Incomplete");
  }

  function channelStatusClass(row) {
    if (!row || !row.enabled) return "disabled";
    if (row.ready) return "enabled";
    return "error";
  }

  function summarizeChannel(row) {
    if (!row) return "-";
    const settings = {};
    (row.fields || []).forEach((field) => {
      settings[field.key] = field.secret ? (field.has_value ? "••••••" : "") : String(field.value || "");
    });
    if (row.name === "web") return settings.base_url || row.launch_hint || "-";
    if (row.name === "cli") return settings.command || row.launch_hint || "-";
    if (row.name === "qq") return settings.app_id ? `app_id=${settings.app_id}` : row.launch_hint || "-";
    if (row.name === "discord") {
      if (settings.guild_id) return `guild_id=${settings.guild_id}`;
      if (settings.http_proxy) return `proxy=${settings.http_proxy}`;
      return row.launch_hint || "-";
    }
    return row.launch_hint || "-";
  }

  function renderChannels() {
    if (!refs.channelsGrid) return;
    refs.channelsGrid.innerHTML = "";
    const rows = state.channels || [];
    if (!rows.length) {
      refs.channelsGrid.textContent = t("no_channels");
      return;
    }
    rows.forEach((row) => {
      const statusClass = channelStatusClass(row);
      const missingText = row.enabled && !row.ready ? channelRequiredHint(row.missing_required || []) : "";
      const card = createResourceCard({
        baseClass: `channel-card ${row.enabled ? "active" : "disabled"}`,
        title: channelDisplayName(row.name, row.display_name || row.name),
        subtitle: row.name || "-",
        badgeText: channelStatusText(row),
        badgeClass: statusClass === "enabled" ? "ok" : statusClass === "error" ? "warn" : "",
        description: row.description || "-",
        metaItems: [
          { label: zhen("Summary", "Summary"), value: summarizeChannel(row) },
          { label: zhen("Config", "Config"), value: missingText || (row.bot_prefix ? `prefix=${row.bot_prefix}` : row.launch_hint || "-") },
          { label: zhen("Runtime", "Runtime"), value: channelRuntimeStatusText(row) },
          { label: zhen("Launch", "Launch"), value: row.launch_command || "-" },
        ],
        onCardClick: () => openChannelDrawer(row.name),
      });
      refs.channelsGrid.appendChild(card);
    });
  }

  function openChannelDrawer(channelName) {
    if (!refs.channelDrawer) return;
    const target = (state.channels || []).find((row) => row.name === channelName);
    if (!target) return;
    state.channelEditor = JSON.parse(JSON.stringify(target));
    refs.channelEnabledInput.checked = Boolean(state.channelEditor.enabled);
    refs.channelPrefixInput.value = String(state.channelEditor.bot_prefix || "");
    refs.channelDrawerTitle.textContent = `${channelDisplayName(target.name, target.display_name || target.name)} ${zhen("设置", "Settings")}`;

    refs.channelFields.innerHTML = "";
    (state.channelEditor.fields || []).forEach((field) => {
      const wrap = document.createElement("label");
      wrap.className = "channel-field";
      const requiredMark = field.required ? " *" : "";
      const hint = field.secret && field.has_value ? zhen("已配置，留空不改", "configured, blank keeps current") : (field.placeholder || "");
      const type = field.type === "number" ? "number" : (field.secret ? "password" : "text");
      wrap.innerHTML = `
        <span>${esc(channelFieldLabel(field.key))}${requiredMark}</span>
        <input
          type="${type}"
          data-channel-key="${esc(field.key)}"
          data-channel-secret="${field.secret ? "1" : "0"}"
          value="${field.secret ? "" : esc(String(field.value || ""))}"
          placeholder="${esc(hint)}"
        />
      `;
      refs.channelFields.appendChild(wrap);
    });

    const missing = state.channelEditor.missing_required || [];
    refs.channelDrawerHint.textContent = missing.length ? channelRequiredHint(missing) : (target.launch_hint || "");
    refs.channelDrawer.classList.remove("hidden");
  }

  function closeChannelDrawer() {
    if (!refs.channelDrawer) return;
    state.channelEditor = null;
    refs.channelDrawer.classList.add("hidden");
  }

  async function loadChannels() {
    state.channels = (await api("/api/v1/channels")).channels || [];
    renderChannels();
  }

  async function saveChannelConfig() {
    if (!state.channelEditor || !refs.channelFields) return;
    const settings = {};
    refs.channelFields.querySelectorAll("input[data-channel-key]").forEach((input) => {
      const key = input.getAttribute("data-channel-key");
      const secret = input.getAttribute("data-channel-secret") === "1";
      const text = String(input.value || "").trim();
      if (!key) return;
      if (secret && !text) return;
      settings[key] = text;
    });

    const payload = {
      enabled: refs.channelEnabledInput.checked,
      bot_prefix: refs.channelPrefixInput.value.trim(),
      settings,
    };
    const response = await api(`/api/v1/channels/${encodeURIComponent(state.channelEditor.name)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.channels = response.channels || [];
    closeChannelDrawer();
    renderChannels();
  }

  function buildSkillsViewModel(rows) {
    const all = Array.isArray(rows) ? rows.filter(Boolean) : [];
    const activated = [];
    const inactivated = [];
    all.forEach((skill) => {
      if (skill.enabled) {
        activated.push(skill);
      } else {
        inactivated.push(skill);
      }
    });
    return {
      all,
      activated,
      inactivated,
      hasAnySkills: all.length > 0,
    };
  }

  function renderSkillsSection(skills, container) {
    skills.forEach((skill) => {
      const skillPath = skill.path || "-";
      const skillName = skill.name || skill.skill_id || skill.directory || "";
      const skillDesc = skill.description || "-";
      const statusLabel = skill.enabled ? t("skills_enabled") : t("skills_disabled");
      const kindLabel = skill.kind || "-";
      const card = createResourceCard({
        baseClass: `skill-card ${skill.enabled ? "active" : "disabled"}`,
        title: skillName,
        subtitle: skill.skill_id || skill.directory || "-",
        badgeText: statusLabel,
        badgeClass: skill.enabled ? "ok" : "",
        description: skillDesc,
        metaItems: [
          { label: t("skill_path"), value: skillPath, mono: true },
          { label: "kind", value: kindLabel },
          { label: "source", value: skill.source_id || "-" },
          { label: "directory", value: skill.directory || "-" },
        ],
        actions: [{
          label: skill.enabled ? t("skills_disable") : t("skills_enable"),
          className: "btn-ghost",
          onClick: async () => {
            const endpoint = skill.enabled ? "disable" : "enable";
            const response = await api(`/api/v1/skills/${encodeURIComponent(skill.skill_id)}/${endpoint}`, {
              method: "POST",
            });
            state.skills = response.skills || [];
            renderSkills();
          },
        }],
      });
      container.appendChild(card);
    });
  }

  function renderSkillsStorePanel() {
    const isOpen = Boolean(state.skillsStoreOpen);
    refs.skillsStorePanel.classList.toggle("hidden", !isOpen);
    refs.openSkillsStoreBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    refs.skillsContent.dataset.store = isOpen ? "open" : "closed";
  }

  function toggleSkillsStore(forceOpen = null) {
    state.skillsStoreOpen = typeof forceOpen === "boolean" ? forceOpen : !state.skillsStoreOpen;
    renderSkillsStorePanel();
  }

  function renderSkills() {
    refs.activatedSkillsGrid.innerHTML = "";
    refs.inactivatedSkillsGrid.innerHTML = "";
    const viewModel = buildSkillsViewModel(state.skills);
    refs.skillsContent.dataset.state = viewModel.hasAnySkills ? "populated" : "empty";
    renderSkillsStorePanel();
    if (!viewModel.hasAnySkills) {
      refs.skillsEmptyState.classList.remove("hidden");
      refs.skillsPopulatedState.classList.add("hidden");
      return;
    }
    refs.skillsEmptyState.classList.add("hidden");
    refs.skillsPopulatedState.classList.remove("hidden");
    renderSkillsSection(viewModel.activated, refs.activatedSkillsGrid);
    renderSkillsSection(viewModel.inactivated, refs.inactivatedSkillsGrid);
  }

  async function loadSkills() {
    state.skills = (await api("/api/v1/skills")).skills || [];
    renderSkills();
  }

  function defaultRemoteEndpoint() {
    return "https://open.bigmodel.cn/api/mcp-broker/proxy/web-search/mcp";
  }

  function findMcpServer(serverId) {
    const targetId = String(serverId || "").trim();
    return (state.mcpDiscovered || []).find((item) => String(item.server_id || "").trim() === targetId) || null;
  }

  function normalizeMcpToolRows(rows) {
    return (Array.isArray(rows) ? rows : [])
      .map((item) => ({
        name: String(item?.name || "").trim(),
        description: String(item?.description || "").trim(),
        selected: item?.selected !== false,
      }))
      .filter((item) => item.name);
  }

  function buildLocalSecretSlots(server) {
    return (Array.isArray(server?.required_secrets) ? server.required_secrets : [])
      .map((item) => String(item || "").trim())
      .filter(Boolean)
      .map((slotName) => ({
        slot_name: slotName,
        masked_value: "",
        has_value: false,
      }));
  }

  function buildLocalToolRows(server) {
    return (Array.isArray(server?.tools) ? server.tools : [])
      .map((name) => String(name || "").trim())
      .filter(Boolean)
      .map((name) => ({
        name,
        description: "",
        selected: true,
      }));
  }

  function serializeMcpArgs(args) {
    return (Array.isArray(args) ? args : [])
      .map((item) => String(item || "").trim())
      .filter(Boolean)
      .join("\n");
  }

  function parseMcpArgs(text) {
    const rows = [];
    String(text || "")
      .split(/\r?\n/)
      .map((item) => item.trim())
      .filter(Boolean)
      .forEach((item) => rows.push(item));
    return rows;
  }

  function renderMcpSecretSlots(secretSlots = []) {
    if (!refs.mcpSecretSlots) return;
    refs.mcpSecretSlots.innerHTML = "";
    const slots = Array.isArray(secretSlots) ? secretSlots : [];
    refs.mcpSecretSlots.hidden = slots.length === 0;
    refs.mcpSecretSlots.style.display = slots.length ? "" : "none";
    slots.forEach((slot) => {
      const label = document.createElement("label");
      label.className = "model-field";
      const title = document.createElement("span");
      title.textContent = String(slot.slot_name || "secret");
      const input = document.createElement("input");
      input.type = "password";
      input.dataset.slotName = String(slot.slot_name || "");
      input.placeholder = String(slot.masked_value || "").trim() || zhen("留空表示保持不变", "Leave blank to keep current value");
      input.autocomplete = "new-password";
      label.appendChild(title);
      label.appendChild(input);
      refs.mcpSecretSlots.appendChild(label);
    });
  }

  function renderMcpToolSelector(toolRows = []) {
    if (!refs.mcpToolsList || !refs.mcpToolsPanel) return;
    refs.mcpToolsList.innerHTML = "";
    const rows = normalizeMcpToolRows(toolRows);
    const summary = refs.mcpToolsPanel.querySelector("summary");
    if (summary) summary.textContent = zhen("启用工具", "Enabled Tools");
    if (!rows.length) {
      refs.mcpToolsList.textContent = zhen("当前没有可配置的工具。", "No tools are available yet.");
      return;
    }
    rows.forEach((tool) => {
      const label = document.createElement("label");
      label.className = "inline-check";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.className = "switch-input";
      input.dataset.toolName = tool.name;
      input.checked = tool.selected !== false;
      const slider = document.createElement("span");
      slider.className = "switch-slider";
      slider.setAttribute("aria-hidden", "true");
      const thumb = document.createElement("span");
      thumb.className = "switch-thumb";
      slider.appendChild(thumb);
      const text = document.createElement("span");
      text.className = "check-label";
      text.textContent = tool.description ? `${tool.name} - ${tool.description}` : tool.name;
      label.appendChild(input);
      label.appendChild(slider);
      label.appendChild(text);
      refs.mcpToolsList.appendChild(label);
    });
  }

  function readMcpSecretValues() {
    const rows = {};
    if (!refs.mcpSecretSlots) return rows;
    refs.mcpSecretSlots.querySelectorAll("input[data-slot-name]").forEach((input) => {
      const slotName = String(input.dataset.slotName || "").trim();
      const value = String(input.value || "").trim();
      if (slotName && value) rows[slotName] = value;
    });
    return rows;
  }

  function readSelectedMcpTools(toolRows = []) {
    const rows = normalizeMcpToolRows(toolRows);
    if (!rows.length || !refs.mcpToolsList) return [];
    const selected = [];
    refs.mcpToolsList.querySelectorAll("input[data-tool-name]").forEach((input) => {
      if (input.checked) selected.push(String(input.dataset.toolName || "").trim());
    });
    if (!selected.length || selected.length === rows.length) return [];
    return selected;
  }

  function currentMcpEditorTools() {
    if (!state.mcpEditor) return [];
    const mode = String(refs.mcpClientModeSelect?.value || state.mcpEditor.mode || "local").trim();
    if (mode === "local") {
      const server = findMcpServer(refs.mcpClientServerSelect?.value || "") || state.mcpEditor.server || null;
      const originalServerId = String(state.mcpEditor.client?.server_id || "").trim();
      const currentServerId = String(server?.server_id || "").trim();
      if (
        state.mcpEditor.client &&
        (
          (originalServerId && originalServerId === currentServerId) ||
          (!originalServerId && String(state.mcpEditor.client.command || "").trim())
        ) &&
        Array.isArray(state.mcpEditor.client.available_tools) &&
        state.mcpEditor.client.available_tools.length
      ) {
        return normalizeMcpToolRows(state.mcpEditor.client.available_tools);
      }
      return buildLocalToolRows(server);
    }
    return normalizeMcpToolRows(state.mcpEditor.availableTools || []);
  }

  function currentMcpEditorSecrets() {
    if (!state.mcpEditor) return [];
    const mode = String(refs.mcpClientModeSelect?.value || state.mcpEditor.mode || "local").trim();
    if (mode === "local") {
      const server = findMcpServer(refs.mcpClientServerSelect?.value || "") || state.mcpEditor.server || null;
      const originalServerId = String(state.mcpEditor.client?.server_id || "").trim();
      const currentServerId = String(server?.server_id || "").trim();
      if (
        state.mcpEditor.client &&
        (
          (originalServerId && originalServerId === currentServerId) ||
          (!originalServerId && String(state.mcpEditor.client.command || "").trim())
        ) &&
        Array.isArray(state.mcpEditor.client.secret_slots) &&
        state.mcpEditor.client.secret_slots.length
      ) {
        return state.mcpEditor.client.secret_slots;
      }
      return buildLocalSecretSlots(server);
    }
    if (Array.isArray(state.mcpEditor.secretSlots) && state.mcpEditor.secretSlots.length) {
      return state.mcpEditor.secretSlots;
    }
    return [{ slot_name: "api_key", masked_value: "", has_value: false }];
  }

  function setMcpFieldVisible(element, visible) {
    if (!element) return;
    element.hidden = !visible;
    element.style.display = visible ? "" : "none";
  }

  function refreshMcpEditorUi() {
    if (!refs.mcpModal || refs.mcpModal.classList.contains("hidden")) return;
    const mode = String(refs.mcpClientModeSelect?.value || "local").trim();
    const localMode = mode === "local";
    const server = findMcpServer(refs.mcpClientServerSelect?.value || "");

    if (state.mcpEditor) {
      state.mcpEditor.mode = mode;
      if (server) state.mcpEditor.server = server;
    }

    setMcpFieldVisible(refs.mcpClientServerField, localMode);
    setMcpFieldVisible(refs.mcpClientCommandField, localMode);
    setMcpFieldVisible(refs.mcpClientArgsField, localMode);
    setMcpFieldVisible(refs.mcpClientCwdField, localMode);
    setMcpFieldVisible(refs.mcpClientEndpointField, !localMode);
    if (refs.mcpClientServerSelect) refs.mcpClientServerSelect.disabled = !localMode;
    if (refs.mcpClientCommandInput) refs.mcpClientCommandInput.disabled = !localMode;
    if (refs.mcpClientArgsInput) refs.mcpClientArgsInput.disabled = !localMode;
    if (refs.mcpClientCwdInput) refs.mcpClientCwdInput.disabled = !localMode;
    if (refs.mcpClientEndpointInput) refs.mcpClientEndpointInput.disabled = localMode;

    if (localMode) {
      if (refs.mcpClientEndpointInput) refs.mcpClientEndpointInput.value = "";
    } else if (refs.mcpClientEndpointInput && !String(refs.mcpClientEndpointInput.value || "").trim()) {
      refs.mcpClientEndpointInput.value = defaultRemoteEndpoint();
    }

    const secretSlots = currentMcpEditorSecrets();
    renderMcpSecretSlots(secretSlots);
    renderMcpToolSelector(currentMcpEditorTools());
    const hasLocalCommand = Boolean(String(refs.mcpClientCommandInput?.value || "").trim());

    if (refs.mcpSecretHelp) {
      if (localMode && !server && !hasLocalCommand) {
        refs.mcpSecretHelp.textContent = t("mcp_no_server_selected");
      } else if (!secretSlots.length) {
        refs.mcpSecretHelp.textContent = t("mcp_no_secret_needed");
      } else {
        const labels = secretSlots.map((item) => String(item.slot_name || "").trim()).filter(Boolean);
        refs.mcpSecretHelp.textContent = `${t("mcp_required_secret_refs")}: ${labels.join(", ") || "-"}`;
      }
    }
  }

  function populateMcpServerOptions() {
    if (!refs.mcpClientServerSelect) return;
    refs.mcpClientServerSelect.innerHTML = "";
    const rows = state.mcpDiscovered || [];
    rows.forEach((server) => {
      const option = document.createElement("option");
      option.value = server.server_id || "";
      option.textContent = mcpDisplayName(server);
      refs.mcpClientServerSelect.appendChild(option);
    });
  }

  function openMcpModal(options = {}) {
    if (!refs.mcpModal) return;
    populateMcpServerOptions();
    const client = options && options.client ? options.client : null;
    const serverId = String(options?.serverId || client?.server_id || "").trim();
    const remoteMode = String(options?.mode || client?.mode || "local").trim() === "remote";
    const server = findMcpServer(serverId) || (state.mcpDiscovered || [])[0] || null;

    state.mcpEditor = {
      editingId: client ? String(client.client_id || "").trim() : "",
      client,
      mode: remoteMode ? "remote" : "local",
      server,
      availableTools: client ? normalizeMcpToolRows(client.available_tools || []) : (remoteMode ? [] : buildLocalToolRows(server)),
      secretSlots: client ? (Array.isArray(client.secret_slots) ? client.secret_slots : []) : (remoteMode ? [{ slot_name: "api_key", masked_value: "", has_value: false }] : buildLocalSecretSlots(server)),
    };

    if (refs.mcpModalTitle) refs.mcpModalTitle.textContent = client ? t("mcp_modal_edit") : t("mcp_modal_create");
    if (refs.mcpClientIdInput) refs.mcpClientIdInput.value = client?.client_id || (remoteMode ? "" : server?.server_id || "");
    if (refs.mcpClientNameInput) refs.mcpClientNameInput.value = client?.name || (remoteMode ? "" : server?.name || "");
    if (refs.mcpClientDescriptionInput) refs.mcpClientDescriptionInput.value = client?.description || (remoteMode ? "" : server?.description || "");
    if (refs.mcpClientEnabledInput) refs.mcpClientEnabledInput.checked = client ? Boolean(client.enabled) : true;
    if (refs.mcpClientModeSelect) refs.mcpClientModeSelect.value = remoteMode ? "remote" : "local";
    if (refs.mcpClientServerSelect && server) refs.mcpClientServerSelect.value = server.server_id || "";
    if (refs.mcpClientCommandInput) refs.mcpClientCommandInput.value = client?.command || "";
    if (refs.mcpClientArgsInput) refs.mcpClientArgsInput.value = serializeMcpArgs(client?.args || []);
    if (refs.mcpClientCwdInput) refs.mcpClientCwdInput.value = client?.cwd || "";
    if (refs.mcpClientEndpointInput) {
      refs.mcpClientEndpointInput.value = client?.endpoint || (remoteMode ? defaultRemoteEndpoint() : "");
    }
    if (refs.mcpClientIdInput) refs.mcpClientIdInput.disabled = Boolean(client);
    refs.mcpModal.classList.remove("hidden");
    refreshMcpEditorUi();
  }

  function closeMcpModal() {
    if (!refs.mcpModal) return;
    refs.mcpModal.classList.add("hidden");
    state.mcpEditor = null;
  }

  function readMcpPayload() {
    const mode = String(refs.mcpClientModeSelect?.value || "local").trim();
    const toolRows = currentMcpEditorTools();
    const payload = {
      client_id: String(refs.mcpClientIdInput?.value || "").trim(),
      original_client_id: String(state.mcpEditor?.editingId || "").trim(),
      name: String(refs.mcpClientNameInput?.value || "").trim(),
      description: String(refs.mcpClientDescriptionInput?.value || "").trim(),
      enabled: Boolean(refs.mcpClientEnabledInput?.checked),
      mode,
      transport: mode === "remote" ? "streamable_http" : "stdio",
      server_id: "",
      endpoint: "",
      command: "",
      args: [],
      cwd: "",
      enabled_tools: readSelectedMcpTools(toolRows),
      env: {},
      headers: {},
      metadata: {},
      secret_values: readMcpSecretValues(),
    };
    if (!payload.client_id) {
      throw new Error(t("mcp_error_client_id_required"));
    }
    if (mode === "local") {
      payload.server_id = String(refs.mcpClientServerSelect?.value || "").trim();
      payload.command = String(refs.mcpClientCommandInput?.value || "").trim();
      payload.args = parseMcpArgs(refs.mcpClientArgsInput?.value || "");
      payload.cwd = String(refs.mcpClientCwdInput?.value || "").trim();
      if (!payload.server_id && !payload.command) {
        throw new Error(t("mcp_error_server_id_required"));
      }
      if (payload.command) {
        payload.server_id = "";
      }
      return payload;
    }
    payload.endpoint = String(refs.mcpClientEndpointInput?.value || "").trim() || defaultRemoteEndpoint();
    if (!payload.endpoint) {
      throw new Error(t("mcp_error_endpoint_required"));
    }
    return payload;
  }

  function applyMcpPayload(data) {
    state.mcpDiscovered = data.discovered || [];
    state.mcpClients = data.clients || [];
    state.mcpActiveTools = data.active_tools || [];
    state.mcpChatGuard = data.chat_guard || { blocked: false, reason: "", client_ids: [] };
    renderMcp();
    updateChatInputGuard();
  }

  function renderMcp() {
    if (!refs.mcpSummary || !refs.mcpDiscoveredGrid || !refs.mcpClientsGrid) return;
    const discovered = Array.isArray(state.mcpDiscovered) ? state.mcpDiscovered : [];
    const clients = Array.isArray(state.mcpClients) ? state.mcpClients : [];
    const activeTools = Array.isArray(state.mcpActiveTools) ? state.mcpActiveTools : [];
    const enabledClients = clients.filter((item) => Boolean(item.enabled));
    const activeToolNames = activeTools.map((item) => String(item.tool_name || "").trim()).filter(Boolean);

    refs.mcpSummary.textContent =
      `${t("mcp_summary_discovered")}: ${discovered.length}\n` +
      `${t("mcp_summary_configured")}: ${clients.length}\n` +
      `${t("mcp_summary_enabled")}: ${enabledClients.length}\n` +
      `${t("mcp_summary_active_tools")}: ${activeToolNames.join(", ") || "-"}`;

    refs.mcpClientsGrid.innerHTML = "";
    if (!clients.length) {
      refs.mcpClientsGrid.textContent = t("mcp_empty_clients");
    } else {
      clients.forEach((client) => {
        const availableTools = normalizeMcpToolRows(client.available_tools || []);
        const selectedTools = availableTools.filter((item) => item.selected !== false).map((item) => item.name);
        const bindingNames = Array.isArray(client.active_tool_names) && client.active_tool_names.length
          ? client.active_tool_names
          : activeTools
              .filter((item) => String(item.client_id || "").trim() === String(client.client_id || "").trim())
              .map((item) => String(item.tool_name || "").trim())
              .filter(Boolean);
        const useLocalCommand = client.mode !== "remote" && !String(client.server_id || "").trim() && String(client.command || "").trim();
        const metaLabel = client.mode === "remote"
          ? t("mcp_field_endpoint")
          : useLocalCommand
            ? t("mcp_field_local_command")
            : t("mcp_label_server_id");
        const metaValue = client.mode === "remote"
          ? client.endpoint || "-"
          : useLocalCommand
            ? `${client.command || "-"} ${(Array.isArray(client.args) ? client.args.join(" ") : "").trim()}`.trim()
            : client.server_id || "-";
        const readiness = String(client.readiness_status || (client.enabled ? "ready" : "disabled")).trim();
          const stateBlocks = [];
          if (client.blocks_chat) stateBlocks.push({ title: zhen("Chat Guard", "Chat Guard"), body: localMcpChatGuardMessage() });
          if (client.server_available === false) stateBlocks.push({ title: zhen("Server", "Server"), body: client.server_availability_detail || "server_unavailable" });
          if (client.runtime_error) stateBlocks.push({ title: zhen("Runtime", "Runtime"), body: client.runtime_error });
          stateBlocks.push({ title: t("mcp_label_source"), body: `${mcpSourceText(client)} / ${String(client?.metadata?.managed_by || "-").trim() || "-"}` });
       const card = createResourceCard({
         baseClass: `mcp-card ${client.enabled ? "active" : "disabled"}`,
         title: mcpDisplayName(client),
        subtitle: client.client_id || "-",
        badgeText: mcpStatusText(readiness),
        badgeClass: mcpStatusToneClass(readiness),
        description: mcpDisplayDescription(client),
        metaItems: [
            { label: t("mcp_label_client_id"), value: client.client_id || "-" },
            { label: t("mcp_label_mode"), value: client.mode === "remote" ? t("mcp_mode_remote") : t("mcp_mode_local") },
            { label: metaLabel, value: metaValue, mono: client.mode === "remote" || useLocalCommand },
            { label: zhen("已选工具", "Selected tools"), value: selectedTools.join(", ") || zhen("全部", "all") },
          ],
          stateBlocks,
          actions: [
             { label: t("mcp_btn_edit"), className: "btn-secondary", onClick: async () => openMcpModal({ client }) },
             { label: client.enabled ? t("mcp_btn_disable") : t("mcp_btn_enable"), className: "btn-ghost", onClick: async () => toggleMcpClient(client.client_id || "", !client.enabled) },
           ].concat(String(client?.metadata?.source || "").trim() === "user"
             ? [{ label: t("btn_delete"), className: "btn-ghost", onClick: async () => deleteMcpClient(client.client_id || "") }]
             : []),
         });
        refs.mcpClientsGrid.appendChild(card);
      });
    }

    refs.mcpDiscoveredGrid.innerHTML = "";
    if (!discovered.length) {
      refs.mcpDiscoveredGrid.textContent = t("mcp_empty_discovered");
      return;
    }
    discovered.forEach((server) => {
      const linkedClients = clients.filter(
        (item) => String(item.mode || "").trim() === "local" && String(item.server_id || "").trim() === String(server.server_id || "").trim()
      );
      const preferredClient = linkedClients.find((item) => Boolean(item.enabled)) || linkedClients[0] || null;
      const displayRow = preferredClient || server;
      const enabled = linkedClients.some((item) => Boolean(item.enabled));
      const statusLabel = server.available === false
        ? "unavailable"
        : !linkedClients.length
          ? "available_unconfigured"
          : enabled
            ? "configured_enabled"
            : "configured_disabled";
      const stateBlocks = server.available === false
        ? [{ title: zhen("Server", "Server"), body: server.availability_detail || "server_unavailable" }]
        : [];
      const card = createResourceCard({
        baseClass: "mcp-card",
        title: mcpDisplayName(displayRow),
        subtitle: server.server_id || "-",
        badgeText: mcpStatusText(statusLabel),
        badgeClass: mcpStatusToneClass(statusLabel),
        description: mcpDisplayDescription(displayRow),
        metaItems: [
          { label: t("mcp_label_server_id"), value: server.server_id || "-" },
          { label: t("mcp_label_transport"), value: server.transport || "-" },
          {
            label: t("mcp_label_secrets"),
            value: server.requires_secrets
              ? (server.required_secrets || []).join(", ") || t("mcp_secret_required")
              : t("mcp_secret_none"),
          },
          { label: t("mcp_label_tools"), value: (server.tools || []).join(", ") || "-" },
        ],
        stateBlocks,
        actions: [{
          label: preferredClient ? t("mcp_btn_edit_config") : t("mcp_btn_create_local"),
          className: "btn-secondary",
          onClick: async () => openMcpModal(preferredClient ? { client: preferredClient } : { mode: "local", serverId: server.server_id || "" }),
        }],
      });
      refs.mcpDiscoveredGrid.appendChild(card);
    });
  }

  async function loadMcp() {
    const data = await api("/api/v1/mcp/sync", { method: "POST" });
    applyMcpPayload(data);
  }

  async function saveMcpClient() {
    const payload = readMcpPayload();
    const data = await api("/api/v1/mcp/clients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    closeMcpModal();
    applyMcpPayload(data);
  }

  async function toggleMcpClient(clientId, enabled) {
    const targetId = String(clientId || "").trim();
    if (!targetId) throw new Error("client_id is required");
    const data = await api(`/api/v1/mcp/clients/${encodeURIComponent(targetId)}/toggle`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: Boolean(enabled) }),
    });
    applyMcpPayload(data);
  }

  async function deleteMcpClient(clientId) {
    const targetId = String(clientId || "").trim();
    if (!targetId) throw new Error("client_id is required");
    const data = await api(`/api/v1/mcp/clients/${encodeURIComponent(targetId)}`, {
      method: "DELETE",
    });
    applyMcpPayload(data);
  }

  function renderSearchStatus() {
    if (!refs.searchStatusBox) return;
    const status = state.searchStatus;
    if (!status) {
      refs.searchStatusBox.textContent = `${t("search_status_ready")}: -`;
      return;
    }
    refs.searchStatusBox.textContent =
      `${t("search_status_ready")}: ${status.ready ? "yes" : "no"}\n` +
      `${t("search_status_indexing")}: ${status.indexing ? "yes" : "no"}\n` +
      `${t("search_status_last_index")}: ${status.last_indexed_at || "-"}\n` +
      `${t("search_status_chunks")}: ${status.chunks ?? 0}\n` +
      `${t("search_status_files")}: ${status.files ?? 0}\n` +
      `${t("search_status_embedder")}: ${status.embedder || "-"}\n` +
      `DB: ${status.db_path || "-"}`;
  }

  function markPreviewByQuery(preview, query) {
    const text = String(preview || "");
    const q = String(query || "").trim();
    if (!q) return esc(text);
    const tokens = [...new Set(q.split(/\s+/).map((x) => x.trim()).filter((x) => x.length >= 2))].slice(0, 8);
    if (!tokens.length) return esc(text);
    const pattern = new RegExp(`(${tokens.map((x) => escapeRegex(x)).join("|")})`, "ig");
    const marked = text.replace(pattern, "@@ANGEL_HL_START@@$1@@ANGEL_HL_END@@");
    return esc(marked)
      .replaceAll("@@ANGEL_HL_START@@", '<span class="search-hit-mark">')
      .replaceAll("@@ANGEL_HL_END@@", "</span>");
  }

  function renderSearchResults() {
    if (!refs.searchResults) return;
    refs.searchResults.innerHTML = "";
    if (state.searchLoading) {
      refs.searchResults.innerHTML = `<div class="search-empty">${esc(zhen("检索中...", "Searching..."))}</div>`;
      return;
    }
    const rows = state.searchResults || [];
    if (!rows.length) {
      refs.searchResults.innerHTML = `<div class="search-empty">${esc(t("search_no_results"))}</div>`;
      return;
    }

    rows.forEach((hit) => {
      const card = document.createElement("article");
      card.className = "search-hit";
      const score = Number(hit.score || 0).toFixed(4);
      const channel = String(hit.channel_prefix || "unknown");
      const matchedBy = Array.isArray(hit.matched_by) ? hit.matched_by.join(" + ") : "-";
      card.innerHTML = `
        <div class="search-hit-top">
          <h3 class="search-hit-title">${esc(hit.session_name || "-")}</h3>
          <span class="badge ${esc(channel)}">${esc(channel)}</span>
        </div>
        <div class="search-hit-meta">
          <span>${esc(hit.user_id || "-")}</span>
          <span>${esc(t("search_score"))}: ${esc(score)}</span>
          <span>match=${esc(matchedBy || "-")}</span>
        </div>
        <div class="search-hit-preview">${markPreviewByQuery(hit.preview || "", state.searchQuery)}</div>
      `;

      card.addEventListener("click", () => {
        openSearchHit(hit).catch((err) => showActionError(err));
      });

      refs.searchResults.appendChild(card);
    });
  }

  async function loadSearchStatus() {
    const data = await api("/api/v1/search/status");
    state.searchStatus = data.status || null;
    renderSearchStatus();
  }

  async function runSearch() {
    const q = String(refs.searchInput?.value || "").trim();
    if (!q) {
      state.searchQuery = "";
      state.searchResults = [];
      renderSearchResults();
      return;
    }

    const limitRaw = Number(refs.searchLimitInput?.value || 20);
    const limit = Number.isFinite(limitRaw) ? Math.max(1, Math.min(100, Math.round(limitRaw))) : 20;
    const channel = String(refs.searchChannelFilter?.value || "").trim();

    state.searchQuery = q;
    state.searchLoading = true;
    renderSearchResults();
    const qs = new URLSearchParams({ q, limit: String(limit) });
    if (channel) qs.set("channel", channel);

    try {
      const data = await api(`/api/v1/search/sessions?${qs.toString()}`);
      const result = data.result || {};
      state.searchResults = Array.isArray(result.session_hits) ? result.session_hits : [];
    } finally {
      state.searchLoading = false;
      renderSearchResults();
    }
  }

  async function reindexSearch() {
    state.searchLoading = true;
    renderSearchResults();
    try {
      await api("/api/v1/search/reindex", { method: "POST" });
      await loadSearchStatus();
      await runSearch();
    } finally {
      state.searchLoading = false;
      renderSearchResults();
    }
  }

  async function openSearchHit(hit) {
    if (!hit) return;
    const target = {
      user_id: hit.user_id,
      session_name: hit.session_name,
      channel_prefix: hit.channel_prefix || "unknown",
    };
    setView("chat");
    await loadSessions(false);
    await selectSession(target);
  }

  function toLocalInputValue(unixTs) {
    const ts = Number(unixTs || 0);
    if (!Number.isFinite(ts) || ts <= 0) return "";
    const d = new Date(ts * 1000);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function fromLocalInputValue(value, fallback = 0, endOfMinute = false) {
    const text = String(value || "").trim();
    if (!text) return fallback;
    const ms = Date.parse(text);
    if (!Number.isFinite(ms)) return fallback;
    const base = Math.floor(ms / 1000);
    // datetime-local is often minute-precision (YYYY-MM-DDTHH:mm).
    // For end bounds, include the whole minute to avoid excluding recent records.
    if (endOfMinute && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(text)) {
      return base + 59;
    }
    return base;
  }

  function formatNum(value) {
    const n = Number(value || 0);
    const locale = state.lang === "zh" ? "zh-CN" : "en-US";
    return new Intl.NumberFormat(locale).format(Number.isFinite(n) ? n : 0);
  }

  function formatTs(ts) {
    const n = Number(ts || 0);
    if (!Number.isFinite(n) || n <= 0) return "-";
    return new Date(n * 1000).toLocaleString(state.lang === "zh" ? "zh-CN" : "en-US");
  }

  function applyBillingQuickRange(rangeValue) {
    const key = String(rangeValue || refs.billingQuickRange?.value || "12h");
    const now = Math.floor(Date.now() / 1000);
    let fromTs = now - 12 * 3600;
    if (key === "24h") fromTs = now - 24 * 3600;
    if (key === "7d") fromTs = now - 7 * 24 * 3600;
    if (key === "30d") fromTs = now - 30 * 24 * 3600;
    if (key === "custom") return;
    refs.billingFromInput.value = toLocalInputValue(fromTs);
    refs.billingToInput.value = toLocalInputValue(now);
  }

  function shouldAutoShiftBillingWindow() {
    const key = String(refs.billingQuickRange?.value || "12h").trim().toLowerCase();
    return key !== "custom";
  }

  function readBillingFilters(resetPage = false) {
    let fromTs = 0;
    let toTs = 0;
    const now = Math.floor(Date.now() / 1000);

    if (shouldAutoShiftBillingWindow()) {
      const key = String(refs.billingQuickRange?.value || "12h").trim().toLowerCase();
      let span = 12 * 3600;
      if (key === "24h") span = 24 * 3600;
      if (key === "7d") span = 7 * 24 * 3600;
      if (key === "30d") span = 30 * 24 * 3600;
      fromTs = now - span;
      toTs = now;
      // Keep UI fields in sync (display only; true query window remains second-precision).
      refs.billingFromInput.value = toLocalInputValue(fromTs);
      refs.billingToInput.value = toLocalInputValue(toTs);
    } else {
      const defaultFrom = now - 12 * 3600;
      fromTs = fromLocalInputValue(refs.billingFromInput?.value, defaultFrom, false);
      toTs = fromLocalInputValue(refs.billingToInput?.value, now, true);
    }

    state.billingFilters = {
      from_ts: Math.min(fromTs, toTs),
      to_ts: Math.max(fromTs, toTs),
      status: String(refs.billingStatusSelect?.value || "all").trim() || "all",
    };
    if (resetPage) state.billingPage = 1;
    return state.billingFilters;
  }

  function stopBillingAutoRefresh() {
    if (state.billingAutoRefreshTimer) {
      clearInterval(state.billingAutoRefreshTimer);
      state.billingAutoRefreshTimer = null;
    }
  }

  function startBillingAutoRefresh() {
    stopBillingAutoRefresh();
    if (state.view !== "billing") return;
    state.billingAutoRefreshTimer = setInterval(() => {
      if (state.view !== "billing") return;
      reloadBilling(false).catch((err) => {
        console.warn("billing auto refresh failed", err);
      });
    }, Number(state.billingAutoRefreshMs || 10000));
  }

  function billingQueryParams(withPaging = false) {
    const f = state.billingFilters || {};
    const qs = new URLSearchParams({
      from_ts: String(f.from_ts || 0),
      to_ts: String(f.to_ts || 0),
      status: String(f.status || "all"),
    });
    if (withPaging) {
      qs.set("page", String(state.billingPage || 1));
      qs.set("page_size", "20");
    }
    return qs;
  }

  function renderBillingStatus() {
    if (!refs.billingStatusBox) return;
    const row = state.billingStatus;
    if (!row) {
      refs.billingStatusBox.textContent = `${t("billing_status_box")}: -`;
      return;
    }
    refs.billingStatusBox.textContent =
      `${t("billing_status_box")}: ${row.log_dir || "-"}\n` +
      `${zhen("可读天数", "Readable Days")}: ${formatNum(row.readable_days || 0)}\n` +
      `${zhen("总记录数", "Total Records")}: ${formatNum(row.total_records || 0)}\n` +
      `${zhen("最近写入", "Last Write")}: ${formatTs(row.last_write_at || 0)}\n` +
      `${zhen("写入错误", "Writer Errors")}: ${formatNum(row.writer_errors || 0)}`;
  }

  function renderBillingOverview() {
    const overviewNode = state.billingOverview || {};
    const row = overviewNode.overview || {};

    if (refs.billingTotalCalls) refs.billingTotalCalls.textContent = formatNum(row.total_calls || 0);
    if (refs.billingSuccessCalls) refs.billingSuccessCalls.textContent = formatNum(row.success_calls || 0);
    if (refs.billingFailedCalls) refs.billingFailedCalls.textContent = formatNum(row.failed_calls || 0);
    if (refs.billingFailureRate) refs.billingFailureRate.textContent = `${Number(row.failure_rate || 0).toFixed(2)}%`;
    if (refs.billingPromptTokens) refs.billingPromptTokens.textContent = formatNum(row.prompt_tokens_total || 0);
    if (refs.billingCompletionTokens) refs.billingCompletionTokens.textContent = formatNum(row.completion_tokens_total || 0);
    if (refs.billingTokensTotal) refs.billingTokensTotal.textContent = formatNum(row.tokens_total || 0);
    if (refs.billingP95Latency) refs.billingP95Latency.textContent = `${formatNum(row.p95_latency_ms || 0)}ms`;
  }

  function renderBillingCalls() {
    if (!refs.billingCallsTable) return;
    refs.billingCallsTable.innerHTML = "";
    const rows = Array.isArray(state.billingCalls) ? state.billingCalls : [];
    const totalPages = Math.max(1, Math.ceil((state.billingTotal || 0) / 20));
    const currentPage = Math.max(1, Math.min(totalPages, Number(state.billingPage || 1)));
    state.billingPage = currentPage;
    state.billingPageSize = 20;
    if (!rows.length) {
      refs.billingCallsTable.innerHTML = `
        <div class="billing-empty-state">
          <div class="billing-empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
            </svg>
          </div>
          <div class="billing-empty-text">${esc(t("billing_no_data"))}</div>
          <div class="billing-empty-hint">Try adjusting your filters or time range</div>
        </div>
      `;
      if (refs.billingPageInfo) refs.billingPageInfo.textContent = `1 / 1`;
      if (refs.billingPrevBtn) refs.billingPrevBtn.disabled = true;
      if (refs.billingNextBtn) refs.billingNextBtn.disabled = true;
      return;
    }

    rows.forEach((row) => {
      const node = document.createElement("div");
      node.className = "billing-row";
      const ok = Boolean(row.success);
      node.innerHTML = `
        <div class="billing-row-top">
          <div class="billing-row-title">${esc(row.provider || "-")} / ${esc(row.model || "-")}</div>
          <span class="billing-status-pill ${ok ? "success" : "failed"}">${esc(ok ? t("billing_status_success") : t("billing_status_failed"))}</span>
        </div>
        <div class="billing-row-meta">
          <span>id=${esc(row.call_id || "-")}</span>
          <span>${formatTs(row.started_at)}</span>
          <span>lat=${esc(row.latency_ms || 0)}ms</span>
          <span>tokens=${esc(row.total_tokens || 0)}</span>
          <span>prompt=${esc(row.prompt_tokens || 0)}</span>
          <span>completion=${esc(row.completion_tokens || 0)}</span>
          <span>src=${esc(row.usage_source || "-")}</span>
          <span>profile=${esc(row.profile_id || "-")}</span>
        </div>
        <div class="billing-row-preview">${esc(row.input_preview || row.error_message || "")}</div>
      `;
      node.addEventListener("click", () => {
        openBillingDetail(row.call_id).catch((err) => showActionError(err));
      });
      refs.billingCallsTable.appendChild(node);
    });

    if (refs.billingPageInfo) refs.billingPageInfo.textContent = `${currentPage} / ${totalPages}`;
    if (refs.billingPrevBtn) refs.billingPrevBtn.disabled = currentPage <= 1;
    if (refs.billingNextBtn) refs.billingNextBtn.disabled = currentPage >= totalPages;
  }

  async function loadBillingStatus() {
    const data = await api("/api/v1/billing/status");
    state.billingStatus = data.status || null;
    renderBillingStatus();
  }

  async function loadBillingOverview() {
    const qs = billingQueryParams(false);
    const data = await api(`/api/v1/billing/overview?${qs.toString()}`);
    state.billingOverview = data.result || null;
    renderBillingOverview();
  }

  async function loadBillingCalls() {
    const qs = billingQueryParams(true);
    const data = await api(`/api/v1/billing/calls?${qs.toString()}`);
    const result = data.result || {};
    state.billingCalls = Array.isArray(result.items) ? result.items.slice(0, 20) : [];
    state.billingTotal = Number(result.total || 0);
    state.billingPage = Math.max(1, Number(result.page || state.billingPage || 1));
    state.billingPageSize = 20;
    renderBillingCalls();
  }

  async function reloadBilling(resetPage = false) {
    readBillingFilters(resetPage);
    await loadBillingStatus();
    await loadBillingOverview();
    await loadBillingCalls();
  }

  async function openBillingDetail(callId) {
    const cid = String(callId || "").trim();
    if (!cid) return;
    const data = await api(`/api/v1/billing/calls/${encodeURIComponent(cid)}`);
    const detail = data.detail || {};
    if (refs.billingDetailPre) {
      refs.billingDetailPre.textContent = JSON.stringify(detail, null, 2);
    }
    refs.billingDetailModal.classList.remove("hidden");
  }

  function closeBillingDetail() {
    if (!refs.billingDetailModal) return;
    refs.billingDetailModal.classList.add("hidden");
  }

  const getProfiles = () => (state.modelState && state.modelState.profiles) || [];
  const getModelTypes = () => (state.modelState && state.modelState.model_types) || [];
  const getSelectedModelType = () => String(state.selectedModelType || "text_generation").trim() || "text_generation";
  const getSelectedModelTypeRow = () => getModelTypes().find((row) => row.model_type === getSelectedModelType()) || null;
  const getProfilesForModelType = (modelType) => getProfiles().filter((row) => String(row.model_type || "").trim() === String(modelType || "").trim());
  const getProviderCatalog = () => (state.modelState && state.modelState.providers) || [];
  const getProvidersForModelType = (modelType) => getProviderCatalog().filter((row) => {
    const supported = Array.isArray(row.supports) ? row.supports : [];
    return supported.includes(String(modelType || "").trim());
  });
  const getProviderPreset = (providerName) => getProviderCatalog().find((row) => row.provider === providerName) || null;
  const modelTypeLabel = (modelType) => {
    const labels = {
      text_generation: zhen("文本生成", "Text Generation"),
      vision: zhen("视觉理解", "Vision"),
      image_generation: zhen("图片生成", "Image Generation"),
      video_generation: zhen("视频生成", "Video Generation"),
      speech_to_text: zhen("语音识别", "Speech to Text"),
      text_to_speech: zhen("语音合成", "Text to Speech"),
      multimodal_embedding: zhen("多模态向量", "Multimodal Embedding"),
      text_embedding: zhen("文本向量", "Text Embedding"),
    };
    return labels[String(modelType || "").trim()] || String(modelType || "").trim() || "-";
  };

  const parseOptionalNumber = (raw, fieldName) => {
    const text = String(raw || "").trim();
    if (!text) return null;
    const value = Number(text);
    if (Number.isNaN(value)) throw new Error(`${fieldName} must be a number`);
    return value;
  };

  const randomCode = (length = 8) => {
    const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
    const n = Math.max(4, Number(length) || 8);
    if (typeof window !== "undefined" && window.crypto && window.crypto.getRandomValues) {
      const bytes = new Uint8Array(n);
      window.crypto.getRandomValues(bytes);
      return Array.from(bytes)
        .map((b) => chars[b % chars.length])
        .join("");
    }
    let out = "";
    for (let i = 0; i < n; i += 1) {
      out += chars[Math.floor(Math.random() * chars.length)];
    }
    return out;
  };

  const buildDefaultProfileId = () => `default_${randomCode(8)}`;

  function resetModelModal(profile = null) {
    const modelType = String(profile?.model_type || getSelectedModelType()).trim() || "text_generation";
    state.modelEditor = profile
      ? { editingId: String(profile.profile_id || "").trim(), modelType }
      : { editingId: "", modelType };
    renderModelTypeSelect(modelType);
    refs.modelProfileIdInput.value = profile?.profile_id || buildDefaultProfileId();
    refs.modelApiKeyInput.value = "";
    refs.modelClearApiKeyInput.checked = false;
    refs.modelMaxTokensInput.value = "";
    refs.modelTimeoutInput.value = "";
    refs.modelTemperatureInput.value = "";
    refs.modelTopPInput.value = "";
    renderModelProviderSelect(modelType, profile?.provider || "");
    if (profile) {
      refs.modelProviderSelect.value = profile.provider || "";
      refs.modelBaseUrlInput.value = profile.base_url || "";
      refs.modelNameInput.value = profile.model || "";
      refs.modelMaxTokensInput.value = profile.max_tokens ?? "";
      refs.modelTimeoutInput.value = profile.timeout ?? "";
      refs.modelTemperatureInput.value = profile.temperature ?? "";
      refs.modelTopPInput.value = profile.top_p ?? "";
    } else {
      const first = getProvidersForModelType(modelType)[0];
      if (first) {
        refs.modelProviderSelect.value = first.provider;
        applyProviderPreset(first.provider, true, modelType);
      } else {
        refs.modelBaseUrlInput.value = "";
        refs.modelNameInput.value = "";
      }
    }
    refs.modelProfileIdInput.disabled = Boolean(profile);
    if (refs.modelClearApiKeyInput) {
      refs.modelClearApiKeyInput.disabled = !profile;
    }
    refreshModelModalText();
  }

  function openModelModal(profile = null) {
    resetModelModal(profile);
    refs.modelModal.classList.remove("hidden");
  }

  function closeModelModal() {
    refs.modelModal.classList.add("hidden");
    state.modelEditor = null;
  }

  function refreshModelModalText() {
    const editing = Boolean(state.modelEditor && state.modelEditor.editingId);
    const modelType = String(state.modelEditor?.modelType || getSelectedModelType()).trim() || "text_generation";
    const typeLabel = modelTypeLabel(modelType);
    refs.modelModalTitle.textContent = editing
      ? zhen(`编辑${typeLabel}`, `Edit ${typeLabel}`)
      : zhen(`新建${typeLabel}`, `Create ${typeLabel}`);
    refs.closeModelModalBtn.setAttribute("aria-label", zhen("关闭侧边栏", "Close drawer"));
    refs.closeModelModalBtn.setAttribute("title", zhen("关闭侧边栏", "Close drawer"));
    if (refs.modelApiKeyInput) {
      const hint = editing ? zhen("已配置，留空不改", "configured, blank keeps current") : t("api_key_placeholder");
      refs.modelApiKeyInput.setAttribute("placeholder", hint);
    }
  }

  function renderModelTypeSelect(selectedType) {
    if (!refs.modelTypeSelect) return;
    const types = getModelTypes();
    refs.modelTypeSelect.innerHTML = "";
    types.forEach((row) => {
      const opt = document.createElement("option");
      opt.value = row.model_type || "";
      opt.textContent = modelTypeLabel(row.model_type);
      refs.modelTypeSelect.appendChild(opt);
    });
    if (selectedType && types.some((row) => row.model_type === selectedType)) {
      refs.modelTypeSelect.value = selectedType;
    } else if (types.length) {
      refs.modelTypeSelect.value = types[0].model_type || "text_generation";
    }
  }

  function renderModelProviderSelect(modelType, selected) {
    const providers = getProvidersForModelType(modelType);
    refs.modelProviderSelect.innerHTML = "";
    providers.forEach((row) => {
      const opt = document.createElement("option");
      opt.value = row.provider;
      opt.textContent = providerDisplayName(row.provider, row.display_name || row.provider);
      refs.modelProviderSelect.appendChild(opt);
    });
    if (selected && providers.some((p) => p.provider === selected)) {
      refs.modelProviderSelect.value = selected;
    } else if (providers.length) {
      refs.modelProviderSelect.value = providers[0].provider;
    }
  }

  function applyProviderPreset(providerName, forceFill = false, modelType = "") {
    const preset = getProviderPreset(providerName);
    if (!preset) return;
    const isCustom = Boolean(preset.is_custom);
    const presetBase = isCustom ? "" : preset.default_base_url || "";
    const typedModel = preset.default_models && modelType ? preset.default_models[modelType] : "";
    const presetModel = typedModel || preset.default_model || "";

    if (forceFill || !refs.modelBaseUrlInput.value.trim() || isCustom) {
      refs.modelBaseUrlInput.value = presetBase;
    }
    if (forceFill || !refs.modelNameInput.value.trim()) {
      refs.modelNameInput.value = presetModel;
    }
  }

  const connectivityClass = (status) => {
    if (status === "success") return "test-success";
    if (status === "failed") return "test-failed";
    return "";
  };

  const modelConnectivityLabel = (status) => {
    if (status === "success") return zhen("\u8fde\u901a\u6027\u5df2\u9a8c\u8bc1", "Connectivity Verified");
    if (status === "failed") return zhen("\u8fde\u901a\u6027\u9a8c\u8bc1\u5931\u8d25", "Connectivity Check Failed");
    return zhen("\u672a\u9a8c\u8bc1\u8fde\u901a\u6027", "Connectivity Not Verified");
  };

  const modelRoleLabel = (isActive) => (isActive
    ? zhen("\u5de5\u4f5c\u4e2d", "Active")
    : zhen("\u53ef\u5207\u6362", "Ready"));

  const modelDisplayValue = (value) => {
    if (value === null || value === undefined) return "-";
    const text = String(value).trim();
    return text || "-";
  };

  function createModelFacts(fields, extraClass = "") {
    const list = document.createElement("div");
    list.className = `model-facts${extraClass ? ` ${extraClass}` : ""}`;

    fields.forEach((field) => {
      const row = document.createElement("div");
      row.className = "model-fact";

      const label = document.createElement("span");
      label.className = "model-fact-label";
      label.textContent = field.label;

      const value = document.createElement("span");
      value.className = `model-fact-value${field.mono ? " mono" : ""}`;
      const displayValue = modelDisplayValue(field.value);
      value.textContent = displayValue;
      if (displayValue !== "-") value.title = displayValue;

      row.appendChild(label);
      row.appendChild(value);
      list.appendChild(row);
    });

    return list;
  }

  function createResourceMeta(items = []) {
    const meta = document.createElement("div");
    meta.className = "resource-meta";
    items.forEach((item) => {
      const entry = document.createElement("div");
      entry.className = "resource-meta__item";

      const label = document.createElement("div");
      label.className = "resource-meta__label";
      label.textContent = item.label || "-";

      const value = document.createElement("div");
      value.className = `resource-meta__value${item.mono ? " mono" : ""}`;
      const displayValue = modelDisplayValue(item.value);
      value.textContent = displayValue;
      if (displayValue !== "-") value.title = displayValue;

      entry.appendChild(label);
      entry.appendChild(value);
      meta.appendChild(entry);
    });
    return meta;
  }

  function createResourceCard(options) {
    const {
      baseClass = "",
      title = "-",
      subtitle = "",
      badgeText = "",
      badgeClass = "",
      description = "",
      metaItems = [],
      actions = [],
      onCardClick = null,
      stateBlocks = [],
    } = options || {};

    const card = document.createElement("article");
    card.className = `resource-card${baseClass ? ` ${baseClass}` : ""}`;
    if (typeof onCardClick === "function") {
      card.addEventListener("click", onCardClick);
    }

    const main = document.createElement("div");
    main.className = "resource-main";

    const top = document.createElement("div");
    top.className = "resource-top";

    const titleWrap = document.createElement("div");
    titleWrap.className = "resource-title-wrap";

    const titleNode = document.createElement("h3");
    titleNode.className = "resource-title";
    titleNode.textContent = title;
    titleNode.title = title;

    const subNode = document.createElement("div");
    subNode.className = "resource-sub";
    subNode.textContent = description || subtitle || "-";
    subNode.title = description || subtitle || "-";

    titleWrap.appendChild(titleNode);
    titleWrap.appendChild(subNode);
    top.appendChild(titleWrap);

    if (badgeText) {
      const badge = document.createElement("span");
      badge.className = `badge ${badgeClass || ""}`.trim();
      badge.textContent = badgeText;
      top.appendChild(badge);
    }

    main.appendChild(top);
    main.appendChild(createResourceMeta(metaItems));

    (Array.isArray(stateBlocks) ? stateBlocks : []).forEach((block) => {
      const node = document.createElement("div");
      node.className = `list-row${block.tone ? ` ${block.tone}` : ""}`;
      const titleRow = document.createElement("div");
      titleRow.className = "list-row__title";
      titleRow.innerHTML = `<span>${esc(block.title || "-")}</span>`;
      const desc = document.createElement("div");
      desc.className = "list-row__desc";
      desc.textContent = block.body || "-";
      node.appendChild(titleRow);
      node.appendChild(desc);
      main.appendChild(node);
    });

    card.appendChild(main);

    if (actions.length) {
      const footer = document.createElement("div");
      footer.className = "resource-footer";
      actions.forEach((action, index) => {
        const btn = document.createElement("button");
        btn.className = action.className || (index === 0 ? "btn-secondary" : "btn-ghost");
        btn.textContent = action.label;
        if (action.disabled) btn.disabled = true;
        if (typeof action.onClick === "function") {
          btn.addEventListener("click", (event) => {
            event.stopPropagation();
            action.onClick(event);
          });
        }
        footer.appendChild(btn);
      });
      card.appendChild(footer);
    }

    return card;
  }

  function renderModelRuntimeState(modelState, runtime) {
    refs.modelRuntimeState.innerHTML = "";
    if (!Object.keys(runtime || {}).length) {
      refs.modelRuntimeState.textContent = t("runtime_empty");
      return;
    }

    const summary = document.createElement("div");
    summary.className = "model-runtime-summary";

    const current = document.createElement("div");
    current.className = "model-runtime-current";

    const currentLabel = document.createElement("span");
    currentLabel.className = "model-runtime-current-label";
    currentLabel.textContent = zhen("\u5f53\u524d\u6a21\u578b\u7c7b\u578b", "Active Model Type");

    const currentValue = document.createElement("strong");
    currentValue.className = "model-runtime-current-value";
    const activeProfileId = modelDisplayValue(runtime.profile_id || runtime.active_profile_id || modelState.active_profiles?.[getSelectedModelType()] || "");
    currentValue.textContent = `${modelTypeLabel(getSelectedModelType())} / ${activeProfileId}`;
    currentValue.title = currentValue.textContent;

    current.appendChild(currentLabel);
    current.appendChild(currentValue);
    summary.appendChild(current);

    summary.appendChild(createModelFacts([
      { label: t("runtime_provider"), value: providerDisplayName(runtime.provider, runtime.provider || "-") },
      { label: t("runtime_model"), value: runtime.model },
      { label: t("runtime_base_url"), value: runtime.base_url, mono: true },
      { label: t("field_temperature"), value: runtime.temperature },
      { label: t("field_top_p"), value: runtime.top_p },
    ], "runtime-facts"));

    refs.modelRuntimeState.appendChild(summary);
  }

  function renderModelTypeGrid() {
    if (!refs.modelTypeGrid) return;
    refs.modelTypeGrid.innerHTML = "";
    const types = getModelTypes();
    const fragment = document.createDocumentFragment();
    types.forEach((row) => {
      const selected = row.model_type === getSelectedModelType();
      const unavailable = row.available === false;
      const card = createResourceCard({
        baseClass: `profile-card model-type-card${selected ? " active" : ""}${unavailable ? " unavailable" : ""}`,
        title: modelTypeLabel(row.model_type),
        subtitle: row.active_profile_id || zhen("未激活", "No Active Profile"),
        badgeText: unavailable ? zhen("未就绪", "Unavailable") : zhen("可用", "Available"),
        badgeClass: unavailable ? "warn" : "ok",
        description: row.availability_detail || zhen("按模型类型统一管理 profiles 与运行态。", "Profiles and runtime are grouped by model type."),
        metaItems: [
          { label: zhen("档案数", "Profiles"), value: row.profile_count ?? 0 },
          { label: zhen("已授权", "Authorized"), value: row.authorized ? zhen("是", "Yes") : zhen("否", "No") },
          { label: zhen("运行状态", "Runtime"), value: row.availability_detail || "-" },
          { label: zhen("类型标识", "Type Key"), value: row.model_type || "-", mono: true },
        ],
      });
      card.addEventListener("click", () => {
        state.selectedModelType = row.model_type || "text_generation";
        renderModels();
      });
      fragment.appendChild(card);
    });
    refs.modelTypeGrid.appendChild(fragment);
  }

  function buildModelProfileCard(profile) {
    const status = profile.connectivity_status || "untested";
    const statusText = modelConnectivityLabel(status);
    const statusClass = connectivityClass(status);
    const statusTip = String(profile.connectivity_detail || "").trim() || statusText;
    const profileId = modelDisplayValue(profile.profile_id);
    return createResourceCard({
      baseClass: `profile-card${profile.active ? " active" : ""}`,
      title: profileId,
      subtitle: modelRoleLabel(profile.active),
      badgeText: statusText,
      badgeClass: statusClass,
      description: statusTip,
      metaItems: [
        { label: zhen("模型类型", "Model Type"), value: modelTypeLabel(profile.model_type) },
        { label: t("field_provider"), value: providerDisplayName(profile.provider, profile.provider || "-") },
        { label: t("field_model_name"), value: profile.model, mono: true },
        { label: t("field_base_url"), value: profile.base_url, mono: true },
      ],
      actions: [
        { label: t("btn_edit"), className: "btn-secondary", onClick: () => openModelModal(profile) },
        { label: t("btn_activate"), className: "btn-ghost", disabled: Boolean(profile.active), onClick: async () => {
          if (profile.active) return;
          await activateModelProfile(profile.profile_id, profile.model_type);
        } },
        { label: zhen("\u6d4b\u8bd5\u8fde\u901a\u6027", "Test Connectivity"), className: "btn-ghost", onClick: async () => {
          await testModelProfile(profile.profile_id, profile.model_type);
        } },
        { label: t("btn_delete"), className: "btn-ghost", onClick: async () => {
          await deleteModelProfile(profile.profile_id, profile.model_type);
        } },
      ],
    });
  }

  function renderModels() {
    const modelState = state.modelState || { providers: [], profiles: [], runtime: {}, model_types: [] };
    const types = modelState.model_types || [];
    if (types.length && !types.some((row) => row.model_type === getSelectedModelType())) {
      state.selectedModelType = types[0].model_type || "text_generation";
    }
    const profiles = getProfilesForModelType(getSelectedModelType());
    const runtime = (modelState.runtime || {})[getSelectedModelType()] || {};

    renderModelTypeGrid();
    renderModelProviderSelect(state.modelEditor?.modelType || getSelectedModelType(), refs.modelProviderSelect.value);
    refreshModelModalText();
    renderModelRuntimeState(modelState, runtime);

    refs.modelProfilesGrid.innerHTML = "";
    if (!profiles.length) {
      refs.modelProfilesGrid.textContent = t("no_profiles");
      return;
    }

    const fragment = document.createDocumentFragment();
    profiles.forEach((profile) => {
      fragment.appendChild(buildModelProfileCard(profile));
    });
    refs.modelProfilesGrid.appendChild(fragment);
  }

  async function loadModels() {
    state.modelState = await api("/api/v1/models/state");
    renderModels();
  }

  function readModelPayload() {
    const profileId = refs.modelProfileIdInput.value.trim();
    if (!profileId) throw new Error("profile_id required");
    const editing = Boolean(state.modelEditor && state.modelEditor.editingId);
    const modelType = String(refs.modelTypeSelect?.value || state.modelEditor?.modelType || getSelectedModelType()).trim() || "text_generation";

    const provider = refs.modelProviderSelect.value.trim() || "openai";
    const preset = getProviderPreset(provider);
    const isCustom = Boolean(preset && preset.is_custom);

    const base = refs.modelBaseUrlInput.value.trim() || (isCustom ? "" : (preset && preset.default_base_url) || "");
    if (!base) throw new Error("base_url required");

    const modelName = refs.modelNameInput.value.trim() || (preset && preset.default_model) || "";
    if (!modelName) throw new Error("model required");
    const apiKey = refs.modelApiKeyInput.value.trim();
    const clearApiKey = Boolean(refs.modelClearApiKeyInput?.checked);
    if (!apiKey && !editing && !clearApiKey) throw new Error("api_key required");

    const temperature = parseOptionalNumber(refs.modelTemperatureInput.value, "temperature");
    const topP = parseOptionalNumber(refs.modelTopPInput.value, "top_p");
    if (topP != null && (topP <= 0 || topP > 1)) throw new Error("top_p must be > 0 and <= 1");

    return {
      profile_id: profileId,
      model_type: modelType,
      provider,
      base_url: base,
      model: modelName,
      api_key: apiKey,
      max_tokens: parseOptionalNumber(refs.modelMaxTokensInput.value, "max_tokens"),
      timeout: parseOptionalNumber(refs.modelTimeoutInput.value, "timeout"),
      temperature,
      top_p: topP,
      clear_api_key: clearApiKey,
    };
  }

  async function saveModelProfile() {
    const payload = readModelPayload();
    state.modelState = await api("/api/v1/models/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.modelProfileId = payload.profile_id;
    closeModelModal();
    renderModels();
  }

  async function activateModelProfile(profileId, modelType = "") {
    const pid = (profileId || "").trim();
    if (!pid) throw new Error("profile_id required");
    state.modelState = await api("/api/v1/models/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile_id: pid, model_type: modelType || getSelectedModelType() }),
    });
    state.modelProfileId = pid;
    renderModels();
  }

  async function deleteModelProfile(profileId, modelType = "") {
    const pid = (profileId || "").trim();
    if (!pid) throw new Error("profile_id required");
    const typeName = encodeURIComponent(modelType || getSelectedModelType());
    state.modelState = await api(`/api/v1/models/profiles/${encodeURIComponent(pid)}?model_type=${typeName}`, { method: "DELETE" });
    if (state.modelProfileId === pid) state.modelProfileId = "";
    renderModels();
  }

  async function testModelProfile(profileId, modelType = "") {
    const pid = (profileId || "").trim();
    if (!pid) throw new Error("profile_id required");
    const typeName = encodeURIComponent(modelType || getSelectedModelType());
    state.modelState = await api(`/api/v1/models/profiles/${encodeURIComponent(pid)}/test?model_type=${typeName}`, { method: "POST" });
    renderModels();
  }

  // Channel runtime v2: config state + runtime state + start/stop/restart operations.
  function channelStatusText(row) {
    if (!row || !row.enabled) return zhen("已禁用", "Disabled");
    if (row.configured) return zhen("已配置", "Configured");
    return zhen("配置不完整", "Config Incomplete");
  }

  function channelStatusClass(row) {
    if (!row || !row.enabled) return "disabled";
    if (row.configured) return "enabled";
    return "error";
  }

  function channelRuntimeStatusText(row) {
    const runtime = row?.runtime || {};
    const status = String(runtime.status || "").trim().toLowerCase();
    if (runtime.running) return zhen("运行中", "Running");
    if (status === "failed") return zhen("启动失败", "Start Failed");
    if (status === "manual") return zhen("仅手动运行", "Manual Only");
    return zhen("未启动", "Not Running");
  }

  function channelRuntimeStatusClass(row) {
    const runtime = row?.runtime || {};
    const status = String(runtime.status || "").trim().toLowerCase();
    if (runtime.running) return "enabled";
    if (status === "failed") return "error";
    return "disabled";
  }

  function summarizeChannel(row) {
    if (!row) return "-";
    const settings = {};
    (row.fields || []).forEach((field) => {
      settings[field.key] = field.secret ? (field.has_value ? "****" : "") : String(field.value || "");
    });
    if (row.name === "web") return settings.base_url || row.launch_command || "-";
    if (row.name === "cli") return settings.command || row.launch_command || "-";
    if (row.name === "qq") return settings.app_id ? `app_id=${settings.app_id}` : row.launch_command || "-";
    if (row.name === "discord") {
      if (settings.guild_id) return `guild_id=${settings.guild_id}`;
      if (settings.http_proxy) return `proxy=${settings.http_proxy}`;
      return row.launch_command || "-";
    }
    return row.launch_command || "-";
  }

  function channelConfigDetail(row) {
    if (!row) return "";
    if (row.enabled && !row.configured) return channelRequiredHint(row.missing_required || []);
    if (row.bot_prefix) return `prefix=${row.bot_prefix}`;
    return row.launch_command || "";
  }

  function channelRuntimeDetail(row) {
    const runtime = row?.runtime || {};
    if (runtime.running) {
      return runtime.pid ? `pid=${runtime.pid}` : zhen("进程运行中", "Process running");
    }
    if (runtime.status === "failed") {
      return String(runtime.last_error || zhen("启动失败，请查看日志", "Start failed, check logs"));
    }
    if (runtime.status === "manual") {
      return zhen("该频道仅支持手动启动。", "Manual-only channel.");
    }
    return zhen("当前未启动。", "Channel is not running.");
  }

  function channelDrawerSummary(row) {
    if (!row) return "";
    const lines = [
      `${zhen("配置状态", "Config")}: ${channelStatusText(row)}`,
      `${zhen("运行状态", "Runtime")}: ${channelRuntimeStatusText(row)}`,
    ];
    const configDetail = channelConfigDetail(row);
    if (configDetail) lines.push(configDetail);
    const runtimeDetail = channelRuntimeDetail(row);
    if (runtimeDetail) lines.push(runtimeDetail);
    if (row.launch_command) lines.push(`${zhen("启动命令", "Launch")}: ${row.launch_command}`);
    return lines.filter(Boolean).join("\n");
  }

  function applyChannelsState(response, keepDrawer = false) {
    state.channels = (response && response.channels) || [];
    renderChannels();
    if (keepDrawer && state.channelEditor && state.channelEditor.name) {
      openChannelDrawer(state.channelEditor.name);
    }
  }

  async function startChannel(name, keepDrawer = false) {
    const response = await api(`/api/v1/channels/${encodeURIComponent(name)}/start`, { method: "POST" });
    applyChannelsState(response, keepDrawer);
  }

  async function stopChannel(name, keepDrawer = false) {
    const response = await api(`/api/v1/channels/${encodeURIComponent(name)}/stop`, { method: "POST" });
    applyChannelsState(response, keepDrawer);
  }

  async function restartChannel(name, keepDrawer = false) {
    const response = await api(`/api/v1/channels/${encodeURIComponent(name)}/restart`, { method: "POST" });
    applyChannelsState(response, keepDrawer);
  }

  function renderChannels() {
    if (!refs.channelsGrid) return;
    refs.channelsGrid.innerHTML = "";
    const rows = state.channels || [];
    if (!rows.length) {
      refs.channelsGrid.textContent = t("no_channels");
      return;
    }
    rows.forEach((row) => {
      const statusClass = channelStatusClass(row);
      const runtimeStatus = channelRuntimeStatusText(row);
      const card = createResourceCard({
        baseClass: `channel-card ${row.enabled ? "active" : "disabled"}`,
        title: channelDisplayName(row.name, row.display_name || row.name),
        subtitle: row.name || "-",
        badgeText: channelStatusText(row),
        badgeClass: statusClass === "enabled" ? "ok" : statusClass === "error" ? "warn" : "",
        description: row.description || "-",
        metaItems: [
          { label: zhen("Summary", "Summary"), value: summarizeChannel(row) },
          { label: zhen("Config", "Config"), value: channelConfigDetail(row) },
          { label: zhen("Runtime", "Runtime"), value: runtimeStatus },
          { label: zhen("Launch", "Launch"), value: row.launch_command || row.launch_hint || "-" },
        ],
        actions: [
          { label: zhen("设置", "Settings"), className: "btn-secondary", onClick: async () => openChannelDrawer(row.name) },
          ...(row.managed
            ? row.runtime?.running
              ? [
                  { label: zhen("停止", "Stop"), className: "btn-ghost", onClick: async () => stopChannel(row.name) },
                  { label: zhen("重启", "Restart"), className: "btn-ghost", onClick: async () => restartChannel(row.name) },
                ]
              : [
                  {
                    label: zhen("启动", "Start"),
                    className: "btn-ghost",
                    disabled: !row.launchable,
                    onClick: async () => startChannel(row.name),
                  },
                ]
            : []),
        ],
        onCardClick: () => openChannelDrawer(row.name),
      });
      refs.channelsGrid.appendChild(card);
    });
  }

  function openChannelDrawer(channelName) {
    if (!refs.channelDrawer) return;
    const target = (state.channels || []).find((row) => row.name === channelName);
    if (!target) return;
    state.channelEditor = JSON.parse(JSON.stringify(target));
    refs.channelEnabledInput.checked = Boolean(state.channelEditor.enabled);
    refs.channelPrefixInput.value = String(state.channelEditor.bot_prefix || "");
    refs.channelDrawerTitle.textContent = `${channelDisplayName(target.name, target.display_name || target.name)} ${zhen("设置", "Settings")}`;

    refs.channelFields.innerHTML = "";
    (state.channelEditor.fields || []).forEach((field) => {
      const wrap = document.createElement("label");
      wrap.className = "channel-field";
      const requiredMark = field.required ? " *" : "";
      const hint = field.secret && field.has_value ? zhen("已配置，留空不改", "configured, blank keeps current") : (field.placeholder || "");
      const type = field.type === "number" ? "number" : (field.secret ? "password" : "text");
      wrap.innerHTML = `
        <span>${esc(channelFieldLabel(field.key))}${requiredMark}</span>
        <input
          type="${type}"
          data-channel-key="${esc(field.key)}"
          data-channel-secret="${field.secret ? "1" : "0"}"
          value="${field.secret ? "" : esc(String(field.value || ""))}"
          placeholder="${esc(hint)}"
        />
      `;
      refs.channelFields.appendChild(wrap);
    });

    refs.channelDrawerHint.textContent = channelDrawerSummary(target);
    refs.channelDrawer.classList.remove("hidden");
  }

  async function loadChannels() {
    applyChannelsState(await api("/api/v1/channels"), false);
  }

  async function loadBrowser() {
    const response = await api("/api/v1/browser/status");
    const userConfigResponse = await api("/api/v1/browser/user-config");
    state.browserStatus = response || null;
    state.browserProfiles = Array.isArray(response?.profiles) ? response.profiles : [];
    state.browserInstall = response?.install || null;
    state.browserRecentCaptures = Array.isArray(response?.recent_captures) ? response.recent_captures : [];
    state.browserSessionBinding = response?.session_binding || null;
    state.browserUserConfig = userConfigResponse?.config || response?.user_config || null;
    renderBrowser();
  }

  async function loadWorkspaceTree(force = false) {
    state.workspaceLoading = true;
    state.workspaceError = "";
    renderWorkspaceBrowser();
    const query = String(state.workspaceTreeSearch || "").trim();
    const qs = new URLSearchParams();
    if (query) qs.set("query", query);
    const response = await api(`/api/v1/workspace/files/tree${qs.toString() ? `?${qs.toString()}` : ""}`);
    state.workspaceRoot = String(response.root || "");
    state.workspaceTree = response.tree || { type: "dir", name: "workspace", path: "", children: [] };
    state.workspaceLoading = false;
    const selectedPath = String(state.workspaceSelectedPath || "");
    const canReuseSelected = selectedPath && isWorkspacePathOpenable(state.workspaceTree, selectedPath);
    const nextPath = force ? "" : (canReuseSelected ? selectedPath : "");
    renderWorkspaceBrowser();
    if (nextPath) {
      await loadWorkspaceFile(nextPath);
      return;
    }
    state.workspaceSelectedPath = "";
    state.workspaceContent = "";
    state.workspaceContentKind = "markdown";
    state.workspaceEditable = false;
    renderWorkspaceBrowser();
  }

  async function loadWorkspaceFile(path) {
    const clean = String(path || "").trim();
    if (!clean) return;
    state.workspaceMode = "preview";
    state.workspaceSelectedPath = clean;
    state.workspaceLoading = true;
    state.workspaceError = "";
    renderWorkspaceBrowser();
    const qs = new URLSearchParams({ path: clean });
    try {
      const response = await api(`/api/v1/workspace/files/file?${qs.toString()}`);
      state.workspaceSelectedPath = String(response.path || clean);
      state.workspaceContent = String(response.content || "");
      state.workspaceContentKind = String(response.kind || "text");
      state.workspaceEditable = Boolean(response.editable);
      state.workspaceDirty = false;
    } catch (err) {
      const message = String(err || "");
      if (message.includes("markdown_only")) {
        state.workspaceSelectedPath = "";
        state.workspaceContent = "";
        state.workspaceContentKind = "markdown";
        state.workspaceEditable = false;
        state.workspaceDirty = false;
      } else {
        throw err;
      }
    } finally {
      state.workspaceLoading = false;
      renderWorkspaceBrowser();
    }
  }

  async function saveWorkspaceFile() {
    if (!state.workspaceSelectedPath) return;
    await api("/api/v1/workspace/files/file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        path: state.workspaceSelectedPath,
        content: String(refs.workspaceEditor?.value || ""),
      }),
    });
    state.workspaceContent = String(refs.workspaceEditor?.value || "");
    state.workspaceDirty = false;
    state.workspaceMode = "preview";
    showNoticeModal({ titleKey: "notice_title_success", body: t("workspace_saved"), variant: "success" });
    renderWorkspaceBrowser();
  }

  function toggleWorkspaceFolder(path) {
    const key = String(path || "");
    state.workspaceExpandedPaths = { ...state.workspaceExpandedPaths, [key]: !state.workspaceExpandedPaths[key] };
    renderWorkspaceBrowser();
  }

  function setWorkspaceEditMode(editing) {
    if (!state.workspaceSelectedPath) return;
    if (editing && !state.workspaceEditable) return;
    if (!editing && state.workspaceDirty) {
      const ok = window.confirm("Discard unsaved changes and return to preview?");
      if (!ok) return;
      state.workspaceDirty = false;
    }
    state.workspaceMode = editing ? "edit" : "preview";
    renderWorkspaceBrowser();
  }

  function renderWorkspaceTreeNode(node, depth = 0, parentVisible = true) {
    if (!node || typeof node !== "object") return "";
    const query = String(state.workspaceTreeSearch || "").trim().toLowerCase();
    const name = String(node.name || "");
    const path = String(node.path || "");
    const type = String(node.type || "");
    const selfMatch = !query || name.toLowerCase().includes(query) || path.toLowerCase().includes(query);
    if (type === "file") {
      if (!selfMatch) return "";
      const openable = Boolean(node.openable);
      const activeClass = path === state.workspaceSelectedPath ? " active" : "";
      const disabledClass = openable ? "" : " is-disabled";
      const sizeText = typeof node.size === "number" ? `${Math.max(1, Math.round(node.size / 1024))} KB` : "";
      return `
        <button class="docs-tree-item docs-tree-item--file${activeClass}${disabledClass}" ${openable ? `data-workspace-file="${esc(path)}"` : "disabled"} style="--docs-depth:${depth};">
          <span class="docs-tree-item__icon">#</span>
          <span class="docs-tree-item__label">${esc(name || path)}</span>
          ${sizeText ? `<span class="docs-tree-item__meta">${esc(sizeText)}</span>` : ""}
        </button>
      `;
    }
    const children = Array.isArray(node.children) ? node.children : [];
    const renderedChildren = children.map((child) => renderWorkspaceTreeNode(child, depth + 1)).filter(Boolean).join("");
    if (!renderedChildren && path !== "" && !selfMatch) return "";
    const expanded = path === "" || query ? true : Boolean(state.workspaceExpandedPaths[path]);
    const folderClass = expanded ? " is-expanded" : "";
    return `
      <div class="docs-tree-folder workspace-tree-folder${folderClass}">
        <button class="docs-tree-folder__label" data-workspace-folder="${esc(path)}" style="--docs-depth:${depth};">
          <span class="docs-tree-item__icon">${path === "" ? "W" : (expanded ? "▾" : "▸")}</span>
          <span class="docs-tree-item__label">${esc(name || "workspace")}</span>
        </button>
        <div class="docs-tree-folder__children">${expanded ? renderedChildren : ""}</div>
      </div>
    `;
  }

  function findFirstWorkspaceFile(node) {
    if (!node || typeof node !== "object") return "";
    if (node.type === "file") return Boolean(node.openable) ? String(node.path || "") : "";
    const children = Array.isArray(node.children) ? node.children : [];
    for (const child of children) {
      const found = findFirstWorkspaceFile(child);
      if (found) return found;
    }
    return "";
  }

  function findWorkspaceNodeByPath(node, targetPath) {
    if (!node || typeof node !== "object") return null;
    const nodePath = String(node.path || "");
    if (nodePath === targetPath) return node;
    const children = Array.isArray(node.children) ? node.children : [];
    for (const child of children) {
      const found = findWorkspaceNodeByPath(child, targetPath);
      if (found) return found;
    }
    return null;
  }

  function isWorkspacePathOpenable(tree, targetPath) {
    const node = findWorkspaceNodeByPath(tree, String(targetPath || ""));
    return Boolean(node && node.type === "file" && node.openable);
  }

  function stripLeadingFrontMatter(markdownText) {
    const raw = String(markdownText || "");
    const normalized = raw.replace(/^\uFEFF/, "");
    if (!normalized.startsWith("---")) return raw;
    const match = normalized.match(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/);
    if (!match) return raw;
    return normalized.slice(match[0].length);
  }

  function renderWorkspaceBrowser() {
    if (refs.workspaceRootLabel) {
      refs.workspaceRootLabel.textContent = state.workspaceRoot ? `${t("workspace_root_label")}: ${state.workspaceRoot}` : "";
      refs.workspaceRootLabel.title = state.workspaceRoot || "";
    }
    if (refs.workspaceCurrentPath) {
      refs.workspaceCurrentPath.textContent = state.workspaceSelectedPath || state.workspaceRoot || "workspace";
      refs.workspaceCurrentPath.title = state.workspaceSelectedPath || state.workspaceRoot || "workspace";
    }
    if (refs.workspacePreview?.parentElement) {
      const empty = !state.workspaceSelectedPath;
      refs.workspacePreview.parentElement.classList.toggle("is-empty", empty);
      if (refs.workspaceEditor) {
        refs.workspaceEditor.classList.toggle("is-hidden", empty || state.workspaceMode !== "edit");
      }
      if (refs.workspacePreview) {
        refs.workspacePreview.classList.toggle("is-hidden", empty || state.workspaceMode === "edit");
      }
    }
    if (refs.workspaceTreeList) {
      const tree = state.workspaceTree;
      const hasChildren = Array.isArray(tree?.children) && tree.children.length > 0;
      if (state.workspaceLoading) {
        refs.workspaceTreeList.innerHTML = `<div class="state-box">${esc(t("workspace_loading"))}</div>`;
      } else if (!hasChildren) {
        refs.workspaceTreeList.innerHTML = `<div class="state-box">${esc(t("workspace_empty"))}</div>`;
      } else {
        const children = Array.isArray(tree?.children) ? tree.children : [];
        refs.workspaceTreeList.innerHTML = children.map((child) => renderWorkspaceTreeNode(child, 0)).filter(Boolean).join("");
      }
      refs.workspaceTreeList.querySelectorAll("[data-workspace-file]").forEach((button) => {
        button.addEventListener("click", () => loadWorkspaceFile(button.getAttribute("data-workspace-file") || "").catch((err) => showActionError(err)));
      });
      refs.workspaceTreeList.querySelectorAll("[data-workspace-folder]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.preventDefault();
          event.stopPropagation();
          toggleWorkspaceFolder(button.getAttribute("data-workspace-folder") || "");
        });
      });
    }
    if (refs.workspaceEditor) {
      const editing = state.workspaceMode === "edit";
      refs.workspaceEditor.value = String(state.workspaceContent || "");
      refs.workspaceEditor.readOnly = !editing;
      refs.workspaceEditor.classList.toggle("is-hidden", !editing);
      refs.workspaceEditor.classList.toggle("is-editing", editing);
    }
    if (refs.workspacePreview) {
      const contentKind = String(state.workspaceContentKind || "markdown");
      const previewText = stripLeadingFrontMatter(state.workspaceContent);
      refs.workspacePreview.classList.toggle("is-hidden", state.workspaceMode === "edit");
      refs.workspacePreview.innerHTML = state.workspaceLoading
        ? `<div class="state-box">${esc(t("workspace_loading"))}</div>`
        : (previewText ? markdownToSafeHtml(previewText) : `<div class="state-box">${esc(t("workspace_open_hint"))}</div>`);
    }
    if (refs.workspaceEditBtn) refs.workspaceEditBtn.disabled = !state.workspaceSelectedPath || state.workspaceMode === "edit" || !state.workspaceEditable;
    if (refs.workspaceCancelBtn) refs.workspaceCancelBtn.disabled = state.workspaceMode !== "edit";
    if (refs.workspaceSaveBtn) refs.workspaceSaveBtn.disabled = state.workspaceMode !== "edit" || !state.workspaceDirty;
  }

  function getBrowserModeDefinitions() {
    return [
      {
        mode: "use_existing_browser",
        title: t("browser_mode_existing_title"),
        description: t("browser_mode_existing_desc"),
      },
      {
        mode: "auto_prepare_browser",
        title: t("browser_mode_auto_title"),
        description: t("browser_mode_auto_desc"),
      },
      {
        mode: "use_fresh_browser",
        title: t("browser_mode_fresh_title"),
        description: t("browser_mode_fresh_desc"),
      },
    ];
  }

  function getBrowserModeTitle(mode) {
    const found = getBrowserModeDefinitions().find((item) => item.mode === mode);
    return found?.title || mode || "-";
  }

  function normalizePath(value) {
    return String(value || "").trim().replace(/\\/g, "/").toLowerCase();
  }

  function getBrowserLaunchWindowText(mode) {
    const key = `browser_window_${mode || ""}`;
    const value = t(key);
    return value === key ? "-" : value;
  }

  function getBrowserLaunchStateText(config) {
    if (config?.connected) return t("browser_launch_state_started");
    const statusName = String(config?.status || "configured");
    if (statusName === "starting") return t("browser_launch_state_starting");
    if (statusName === "failed" || statusName === "needs_user_action") return t("browser_launch_state_failed");
    return t("browser_launch_state_idle");
  }

  function getBrowserLaunchProfileSourceText(config) {
    const key = `browser_launch_source_${config?.launch_profile_source || ""}`;
    const value = t(key);
    return value === key ? "-" : value;
  }

  function renderBrowser() {
    renderBrowserUserModes();
    renderBrowserUserStatus();
    renderBrowserUserSetup();
    renderBrowserPrimaryActions();
    renderBrowserIdentityPanel();
    renderBrowserOverview();
    renderBrowserProfiles();
    renderBrowserInstall();
    renderBrowserDiagnostics();
    renderBrowserBinding();
  }

  function renderBrowserUserModes() {
    if (!refs.browserUserModesGrid) return;
    const currentMode = String(state.browserUserConfig?.selected_mode || "use_existing_browser");
    refs.browserUserModesGrid.innerHTML = getBrowserModeDefinitions()
      .map((item) => {
        const activeClass = item.mode === currentMode ? " active" : "";
        return `
          <button class="browser-mode-card${activeClass}" data-browser-mode="${esc(item.mode)}" type="button">
            <span class="browser-mode-card__eyebrow">${esc(t("browser_selected_mode"))}</span>
            <strong class="browser-mode-card__title">${esc(item.title)}</strong>
            <span class="browser-mode-card__desc">${esc(item.description)}</span>
          </button>
        `;
      })
      .join("");
    refs.browserUserModesGrid.querySelectorAll("[data-browser-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        const mode = button.getAttribute("data-browser-mode") || "use_existing_browser";
        setBrowserUserMode(mode).catch((err) => showActionError(err));
      });
    });
  }

  function renderBrowserUserStatus() {
    if (!refs.browserUserStatusPanel) return;
    const config = state.browserUserConfig || {};
    const install = state.browserInstall || {};
    const connected = !!config.connected;
    const statusName = String(config.status || "configured");
    const browserLabel = config.preferred_browser_name || config.browser_executable_path || "-";
    const profileLabel = config.selected_profile_label || config.profile_directory || "-";
    const launchWindowText = getBrowserLaunchWindowText(config.launch_window_mode || "");
    const launchStateText = getBrowserLaunchStateText(config);
    const launchProfileSourceText = getBrowserLaunchProfileSourceText(config);
    refs.browserUserStatusPanel.className = `state-box ${connected ? "ok" : statusName === "failed" ? "error" : statusName === "needs_user_action" ? "warn" : "warn"}`;
    refs.browserUserStatusPanel.innerHTML = `
      <div><strong>${esc(t("browser_selected_mode"))}:</strong> ${esc(getBrowserModeTitle(config.selected_mode || "use_existing_browser"))}</div>
      <div><strong>${esc(t("browser_launch_state"))}:</strong> ${esc(launchStateText)}</div>
      <div><strong>${esc(t("browser_launch_profile_source"))}:</strong> ${esc(launchProfileSourceText)}</div>
      <div><strong>${esc(t("browser_connected_state"))}:</strong> ${esc(config.connection_status || statusName || "-")}</div>
      <div><strong>${esc(t("browser_last_used_browser"))}:</strong> ${esc(browserLabel)}</div>
      <div><strong>${esc(t("browser_identity_profile"))}:</strong> ${esc(profileLabel)}</div>
      <div><strong>${esc(t("browser_launch_window_result"))}:</strong> ${esc(launchWindowText)}</div>
      <div><strong>${esc(t("browser_last_strategy"))}:</strong> ${esc(config.last_launch_strategy || "-")}</div>
      <div><strong>${esc(t("browser_last_connected_at"))}:</strong> ${esc(config.last_connected_at || "-")}</div>
      <div><strong>${esc(t("browser_system_browsers"))}:</strong> ${esc((install.system_browsers || []).map((item) => item.name).join(", ") || "-")}</div>
      <div><strong>${esc(t("browser_last_error"))}:</strong> ${esc(config.last_error || install.last_error || "-")}</div>
    `;
    if (refs.browserModeHint) {
      refs.browserModeHint.textContent = connected
        ? t("browser_started_hint")
        : statusName === "needs_user_action" || statusName === "failed"
          ? t("browser_needs_action")
          : t("browser_mode_saved");
    }
  }

  function renderBrowserPrimaryActions() {
    if (refs.launchBrowserBtn) {
      refs.launchBrowserBtn.textContent = t("browser_launch_btn");
      refs.launchBrowserBtn.disabled = false;
    }
    if (refs.disconnectBrowserBtn) {
      refs.disconnectBrowserBtn.textContent = t("browser_disconnect_btn");
      refs.disconnectBrowserBtn.disabled = !state.browserUserConfig?.connected;
    }
  }

  function renderBrowserUserSetup() {
    if (!refs.browserUserSetupPanel) return;
    const config = state.browserUserConfig || {};
    const install = state.browserInstall || {};
    const currentMode = String(config.selected_mode || "use_existing_browser");
    if (currentMode !== "use_existing_browser") {
      refs.browserUserSetupPanel.innerHTML = "";
      return;
    }
    const systemBrowsers = Array.isArray(install.system_browsers) ? install.system_browsers : [];
    const browserButtons = systemBrowsers.length
      ? systemBrowsers
          .map(
            (item) => {
              const isSelected = normalizePath(item.path || "") === normalizePath(config.browser_executable_path || "");
              return `
              <button class="btn-secondary btn-glass btn-sm browser-detected-choice${isSelected ? " active" : ""}" type="button" data-detected-browser-path="${esc(item.path || "")}" data-detected-browser-name="${esc(item.name || "")}">
                ${esc(item.name || "browser")} · ${esc(item.path || "")}
              </button>
            `;
            },
          )
          .join("")
      : `<div class="state-box warn">${esc(t("browser_detected_empty"))}</div>`;
    const selectedSummary = config.browser_executable_path
      ? `<div class="state-box ok"><strong>${esc(t("browser_selected_browser"))}:</strong> ${esc(config.preferred_browser_name || config.browser_executable_path || "-")}<br/>${esc(t("browser_selection_saved"))}</div>`
      : "";
    const launchProfileSummary = config.launch_profile_source
      ? `<div class="state-box ok"><strong>${esc(t("browser_launch_profile_source"))}:</strong> ${esc(getBrowserLaunchProfileSourceText(config))}</div>`
      : "";
    refs.browserUserSetupPanel.innerHTML = `
      <div class="browser-setup-card">
        <div class="panel-header">
          <h3>${esc(t("browser_setup_title"))}</h3>
          <div class="row-actions">
            <button id="detectBrowserAccessBtn" class="btn-secondary btn-glass btn-sm" type="button">${esc(t("browser_detect_action_btn"))}</button>
            <button id="pickBrowserExecutableBtn" class="btn-secondary btn-glass btn-sm" type="button">${esc(t("browser_choose_program_btn"))}</button>
          </div>
        </div>
        <div class="browser-detected-list">
          <div class="browser-setup-label">${esc(t("browser_detected_title"))}</div>
          <div class="browser-detected-actions">${browserButtons}</div>
        </div>
        ${selectedSummary}
        ${launchProfileSummary}
        <div class="state-box ok">${esc(t("browser_identity_detected"))}</div>
      </div>
    `;

    const detectBtn = document.getElementById("detectBrowserAccessBtn");
    if (detectBtn) {
      detectBtn.addEventListener("click", () => detectBrowserInstall().catch((err) => showActionError(err)));
    }
    const pickBtn = document.getElementById("pickBrowserExecutableBtn");
    if (pickBtn) {
      pickBtn.addEventListener("click", () => pickBrowserExecutable().catch((err) => showActionError(err)));
    }
    refs.browserUserSetupPanel.querySelectorAll("[data-detected-browser-path]").forEach((button) => {
      button.addEventListener("click", () => {
        const path = button.getAttribute("data-detected-browser-path") || "";
        const name = button.getAttribute("data-detected-browser-name") || "";
        applyDetectedBrowserSelection(path, name).catch((err) => showActionError(err));
      });
    });
  }

  function renderBrowserIdentityPanel() {
    if (!refs.browserIdentityPanel) return;
    const config = state.browserUserConfig || {};
    const profileRows = Array.isArray(config.discovered_profiles) ? config.discovered_profiles : [];
    const currentProgram = String(config.browser_executable_path || "").trim();
    if (!currentProgram) {
      refs.browserIdentityPanel.className = "state-box warn";
      refs.browserIdentityPanel.innerHTML = `
        <div><strong>${esc(t("browser_identity_title"))}:</strong> ${esc(t("browser_identity_empty"))}</div>
      `;
      return;
    }
    const profileButtons = profileRows.length
      ? profileRows
          .map((item) => {
            const selected = String(item.id || "") === String(config.profile_directory || "");
            return `
              <button class="btn-secondary btn-glass btn-sm${selected ? " active" : ""}" type="button" data-browser-profile-id="${esc(item.id || "")}">
                ${esc(item.label || item.id || "-")}
              </button>
            `;
          })
          .join("")
      : `<span class="page-sub">-</span>`;
    refs.browserIdentityPanel.className = "state-box ok";
    refs.browserIdentityPanel.innerHTML = `
      <div><strong>${esc(t("browser_identity_program"))}:</strong> ${esc(currentProgram)}</div>
      <div><strong>${esc(t("browser_identity_family"))}:</strong> ${esc(config.preferred_browser_name || config.browser_family || "-")}</div>
      <div><strong>${esc(t("browser_identity_data_dir"))}:</strong> ${esc(config.user_data_dir || "-")}</div>
      <div><strong>${esc(t("browser_identity_profile"))}:</strong> ${esc(config.selected_profile_label || config.profile_directory || "-")}</div>
      <div><strong>${esc(t("browser_identity_profiles"))}:</strong></div>
      <div class="browser-profile-choice-row">${profileButtons}</div>
      <div class="browser-actions-row">
        <button id="refreshBrowserIdentityBtn" class="btn-secondary btn-glass btn-sm" type="button">${esc(t("browser_refresh_identity_btn"))}</button>
        <button id="saveBrowserIdentityBtn" class="btn-secondary btn-glass btn-sm" type="button">${esc(t("browser_identity_save_btn"))}</button>
      </div>
      <div class="browser-identity-advanced-grid">
        <label class="browser-setup-field">
          <span>${esc(t("browser_identity_data_dir"))}</span>
          <input id="browserUserDataDirInput" class="liquid-glass" value="${esc(config.user_data_dir || "")}" />
        </label>
        <label class="browser-setup-field">
          <span>${esc(t("browser_identity_profile"))}</span>
          <input id="browserProfileDirectoryInput" class="liquid-glass" value="${esc(config.profile_directory || "")}" />
        </label>
        <label class="browser-setup-field browser-setup-field--port">
          <span>${esc(t("browser_port_label"))}</span>
          <input id="browserDebugPortInput" type="number" min="1" max="65535" class="liquid-glass" value="${esc(String(config.remote_debugging_port || 9222))}" />
        </label>
      </div>
    `;
    refs.browserIdentityPanel.querySelectorAll("[data-browser-profile-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const profileId = button.getAttribute("data-browser-profile-id") || "";
        chooseBrowserProfile(profileId).catch((err) => showActionError(err));
      });
    });
    const refreshBtn = document.getElementById("refreshBrowserIdentityBtn");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => refreshBrowserIdentity().catch((err) => showActionError(err)));
    }
    const saveBtn = document.getElementById("saveBrowserIdentityBtn");
    if (saveBtn) {
      saveBtn.addEventListener("click", () => saveBrowserIdentitySettings().catch((err) => showActionError(err)));
    }
  }

  function renderBrowserOverview() {
    if (!refs.browserOverview) return;
    const status = state.browserStatus || {};
    const installState = state.browserInstall?.status || "pending";
    const captures = Array.isArray(status.recent_captures) ? status.recent_captures : [];
    refs.browserOverview.className = `state-box ${installState === "failed" ? "error" : installState === "installed" ? "ok" : "warn"}`;
    refs.browserOverview.innerHTML = `
      <div><strong>${t("browser_default_profile")}:</strong> ${esc(status.default_profile || "-")}</div>
      <div><strong>${t("browser_workspace_root")}:</strong> ${esc(status.workspace_browser_root || "-")}</div>
      <div><strong>${t("browser_install_state")}:</strong> ${esc(installState)}</div>
      <div><strong>recent capture</strong>: ${esc(captures.slice(0, 1).map((item) => item.name || item.path || "-").join(", ") || "-")}</div>
    `;
  }

  function renderBrowserProfiles() {
    if (!refs.browserProfilesGrid) return;
    refs.browserProfilesGrid.innerHTML = "";
    const profiles = state.browserProfiles || [];
    if (!profiles.length) {
      refs.browserProfilesGrid.textContent = t("browser_no_profiles");
      return;
    }

    profiles.forEach((profile) => {
      const status = profile.status || {};
      const diagnostics = Array.isArray(status.diagnostics) ? status.diagnostics : [];
      const tabs = Array.isArray(status.tabs) ? status.tabs : [];
      const stateBlocks = [];
      if (diagnostics.length) {
        diagnostics.slice(0, 2).forEach((item) => {
          stateBlocks.push({ title: zhen("Diagnostic", "Diagnostic"), body: item.summary || "-" });
        });
      }
      if (profile.driver === "existing-session") {
        stateBlocks.push({ title: zhen("Hint", "Hint"), body: `${t("browser_existing_hint")} (${status.cdp_url || `http://${profile.cdp_host || "127.0.0.1"}:${profile.cdp_port || 9222}`})` });
      }
      if (profile.driver === "remote-cdp" && !status.running) {
        stateBlocks.push({ title: zhen("Remote", "Remote"), body: status.last_error || (status.cdp_url || profile.cdp_url || "-") });
      }
      if (tabs.length) {
        tabs.slice(0, 2).forEach((tab) => {
          stateBlocks.push({ title: zhen("Tab", "Tab"), body: tab.title || tab.url || tab.target_id || "-" });
        });
      }
      const card = createResourceCard({
        baseClass: "profile-card browser-profile-card",
        title: profile.profile_id || "-",
        subtitle: profile.driver || "-",
        badgeText: status.running ? t("browser_running") : status.status === "stopped" ? t("browser_stopped") : t("browser_idle"),
        badgeClass: status.running ? "ok" : "",
        description: diagnostics[0]?.summary || t("browser_no_diagnostics"),
        metaItems: [
          { label: "driver", value: profile.driver || "-" },
          { label: "channel", value: profile.channel || "-" },
          { label: profile.driver === "managed" || profile.driver === "user-identity" ? "exec" : "cdp", value: profile.driver === "managed" || profile.driver === "user-identity" ? (status.executable_path || profile.executable_path || "-") : (status.cdp_url || profile.cdp_url || "-"), mono: true },
          { label: "tabs", value: tabs.length || 0 },
        ],
        stateBlocks,
        actions: [
          { label: t("browser_start_btn"), className: "btn-secondary", disabled: !status.capabilities?.supports_start, onClick: async () => startBrowserProfile(profile.profile_id) },
          { label: t("browser_stop_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_stop, onClick: async () => stopBrowserProfile(profile.profile_id) },
          { label: t("browser_diagnose_btn"), className: "btn-ghost", onClick: async () => diagnoseBrowserProfile(profile.profile_id) },
          { label: t("browser_reconnect_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_reconnect, onClick: async () => reconnectBrowserProfile(profile.profile_id) },
          { label: t("browser_tabs_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_tabs, onClick: async () => showBrowserTabs(profile.profile_id) },
          { label: t("browser_open_tab_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_tabs, onClick: async () => openBrowserTab(profile.profile_id) },
          { label: t("browser_snapshot_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_snapshot, onClick: async () => snapshotBrowserProfile(profile.profile_id) },
          { label: t("browser_screenshot_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_screenshot, onClick: async () => screenshotBrowserProfile(profile.profile_id) },
          { label: t("browser_act_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_act, onClick: async () => actBrowserProfile(profile.profile_id) },
          { label: t("browser_set_default_btn"), className: "btn-ghost", onClick: async () => setDefaultBrowserProfile(profile.profile_id) },
          { label: t("browser_reset_btn"), className: "btn-ghost", disabled: !status.capabilities?.supports_reset, onClick: async () => resetBrowserProfile(profile.profile_id) },
        ],
      });

      refs.browserProfilesGrid.appendChild(card);
    });
  }

  function renderBrowserInstall() {
    if (!refs.browserInstallPanel || !refs.installManagedBrowserBtn) return;
    const install = state.browserInstall || {};
    const systemBrowsers = Array.isArray(install.system_browsers) ? install.system_browsers : [];
    const offerInstall = !!install.offer_install;
    refs.browserInstallPanel.className = `state-box ${install.status === "failed" ? "error" : install.status === "installed" ? "ok" : "warn"}`;
    refs.browserInstallPanel.innerHTML = `
      <div><strong>${t("browser_install_state")}:</strong> ${esc(install.status || "pending")}</div>
      <div><strong>${t("browser_system_browsers")}:</strong> ${esc(systemBrowsers.map((item) => item.name).join(", ") || "-")}</div>
      <div><strong>${t("browser_offer_install")}:</strong> ${esc(offerInstall ? t(systemBrowsers.length ? "browser_install_optional" : "browser_install_required") : t("browser_install_not_needed"))}</div>
      <div><strong>cache</strong>: ${esc(install.cache_dir || "-")}</div>
      <div><strong>${t("browser_last_error")}:</strong> ${esc(install.last_error || "-")}</div>
    `;
    refs.installManagedBrowserBtn.disabled = !offerInstall && install.status !== "failed";
    if (refs.reinstallManagedBrowserBtn) {
      refs.reinstallManagedBrowserBtn.textContent = t("browser_install_reinstall_btn");
      refs.reinstallManagedBrowserBtn.disabled = false;
    }
    if (refs.removeManagedBrowserBtn) {
      refs.removeManagedBrowserBtn.textContent = t("browser_install_remove_btn");
      refs.removeManagedBrowserBtn.disabled = false;
    }
    if (refs.cancelManagedBrowserBtn) {
      refs.cancelManagedBrowserBtn.textContent = t("browser_install_cancel_btn");
      refs.cancelManagedBrowserBtn.disabled = install.status !== "installing";
    }
  }

  function renderBrowserDiagnostics() {
    if (!refs.browserDiagnosticsPanel) return;
    refs.browserDiagnosticsPanel.innerHTML = "";
    const rows = [];
    (state.browserProfiles || []).forEach((profile) => {
      const diagnostics = Array.isArray(profile?.status?.diagnostics) ? profile.status.diagnostics : [];
      diagnostics.forEach((item) => rows.push({ profile_id: profile.profile_id, ...item }));
    });
    if (!rows.length) {
      refs.browserDiagnosticsPanel.textContent = t("browser_no_diagnostics");
      return;
    }
    rows.forEach((item) => {
      const line = document.createElement("div");
      line.className = `state-box ${item.level === "error" ? "error" : item.level === "warn" ? "warn" : "ok"}`;
      line.textContent = `${item.profile_id}: ${item.summary || "-"}`;
      refs.browserDiagnosticsPanel.appendChild(line);
    });
  }

  function renderBrowserBinding() {
    if (!refs.browserBindingPanel) return;
    const binding = state.browserSessionBinding || {};
    refs.browserBindingPanel.className = `state-box ${binding.profile_id ? "ok" : "warn"}`;
    const captures = Array.isArray(state.browserRecentCaptures) ? state.browserRecentCaptures : [];
    const recentCapture = captures[0] || {};
    refs.browserBindingPanel.innerHTML = `
      <div><strong>profile</strong>: ${esc(binding.profile_id || "-")}</div>
      <div><strong>session</strong>: ${esc(binding.session_id || "-")}</div>
      <div><strong>tab</strong>: ${esc(binding.tab_id || "-")}</div>
      <div><strong>latest capture</strong>: ${esc(recentCapture.name || recentCapture.path || "-")}</div>
    `;
  }

  async function startBrowserProfile(profileId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/start`, { method: "POST" });
    await loadBrowser();
  }

  async function stopBrowserProfile(profileId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/stop`, { method: "POST" });
    await loadBrowser();
  }

  async function diagnoseBrowserProfile(profileId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/diagnose`, { method: "POST" });
    await loadBrowser();
  }

  async function reconnectBrowserProfile(profileId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/reconnect`, { method: "POST" });
    await loadBrowser();
  }

  async function showBrowserTabs(profileId) {
    const response = await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/tabs`);
    const tabs = Array.isArray(response?.tabs) ? response.tabs : [];
    showNoticeModal({
      titleKey: "notice_title_info",
      body: tabs.length ? tabs.map((tab) => `${tab.target_id}: ${tab.title || tab.url || "-"}`).join("\n") : t("browser_tabs_empty"),
      variant: "info",
    });
    await loadBrowser();
  }

  async function selectBrowserTab(profileId, targetId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/tabs/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_id: targetId }),
    });
    await loadBrowser();
  }

  async function closeBrowserTab(profileId, targetId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/tabs/close`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_id: targetId }),
    });
    await loadBrowser();
  }

  async function openBrowserTab(profileId) {
    const url = window.prompt("URL", "about:blank");
    if (url === null) return;
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/tabs/open`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    await loadBrowser();
  }

  async function snapshotBrowserProfile(profileId) {
    const response = await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/snapshot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    if (response?.artifact?.path) {
      showNoticeModal({ titleKey: "notice_title_success", body: response.artifact.path, variant: "success" });
    }
    await loadBrowser();
  }

  async function screenshotBrowserProfile(profileId) {
    const response = await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/screenshot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_page: true }),
    });
    if (response?.artifact?.path) {
      showNoticeModal({ titleKey: "notice_title_success", body: response.artifact.path, variant: "success" });
    }
    await loadBrowser();
  }

  async function actBrowserProfile(profileId) {
    const kind = window.prompt("kind (navigate/evaluate/click/fill/upload/press/wait)", "navigate");
    if (kind === null) return;
    const payload = { kind };
    if (kind === "navigate") {
      const url = window.prompt("url", "https://example.com");
      if (url === null) return;
      payload.url = url;
    } else if (kind === "evaluate") {
      const expression = window.prompt("expression", "document.title");
      if (expression === null) return;
      payload.expression = expression;
    } else if (kind === "click" || kind === "fill") {
      const selector = window.prompt("selector", "input");
      if (selector === null) return;
      payload.selector = selector;
      if (kind === "fill") {
        const value = window.prompt("value", "hello");
        if (value === null) return;
        payload.value = value;
      }
    } else if (kind === "upload") {
      const selector = window.prompt("selector", "input[type=file]");
      if (selector === null) return;
      const filePath = window.prompt("file_path", "");
      if (filePath === null) return;
      payload.selector = selector;
      payload.file_path = filePath;
    } else if (kind === "press") {
      const selector = window.prompt("selector (optional)", "");
      if (selector === null) return;
      const key = window.prompt("key", "Enter");
      if (key === null) return;
      payload.selector = selector;
      payload.key = key;
    } else if (kind === "wait") {
      const selector = window.prompt("selector (optional)", "");
      if (selector === null) return;
      const timeoutMs = window.prompt("timeout_ms", "3000");
      if (timeoutMs === null) return;
      payload.selector = selector;
      payload.timeout_ms = Number(timeoutMs) || 3000;
    }
    const response = await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/act`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (response?.result) {
      showNoticeModal({
        titleKey: "notice_title_success",
        body: JSON.stringify(response.result, null, 2),
        variant: "success",
      });
    }
    await loadBrowser();
  }

  async function setDefaultBrowserProfile(profileId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/set-default`, { method: "POST" });
    await loadBrowser();
  }

  async function setBrowserUserMode(mode) {
    await api("/api/v1/browser/user-config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selected_mode: mode }),
    });
    await loadBrowser();
  }

  async function applyDetectedBrowserSelection(path, name) {
    await api("/api/v1/browser/user-config/identity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        selected_mode: "use_existing_browser",
        browser_executable_path: path,
        preferred_browser_name: name,
      }),
    });
    await loadBrowser();
  }

  async function pickBrowserExecutable() {
    await api("/api/v1/browser/user-config/pick-executable", {
      method: "POST",
    });
    await loadBrowser();
  }

  async function chooseBrowserProfile(profileDirectory) {
    await api("/api/v1/browser/user-config/identity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        selected_mode: "use_existing_browser",
        browser_executable_path: state.browserUserConfig?.browser_executable_path || "",
        preferred_browser_name: state.browserUserConfig?.preferred_browser_name || "",
        profile_directory: profileDirectory,
        user_data_dir: state.browserUserConfig?.user_data_dir || "",
      }),
    });
    await loadBrowser();
  }

  async function refreshBrowserIdentity() {
    await api("/api/v1/browser/user-config/identity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        selected_mode: "use_existing_browser",
        browser_executable_path: state.browserUserConfig?.browser_executable_path || "",
        preferred_browser_name: state.browserUserConfig?.preferred_browser_name || "",
        user_data_dir: state.browserUserConfig?.user_data_dir || "",
        profile_directory: state.browserUserConfig?.profile_directory || "",
      }),
    });
    await loadBrowser();
  }

  async function saveBrowserIdentitySettings() {
    const userDataDirInput = document.getElementById("browserUserDataDirInput");
    const profileDirectoryInput = document.getElementById("browserProfileDirectoryInput");
    const portInput = document.getElementById("browserDebugPortInput");
    const browserPath = String(state.browserUserConfig?.browser_executable_path || "").trim();
    const userDataDir = String(userDataDirInput?.value || "").trim();
    const profileDirectory = String(profileDirectoryInput?.value || "").trim();
    const remoteDebuggingPort = Number(portInput?.value || 9222) || 9222;
    await api("/api/v1/browser/user-config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        selected_mode: "use_existing_browser",
        browser_executable_path: browserPath,
        preferred_browser_name: state.browserUserConfig?.preferred_browser_name || "",
        user_data_dir: userDataDir,
        profile_directory: profileDirectory,
        remote_debugging_port: remoteDebuggingPort,
      }),
    });
    await loadBrowser();
  }

  async function launchConfiguredBrowser() {
    const payload = {
      selected_mode: state.browserUserConfig?.selected_mode || "use_existing_browser",
      browser_executable_path: state.browserUserConfig?.browser_executable_path || "",
      user_data_dir: state.browserUserConfig?.user_data_dir || "",
      profile_directory: state.browserUserConfig?.profile_directory || "",
      remote_debugging_port: state.browserUserConfig?.remote_debugging_port || 0,
      preferred_browser_name: state.browserUserConfig?.preferred_browser_name || "",
    };
    try {
      await api("/api/v1/browser/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } finally {
      await loadBrowser();
    }
  }

  async function disconnectConfiguredBrowser() {
    try {
      await api("/api/v1/browser/disconnect", { method: "POST" });
    } finally {
      await loadBrowser();
    }
  }

  async function resetBrowserProfile(profileId) {
    await api(`/api/v1/browser/profiles/${encodeURIComponent(profileId)}/reset`, { method: "POST" });
    await loadBrowser();
  }

  async function detectBrowserInstall() {
    await api("/api/v1/browser/install/detect", { method: "POST" });
    await loadBrowser();
  }

  async function installManagedBrowser() {
    await api("/api/v1/browser/install/managed", { method: "POST" });
    await loadBrowser();
  }

  async function reinstallManagedBrowser() {
    await api("/api/v1/browser/install/reinstall", { method: "POST" });
    await loadBrowser();
  }

  async function removeManagedBrowser() {
    await api("/api/v1/browser/install/remove", { method: "POST" });
    await loadBrowser();
  }

  async function cancelManagedBrowserInstall() {
    await api("/api/v1/browser/install/cancel", { method: "POST" });
    await loadBrowser();
  }

  async function saveChannelConfig() {
    if (!state.channelEditor || !refs.channelFields) return;
    const settings = {};
    refs.channelFields.querySelectorAll("input[data-channel-key]").forEach((input) => {
      const key = input.getAttribute("data-channel-key");
      const secret = input.getAttribute("data-channel-secret") === "1";
      const text = String(input.value || "").trim();
      if (!key) return;
      if (secret && !text) return;
      settings[key] = text;
    });

    const payload = {
      enabled: refs.channelEnabledInput.checked,
      bot_prefix: refs.channelPrefixInput.value.trim(),
      settings,
    };
    const response = await api(`/api/v1/channels/${encodeURIComponent(state.channelEditor.name)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    applyChannelsState(response, false);
    closeChannelDrawer();
  }

  function makeActionBtn(label, fn, options = {}) {
    const btn = document.createElement("button");
    btn.className = "btn-ghost";
    btn.textContent = label;
    btn.disabled = Boolean(options.disabled);
    btn.addEventListener("click", async () => {
      if (btn.disabled) return;
      try {
        await fn();
      } catch (err) {
        showActionError(err);
      }
    });
    return btn;
  }

  function bindEvents() {
    refs.langToggleBtn.addEventListener("click", () => {
      state.lang = state.lang === "zh" ? "en" : "zh";
      localStorage.setItem(LANG_KEY, state.lang);
      document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
      applyI18n();
      renderSessions();
      renderMessages();
      renderEvents();
      renderChannels();
      renderBrowser();
      renderAlarms();
      renderSkills();
      renderMcp();
      renderModels();
      renderBillingStatus();
      renderBillingOverview();
      renderBillingCalls();
      saveRuntimeSettings().catch((err) => console.warn("save settings failed", err));
    });

    refs.navItems.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const targetView = String(btn.dataset.view || "").trim();
        setView(targetView, { explicit: true });
        try {
          await loadViewDataOnEnter(targetView);
        } catch (err) {
          showActionError(err);
        }
      });
    });

    refs.sessionFilters.forEach((btn) => {
      btn.addEventListener("click", () => {
        state.filter = btn.dataset.filter;
        refs.sessionFilters.forEach((b) => b.classList.toggle("active", b === btn));
        renderSessions();
      });
    });

    refs.newSessionBtn.addEventListener("click", async () => {
      await api("/api/v1/sessions/new", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "web:local" }),
      });
      await loadSessions(false);
      const latest = state.sessions.find((s) => s.user_id === "web:local");
      if (latest) await selectSession(latest);
    });

    refs.refreshSessionsBtn.addEventListener("click", () => loadSessions(false));
    refs.sendBtn.addEventListener("click", () => sendMessage().catch((err) => showActionError(err)));
    if (refs.voiceInputBtn) refs.voiceInputBtn.addEventListener("click", () => toggleVoiceInput());
    refs.chatInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") sendMessage().catch((err) => showActionError(err));
    });
    refs.cancelBtn.addEventListener("click", () => cancelCurrent().catch((err) => showActionError(err)));
    refs.fileInput.addEventListener("change", async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      try {
        await uploadFile(file);
      } catch (err) {
        showActionError(err, "upload_failed");
      } finally {
        refs.fileInput.value = "";
      }
    });

    if (refs.reloadAlarmsBtn) refs.reloadAlarmsBtn.addEventListener("click", () => loadAlarms().catch((err) => showActionError(err)));
    if (refs.reloadChannelsBtn) refs.reloadChannelsBtn.addEventListener("click", () => loadChannels().catch((err) => showActionError(err)));
    if (refs.reloadBrowserBtn) refs.reloadBrowserBtn.addEventListener("click", () => loadBrowser().catch((err) => showActionError(err)));
    if (refs.detectBrowserInstallBtn) refs.detectBrowserInstallBtn.addEventListener("click", () => detectBrowserInstall().catch((err) => showActionError(err)));
    if (refs.launchBrowserBtn) refs.launchBrowserBtn.addEventListener("click", () => launchConfiguredBrowser().catch((err) => showActionError(err)));
    if (refs.disconnectBrowserBtn) refs.disconnectBrowserBtn.addEventListener("click", () => disconnectConfiguredBrowser().catch((err) => showActionError(err)));
    if (refs.installManagedBrowserBtn) refs.installManagedBrowserBtn.addEventListener("click", () => installManagedBrowser().catch((err) => showActionError(err)));
    if (refs.reinstallManagedBrowserBtn) refs.reinstallManagedBrowserBtn.addEventListener("click", () => reinstallManagedBrowser().catch((err) => showActionError(err)));
    if (refs.removeManagedBrowserBtn) refs.removeManagedBrowserBtn.addEventListener("click", () => removeManagedBrowser().catch((err) => showActionError(err)));
    if (refs.cancelManagedBrowserBtn) refs.cancelManagedBrowserBtn.addEventListener("click", () => cancelManagedBrowserInstall().catch((err) => showActionError(err)));
    if (refs.reloadWorkspaceTreeBtn) refs.reloadWorkspaceTreeBtn.addEventListener("click", () => loadWorkspaceTree(true).catch((err) => showActionError(err)));
    if (refs.workspaceTreeSearch) refs.workspaceTreeSearch.addEventListener("input", () => {
      state.workspaceTreeSearch = String(refs.workspaceTreeSearch.value || "");
      loadWorkspaceTree(false).catch((err) => showActionError(err));
    });
    if (refs.workspaceEditBtn) refs.workspaceEditBtn.addEventListener("click", () => setWorkspaceEditMode(true));
    if (refs.workspaceCancelBtn) refs.workspaceCancelBtn.addEventListener("click", () => {
      state.workspaceMode = "preview";
      state.workspaceDirty = false;
      if (state.workspaceSelectedPath) {
        loadWorkspaceFile(state.workspaceSelectedPath).catch((err) => showActionError(err));
      } else {
        renderWorkspaceBrowser();
      }
    });
    if (refs.workspaceSaveBtn) refs.workspaceSaveBtn.addEventListener("click", () => saveWorkspaceFile().catch((err) => showActionError(err)));
    if (refs.workspaceEditor) refs.workspaceEditor.addEventListener("input", () => {
      state.workspaceContent = String(refs.workspaceEditor.value || "");
      state.workspaceDirty = true;
      renderWorkspaceBrowser();
    });
    if (refs.closeTaskBoardModalBtn) refs.closeTaskBoardModalBtn.addEventListener("click", () => closeTaskBoardModal());
    if (refs.taskBoardModal) {
      refs.taskBoardModal.addEventListener("click", (event) => {
        if (event.target === refs.taskBoardModal) closeTaskBoardModal();
      });
    }
    if (refs.saveChannelBtn) refs.saveChannelBtn.addEventListener("click", () => saveChannelConfig().catch((err) => showActionError(err)));
    if (refs.cancelChannelBtn) refs.cancelChannelBtn.addEventListener("click", () => closeChannelDrawer());
    if (refs.closeChannelDrawerBtn) refs.closeChannelDrawerBtn.addEventListener("click", () => closeChannelDrawer());
    if (refs.channelDrawer) {
      refs.channelDrawer.addEventListener("click", (event) => {
        if (event.target === refs.channelDrawer) closeChannelDrawer();
      });
    }
    refs.reloadSkillsBtn.addEventListener("click", () => loadSkills().catch((err) => showActionError(err)));
    if (refs.openSkillsStoreBtn) {
      refs.openSkillsStoreBtn.addEventListener("click", () => {
        toggleSkillsStore();
      });
    }
    if (refs.closeSkillsStoreBtn) refs.closeSkillsStoreBtn.addEventListener("click", () => toggleSkillsStore(false));
    if (refs.refreshMcpBtn) refs.refreshMcpBtn.addEventListener("click", () => loadMcp().catch((err) => showActionError(err)));
    if (refs.newLocalMcpBtn) refs.newLocalMcpBtn.addEventListener("click", () => openMcpModal({ mode: "local" }));
    if (refs.newRemoteMcpBtn) refs.newRemoteMcpBtn.addEventListener("click", () => openMcpModal({ mode: "remote" }));
    if (refs.closeMcpModalBtn) refs.closeMcpModalBtn.addEventListener("click", () => closeMcpModal());
    if (refs.cancelMcpModalBtn) refs.cancelMcpModalBtn.addEventListener("click", () => closeMcpModal());
    if (refs.saveMcpClientBtn) refs.saveMcpClientBtn.addEventListener("click", () => saveMcpClient().catch((err) => showActionError(err)));
    if (refs.mcpClientModeSelect) refs.mcpClientModeSelect.addEventListener("change", () => refreshMcpEditorUi());
    if (refs.mcpClientServerSelect) refs.mcpClientServerSelect.addEventListener("change", () => refreshMcpEditorUi());
    if (refs.mcpClientCommandInput) refs.mcpClientCommandInput.addEventListener("input", () => refreshMcpEditorUi());
    if (refs.mcpModal) {
      refs.mcpModal.addEventListener("click", (event) => {
        if (event.target === refs.mcpModal) closeMcpModal();
      });
    }
    refs.reloadModelsBtn.addEventListener("click", () => loadModels().catch((err) => showActionError(err)));
    refs.newModelBtn.addEventListener("click", () => openModelModal());
    refs.closeModelModalBtn.addEventListener("click", () => closeModelModal());
    refs.cancelModelModalBtn.addEventListener("click", () => closeModelModal());
    refs.saveModelProfileBtn.addEventListener("click", () => saveModelProfile().catch((err) => showActionError(err)));
    refs.modelProviderSelect.addEventListener("change", () => {
      const modelType = String(refs.modelTypeSelect?.value || state.modelEditor?.modelType || getSelectedModelType()).trim() || "text_generation";
      applyProviderPreset(refs.modelProviderSelect.value, true, modelType);
    });
    if (refs.modelTypeSelect) {
      refs.modelTypeSelect.addEventListener("change", () => {
        const modelType = String(refs.modelTypeSelect.value || "text_generation").trim() || "text_generation";
        if (state.modelEditor) state.modelEditor.modelType = modelType;
        renderModelProviderSelect(modelType, "");
        const first = getProvidersForModelType(modelType)[0];
        if (first) {
          refs.modelProviderSelect.value = first.provider;
          applyProviderPreset(first.provider, true, modelType);
        } else {
          refs.modelBaseUrlInput.value = "";
          refs.modelNameInput.value = "";
        }
        refreshModelModalText();
      });
    }
    refs.modelModal.addEventListener("click", (event) => {
      if (event.target === refs.modelModal) closeModelModal();
    });
    if (refs.runSearchBtn) refs.runSearchBtn.addEventListener("click", () => runSearch().catch((err) => showActionError(err)));
    if (refs.reindexSearchBtn) refs.reindexSearchBtn.addEventListener("click", () => reindexSearch().catch((err) => showActionError(err)));
    if (refs.refreshSearchStatusBtn) refs.refreshSearchStatusBtn.addEventListener("click", () => loadSearchStatus().catch((err) => showActionError(err)));
    if (refs.searchInput) {
      refs.searchInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") runSearch().catch((err) => showActionError(err));
      });
    }
    if (refs.refreshBillingBtn) refs.refreshBillingBtn.addEventListener("click", () => reloadBilling(false).catch((err) => showActionError(err)));
    if (refs.applyBillingFiltersBtn) refs.applyBillingFiltersBtn.addEventListener("click", () => reloadBilling(true).catch((err) => showActionError(err)));
    if (refs.billingQuickRange) {
      refs.billingQuickRange.addEventListener("change", () => {
        applyBillingQuickRange(refs.billingQuickRange.value);
        reloadBilling(true).catch((err) => showActionError(err));
      });
    }
    if (refs.billingPrevBtn) {
      refs.billingPrevBtn.addEventListener("click", () => {
        const totalPages = Math.max(1, Math.ceil((state.billingTotal || 0) / 20));
        state.billingPage = Math.max(1, Math.min(totalPages, (state.billingPage || 1) - 1));
        loadBillingCalls().catch((err) => showActionError(err));
      });
    }
    if (refs.billingNextBtn) {
      refs.billingNextBtn.addEventListener("click", () => {
        const totalPages = Math.max(1, Math.ceil((state.billingTotal || 0) / 20));
        state.billingPage = Math.max(1, Math.min(totalPages, (state.billingPage || 1) + 1));
        loadBillingCalls().catch((err) => showActionError(err));
      });
    }
    if (refs.closeBillingDetailBtn) refs.closeBillingDetailBtn.addEventListener("click", () => closeBillingDetail());
    if (refs.billingDetailModal) {
      refs.billingDetailModal.addEventListener("click", (event) => {
        if (event.target === refs.billingDetailModal) closeBillingDetail();
      });
    }
    if (refs.closeImagePreviewBtn) refs.closeImagePreviewBtn.addEventListener("click", () => closeImagePreview());
    if (refs.imagePreviewModal) {
      refs.imagePreviewModal.addEventListener("click", (event) => {
        if (event.target === refs.imagePreviewModal) closeImagePreview();
      });
    }
    if (refs.closeNoticeModalBtn) refs.closeNoticeModalBtn.addEventListener("click", () => closeNoticeModal());
    if (refs.confirmNoticeModalBtn) refs.confirmNoticeModalBtn.addEventListener("click", () => closeNoticeModal());
    if (refs.noticeModal) {
      refs.noticeModal.addEventListener("click", (event) => {
        if (event.target === refs.noticeModal) closeNoticeModal();
      });
    }
    document.addEventListener("keydown", (event) => {
      const settingsDrawer = document.getElementById("settingsDrawer");
      if (event.key === "Escape" && settingsDrawer && !settingsDrawer.classList.contains("hidden")) {
        ThemeManager.closeSettings();
        return;
      }
      if (event.key === "Escape" && refs.channelDrawer && !refs.channelDrawer.classList.contains("hidden")) {
        closeChannelDrawer();
        return;
      }
      if (event.key === "Escape" && refs.billingDetailModal && !refs.billingDetailModal.classList.contains("hidden")) {
        closeBillingDetail();
        return;
      }
      if (event.key === "Escape" && refs.imagePreviewModal && !refs.imagePreviewModal.classList.contains("hidden")) {
        closeImagePreview();
        return;
      }
      if (event.key === "Escape" && refs.taskBoardModal && !refs.taskBoardModal.classList.contains("hidden")) {
        closeTaskBoardModal();
        return;
      }
      if (event.key === "Escape" && refs.noticeModal && !refs.noticeModal.classList.contains("hidden")) {
        closeNoticeModal();
        return;
      }
      if (event.key === "Escape" && refs.mcpModal && !refs.mcpModal.classList.contains("hidden")) {
        closeMcpModal();
        return;
      }
      if (event.key === "Escape" && !refs.modelModal.classList.contains("hidden")) {
        closeModelModal();
      }
    });
    window.addEventListener("beforeunload", () => {
      stopBillingAutoRefresh();
      stopSessionAutoRefresh();
      try {
        stopVoiceInput();
      } catch {
        // Ignore cleanup failures.
      }
      cleanupVoiceStream();
    });
  }

  async function refreshSelectedSessionMessages(force = false) {
    if (!state.selected) return false;
    const userId = String(state.selected.user_id || "");
    const sessionName = String(state.selected.session_name || "");
    if (!userId || !sessionName) return false;

    const qs = new URLSearchParams({ user_id: userId, session_name: sessionName });
    const data = await api(`/api/v1/sessions/messages?${qs.toString()}`);
    const preferredRows = Array.isArray(data.render_messages) ? data.render_messages : [];
    const fallbackRows = Array.isArray(data.messages) ? data.messages : [];
    let normalized = normalizeMessages(preferredRows.length ? preferredRows : fallbackRows);
    if (!normalized.length && fallbackRows.length && preferredRows !== fallbackRows) {
      normalized = normalizeMessages(fallbackRows);
    }

    const sig = buildMessageSignature(normalized);
    if (!force && sig === state.selectedSessionMsgSig) return false;
    state.selectedSessionMsgSig = sig;
    state.messages = normalized;
    state.pendingThinkingByType = {};
    renderMessages();
    return true;
  }

  function stopSessionAutoRefresh() {
    if (state.sessionAutoRefreshTimer) {
      clearInterval(state.sessionAutoRefreshTimer);
      state.sessionAutoRefreshTimer = null;
    }
  }

  function startSessionAutoRefresh() {
    stopSessionAutoRefresh();
    if (state.view !== "chat") return;
    state.sessionAutoRefreshTimer = setInterval(() => {
      if (state.view !== "chat") return;
      if (!state.selected) return;
      // Avoid overriding streaming UI while an active request is running.
      if (state.currentRequestId) return;
      refreshSelectedSessionMessages(false).catch((err) => {
        console.warn("session auto refresh failed", err);
      });
      refreshSelectedSessionTasks(false).catch((err) => {
        console.warn("task board auto refresh failed", err);
      });
    }, Number(state.sessionAutoRefreshMs || 1500));
  }

  // Theme system with compatibility color presets.
  const THEME_CONFIG = {
    modes: ['light', 'dark', 'auto'],
  };

  const ThemeManager = {
    init() {
      this.setMode(state.themeMode, false);
      this.updateModeButtons();
    },

    setMode(mode, save = true) {
      const normalizedMode = normalizeThemeMode(mode);
      if (!THEME_CONFIG.modes.includes(normalizedMode)) return;
      state.themeMode = normalizedMode;

      let effectiveTheme = normalizedMode;
      if (normalizedMode === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        effectiveTheme = prefersDark ? 'dark' : 'light';
      }

      document.documentElement.setAttribute('data-theme', effectiveTheme);
      if (save) localStorage.setItem('themeMode', normalizedMode);
      this.updateModeButtons();
    },

    updateModeButtons() {
      const currentMode = normalizeThemeMode(state.themeMode);
      document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === currentMode);
      });
    },

    openSettings() {
      const drawer = document.getElementById('settingsDrawer');
      if (drawer) drawer.classList.remove('hidden');
    },

    closeSettings() {
      const drawer = document.getElementById('settingsDrawer');
      if (drawer) drawer.classList.add('hidden');
    }
  };

  // Settings drawer handlers
  function bindSettingsEvents() {
    const settingsBtn = document.getElementById('settingsBtn');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const settingsDrawer = document.getElementById('settingsDrawer');

    if (settingsBtn) {
      settingsBtn.addEventListener('click', (event) => {
        event.preventDefault();
        ThemeManager.openSettings();
      });
    }

    if (closeSettingsBtn) {
      closeSettingsBtn.addEventListener('click', () => ThemeManager.closeSettings());
    }

    if (settingsDrawer) {
      settingsDrawer.addEventListener('click', (e) => {
        if (e.target === settingsDrawer) ThemeManager.closeSettings();
      });
    }

    // Theme mode buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        ThemeManager.setMode(mode);
        saveRuntimeSettings().catch((err) => console.warn("save settings failed", err));
      });
    });

    if (refs.replyLanguageSelect) {
      refs.replyLanguageSelect.value = state.replyLanguage;
      refs.replyLanguageSelect.addEventListener("change", () => {
        const next = String(refs.replyLanguageSelect.value || "").trim().toLowerCase();
        state.replyLanguage = next === "en" ? "en" : "zh";
        localStorage.setItem("WeClaw_reply_language", state.replyLanguage);
        saveRuntimeSettings().catch((err) => console.warn("save settings failed", err));
      });
    }

    // Listen for system theme changes when in auto mode
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const currentMode = normalizeThemeMode(state.themeMode);
      if (currentMode === 'auto') {
        ThemeManager.setMode('auto', false);
      }
    });
  }

  async function boot() {
    bindEvents();
    try {
      await loadRuntimeSettings();
    } catch (err) {
      console.warn("load settings failed", err);
    }
    ThemeManager.init();
    bindSettingsEvents();
    if (refs.replyLanguageSelect) refs.replyLanguageSelect.value = state.replyLanguage;
    document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
    applyI18n();
    await loadHealth();
    await loadSessions();
    await loadChannels();
    await loadBrowser();
    await loadWorkspaceTree();
    await loadAlarms();
    await loadSkills();
    await loadModels();
    await loadSearchStatus();
    if (refs.billingQuickRange) refs.billingQuickRange.value = "12h";
    applyBillingQuickRange("12h");
    readBillingFilters(true);
    await loadBillingStatus();
    updateVoiceUi();
    if (!state.hasExplicitView) {
      setView("chat");
    }
    // Initialize page title without animation
    const titleEl = document.getElementById("pageTitle");
    if (titleEl) {
      const titleMap = PAGE_TITLES["chat"];
      if (titleMap) {
        titleEl.textContent = state.lang === "zh" ? titleMap.zh : titleMap.en;
      }
    }
  }

  boot().catch((err) => {
    console.error(err);
    showActionError(err, "init_failed");
  });
})();
