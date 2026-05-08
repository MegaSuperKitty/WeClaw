import type { BridgeInboundMessage, BridgeOutboundMessage } from "./bridge_types.js";

export type GatewayBridgeClientOptions = {
  gatewayBaseUrl: string;
};

export class GatewayBridgeClient {
  readonly gatewayBaseUrl: string;

  constructor(options: GatewayBridgeClientOptions) {
    this.gatewayBaseUrl = options.gatewayBaseUrl.replace(/\/+$/, "");
  }

  async sendInboundMessage(payload: BridgeInboundMessage): Promise<void> {
    const response = await fetch(`${this.gatewayBaseUrl}/bridge/inbound`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`gateway bridge inbound failed: ${response.status}`);
    }
  }

  async pullOutboundMessage(params: {
    channel?: string;
    accountId?: string;
  }): Promise<BridgeOutboundMessage | null> {
    const url = new URL(`${this.gatewayBaseUrl}/bridge/outbound/pull`);
    if (params.channel) {
      url.searchParams.set("channel", params.channel);
    }
    if (params.accountId) {
      url.searchParams.set("account_id", params.accountId);
    }
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`gateway bridge outbound pull failed: ${response.status}`);
    }
    const payload = (await response.json()) as {
      ok?: boolean;
      message?: BridgeOutboundMessage | null;
    };
    return payload.message ?? null;
  }
}
