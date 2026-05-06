import type { BridgeOutboundMessage } from "./bridge_types.js";

export type HostOutboundHandler = {
  channel: string;
  deliver: (message: BridgeOutboundMessage) => Promise<void> | void;
};

export class HostOutboundAdapter {
  private readonly handlers = new Map<string, HostOutboundHandler>();

  register(handler: HostOutboundHandler): void {
    this.handlers.set(handler.channel, handler);
  }

  listChannels(): string[] {
    return Array.from(this.handlers.keys()).sort();
  }

  async deliver(message: BridgeOutboundMessage): Promise<boolean> {
    const handler = this.handlers.get(message.channel);
    if (!handler) {
      return false;
    }
    await handler.deliver(message);
    return true;
  }
}
