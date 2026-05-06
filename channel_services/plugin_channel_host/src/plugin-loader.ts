import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

import type { BridgeInboundMessage, BridgeOutboundMessage } from "./bridge_types.js";
import { HostOutboundAdapter } from "./outbound-adapter.js";

export type HostChannelPlugin = {
  channel: string;
  setup?: () => Promise<void> | void;
  onInbound?: (message: BridgeInboundMessage) => Promise<void> | void;
  onOutbound?: (message: BridgeOutboundMessage) => Promise<void> | void;
};

export class HostPluginLoader {
  private readonly plugins = new Map<string, HostChannelPlugin>();
  private readonly outboundAdapter: HostOutboundAdapter;

  constructor(outboundAdapter: HostOutboundAdapter) {
    this.outboundAdapter = outboundAdapter;
  }

  async register(plugin: HostChannelPlugin): Promise<void> {
    await plugin.setup?.();
    this.plugins.set(plugin.channel, plugin);
    if (plugin.onOutbound) {
      this.outboundAdapter.register({
        channel: plugin.channel,
        deliver: plugin.onOutbound,
      });
    }
  }

  async loadPluginDirectories(pluginDirs: string[]): Promise<string[]> {
    const loaded: string[] = [];
    for (const pluginDir of pluginDirs) {
      const normalizedDir = path.resolve(pluginDir);
      if (!fs.existsSync(normalizedDir) || !fs.statSync(normalizedDir).isDirectory()) {
        continue;
      }
      const plugin = await this.loadFromDirectory(normalizedDir);
      if (!plugin) {
        continue;
      }
      loaded.push(plugin.channel);
    }
    return loaded;
  }

  listChannels(): string[] {
    return Array.from(this.plugins.keys()).sort();
  }

  async notifyInbound(message: BridgeInboundMessage): Promise<void> {
    const plugin = this.plugins.get(message.channel);
    await plugin?.onInbound?.(message);
  }

  private async loadFromDirectory(pluginDir: string): Promise<HostChannelPlugin | null> {
    const packageJsonPath = path.join(pluginDir, "package.json");
    const manifestPath = path.join(pluginDir, "openclaw.plugin.json");
    if (!fs.existsSync(packageJsonPath) || !fs.existsSync(manifestPath)) {
      return null;
    }
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf-8")) as {
      openclaw?: { extensions?: string[]; channel?: { id?: string } };
    };
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8")) as {
      kind?: string;
      id?: string;
      channels?: string[];
    };
    if (manifest.kind !== "channel") {
      return null;
    }

    const extensionEntry = packageJson.openclaw?.extensions?.[0] ?? "./index.js";
    const entryPath = path.resolve(pluginDir, extensionEntry);
    const moduleUrl = pathToFileURL(entryPath).href;
    const imported = (await import(moduleUrl)) as { default?: unknown };
    const plugin = imported.default;
    if (!plugin || typeof plugin !== "object") {
      return null;
    }
    const candidate = plugin as HostChannelPlugin;
    const expectedChannel =
      String(packageJson.openclaw?.channel?.id || "").trim() ||
      String(manifest.id || "").trim() ||
      String((manifest.channels || [])[0] || "").trim();
    if (!candidate.channel || (expectedChannel && candidate.channel !== expectedChannel)) {
      return null;
    }

    await this.register(candidate);
    return candidate;
  }
}
