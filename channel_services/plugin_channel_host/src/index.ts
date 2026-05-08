import { PluginChannelHostService } from "./service.js";
import path from "node:path";

function readInt(name: string, fallback: number): number {
  const raw = process.env[name];
  const value = Number.parseInt(String(raw ?? ""), 10);
  return Number.isFinite(value) ? value : fallback;
}

function readPluginDirs(): string[] {
  const raw = String(process.env.WECLAW_PLUGIN_CHANNEL_PLUGIN_DIRS ?? "").trim();
  if (!raw) {
    return [path.resolve(process.cwd(), "plugins", "echo_channel")];
  }
  return raw
    .split(path.delimiter)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => path.resolve(item));
}

const service = new PluginChannelHostService({
  host: process.env.WECLAW_PLUGIN_CHANNEL_HOST_BIND ?? "127.0.0.1",
  port: readInt("WECLAW_PLUGIN_CHANNEL_HOST_PORT", 8765),
  gatewayBaseUrl: process.env.WECLAW_GATEWAY_BASE_URL ?? "http://127.0.0.1:7788/api/v1",
  pluginDirs: readPluginDirs(),
});

await service.bootstrap();
service.listen();
