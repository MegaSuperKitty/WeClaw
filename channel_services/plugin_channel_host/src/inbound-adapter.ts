import type { BridgeInboundMessage } from "./bridge_types.js";
import { resolveSessionRoute, type HostSessionRoute } from "./session-route.js";

export type NormalizedInboundEnvelope = {
  route: HostSessionRoute;
  bridgeMessage: BridgeInboundMessage;
};

export class HostInboundAdapter {
  normalize(message: BridgeInboundMessage): NormalizedInboundEnvelope {
    return {
      route: resolveSessionRoute(message),
      bridgeMessage: {
        ...message,
        account_id: String(message.account_id || "default"),
        thread_id: message.thread_id ?? null,
        message: {
          ...message.message,
          attachments: Array.isArray(message.message.attachments) ? message.message.attachments : [],
        },
      },
    };
  }
}
