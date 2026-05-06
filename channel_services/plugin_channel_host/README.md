# Plugin Channel Host

这是 WeClaw 当前用于承载插件化 channel 的 TS channel service。

源码目录现在只保留源码与锁文件。真正运行时所需的 `node_modules/` 与 `dist/` 会在首次启动时由 WeClaw 安装到 workspace runtime 目录下，而不是要求源码目录自带依赖产物。

当前目录已经具备最小可验证宿主边界：

- `bridge_types.ts`：定义与 Python gateway 对接的最小 bridge payload
- `bridge_client.ts`：调用 WeClaw gateway bridge API
- `service.ts`：HTTP 服务骨架与轮询逻辑
- `inbound-adapter.ts`：入站标准化
- `outbound-adapter.ts`：出站分发适配
- `session-route.ts`：最小 session route 元数据
- `plugin-loader.ts`：后续 channel plugin 宿主入口
- `index.ts`：启动入口
- `plugins/echo_channel/`：本地插件包，用作最小联调验证对象

## 设计目标

- 不依赖外部参考项目源码运行时
- 只定义本地桥接协议
- 让 WeClaw 的 Python Gateway 以后通过服务方式对接 TS channel runtime
- 保持跨平台，优先支持 Windows 和 macOS
- 用真实 plugin package 结构验证宿主契约，而不是只停留在接口骨架

## HTTP 接口

- `GET /healthz`：健康检查
- `POST /bridge/inbound`：接收入站消息并转发给 gateway
- `POST /bridge/outbound`：直接接收一条出站消息并尝试交给已注册 channel handler
- `GET /bridge/outbound/pull`：从 gateway 拉取待投递出站消息，再交给已注册 channel handler

`/healthz` 当前也会返回已加载的 channel 列表，便于最小宿主联调。

## 当前已验证能力

- 能从 `WECLAW_PLUGIN_CHANNEL_PLUGIN_DIRS` 指定目录自动发现并加载插件包
- 能把 plugin 侧入站消息通过 bridge 转发给 Python gateway
- 能从 Python gateway 拉取 outbound final message 并交给 plugin outbound handler
- 已有 `tests/test_plugin_channel_host_plugin_package.py` 与 `tests/test_plugin_channel_host_plugin_smoke.py` 固定最小闭环

## 运行时安装位置

- 源码：`channel_services/plugin_channel_host/`
- workspace 运行时：`~/.weclaw/agents/<agent_id>/runtime/plugin_channel_host/`

当前 Console 会通过 `channels/runners/plugin_channel_host_runner.py` 调用 Python 安装器，把源码同步到 workspace runtime，再按需执行：

- `npm install`
- `npm run build`

这样 Git 仓库和源码压缩包不需要自带 `node_modules/` 与 `dist/`。

## 仍未覆盖

- 真实 OpenClaw SDK 全量兼容实现
- 持久化
- 认证
- 重试与队列

当前已经预留的扩展点：

- `plugin-loader.ts`：后续注册 channel plugin
- `outbound-adapter.ts`：按 channel 分发 outbound
- `session-route.ts`：把 inbound route 元数据集中到单一事实源

## 关联文档

- `../../WeClaw_docs/gateway/bridge-and-plugin-channel-host.md`
- `../../WeClaw_docs/channels/channel-runtime.md`
- `../../WeClaw_docs/console/chat-and-event-stream.md`

后续可以继续在这个目录下替换 `echo_channel` 为真实目标 channels，或补更完整的 OpenClaw runtime helper。
