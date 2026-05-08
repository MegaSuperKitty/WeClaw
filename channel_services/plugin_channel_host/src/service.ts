import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import type {
  BridgeHealthResponse,
  BridgeInboundMessage,
  BridgeOutboundMessage,
} from "./bridge_types.js";
import { GatewayBridgeClient } from "./bridge_client.js";
import { HostInboundAdapter } from "./inbound-adapter.js";
import { HostOutboundAdapter } from "./outbound-adapter.js";
import { HostPluginLoader, type HostChannelPlugin } from "./plugin-loader.js";

type PluginChannelHostServiceOptions = {
  host: string;
  port: number;
  gatewayBaseUrl: string;
  pluginDirs?: string[];
};

async function readJson<T>(req: IncomingMessage): Promise<T> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  const text = Buffer.concat(chunks).toString("utf-8").trim();
  return (text ? JSON.parse(text) : {}) as T;
}

function writeJson(res: ServerResponse, statusCode: number, payload: unknown): void {
  const body = JSON.stringify(payload);
  res.statusCode = statusCode;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.end(body);
}

export class PluginChannelHostService {
  private readonly host: string;
  private readonly port: number;
  private readonly gateway: GatewayBridgeClient;
  private readonly inboundAdapter = new HostInboundAdapter();
  private readonly outboundAdapter = new HostOutboundAdapter();
  private readonly pluginLoader = new HostPluginLoader(this.outboundAdapter);
  private readonly pluginDirs: string[];
  private pollTimer: NodeJS.Timeout | null = null;

  constructor(options: PluginChannelHostServiceOptions) {
    this.host = options.host;
    this.port = options.port;
    this.gateway = new GatewayBridgeClient({ gatewayBaseUrl: options.gatewayBaseUrl });
    this.pluginDirs = Array.isArray(options.pluginDirs) ? options.pluginDirs : [];
  }

  async bootstrap(): Promise<void> {
    await this.pluginLoader.loadPluginDirectories(this.pluginDirs);
  }

  listen(): void {
    const server = createServer(async (req, res) => {
      try {
        await this.handle(req, res);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        writeJson(res, 500, { ok: false, error: message });
      }
    });
    server.listen(this.port, this.host, () => {
      // eslint-disable-next-line no-console
      console.log(
        `[plugin_channel_host] listening on http://${this.host}:${this.port} -> gateway ${this.gateway.gatewayBaseUrl}`,
      );
    });
    this.startPollingOutbound();
  }

  async registerPlugin(plugin: HostChannelPlugin): Promise<void> {
    await this.pluginLoader.register(plugin);
  }

  private async handle(req: IncomingMessage, res: ServerResponse): Promise<void> {
    const method = req.method ?? "GET";
    const url = req.url ?? "/";

    if (method === "GET" && url === "/healthz") {
      const payload: BridgeHealthResponse = {
        ok: true,
        service: "plugin_channel_host",
        now: new Date().toISOString(),
        channels: this.pluginLoader.listChannels(),
      };
      writeJson(res, 200, payload);
      return;
    }

    if (method === "POST" && url === "/bridge/inbound") {
      const payload = await readJson<BridgeInboundMessage>(req);
      const normalized = this.inboundAdapter.normalize(payload);
      await this.pluginLoader.notifyInbound(normalized.bridgeMessage);
      await this.gateway.sendInboundMessage(normalized.bridgeMessage);
      writeJson(res, 202, { ok: true });
      return;
    }

    if (method === "POST" && url === "/bridge/outbound") {
      const payload = await readJson<BridgeOutboundMessage>(req);
      const delivered = await this.outboundAdapter.deliver(payload);
      if (!delivered) {
        // eslint-disable-next-line no-console
        console.log("[plugin_channel_host] outbound payload", JSON.stringify(payload));
      }
      writeJson(res, 202, { ok: true });
      return;
    }

    writeJson(res, 404, { ok: false, error: "not_found" });
  }

  private startPollingOutbound(): void {
    if (this.pollTimer) {
      return;
    }
    this.pollTimer = setInterval(() => {
      void this.pollOutbound().catch((error) => {
        const message = error instanceof Error ? error.message : String(error);
        // eslint-disable-next-line no-console
        console.error("[plugin_channel_host] outbound poll failed:", message);
      });
    }, 1500);
  }

  private async pollOutbound(): Promise<void> {
    const message = await this.gateway.pullOutboundMessage({});
    if (!message) {
      return;
    }
    const delivered = await this.outboundAdapter.deliver(message);
    if (!delivered) {
      // eslint-disable-next-line no-console
      console.log("[plugin_channel_host] pulled outbound message", JSON.stringify(message));
    }
  }
}
