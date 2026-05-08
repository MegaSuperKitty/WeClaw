export type BridgePeerKind = "direct" | "group" | "channel";

export type BridgeInboundMessage = {
  type: "inbound_message";
  channel: string;
  account_id: string;
  conversation: {
    peer_kind: BridgePeerKind;
    peer_id: string;
  };
  thread_id?: string | null;
  sender: {
    user_id: string;
  };
  message: {
    message_id: string;
    text: string;
    attachments: unknown[];
  };
};

export type BridgeOutboundMessage = {
  type: "outbound_message";
  session_id: string;
  run_id: string;
  channel: string;
  account_id?: string;
  delivery: {
    account_id: string;
    to: string;
    thread_id?: string | null;
  };
  message: {
    mode: "delta" | "final";
    text: string;
  };
};

export type BridgeHealthResponse = {
  ok: true;
  service: "plugin_channel_host";
  now: string;
  channels?: string[];
};
