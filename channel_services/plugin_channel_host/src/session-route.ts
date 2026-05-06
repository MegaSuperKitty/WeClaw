import type { BridgeInboundMessage } from "./bridge_types.js";

export type HostSessionRoute = {
  channel: string;
  accountId: string;
  peerKind: BridgeInboundMessage["conversation"]["peer_kind"];
  peerId: string;
  senderId: string;
  threadId?: string | null;
};

export function resolveSessionRoute(message: BridgeInboundMessage): HostSessionRoute {
  return {
    channel: message.channel,
    accountId: message.account_id,
    peerKind: message.conversation.peer_kind,
    peerId: message.conversation.peer_id,
    senderId: message.sender.user_id,
    threadId: message.thread_id ?? null,
  };
}
