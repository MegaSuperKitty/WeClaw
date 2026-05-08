import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const runtimeDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "runtime");
const inboundLog = path.join(runtimeDir, "inbound.jsonl");
const outboundLog = path.join(runtimeDir, "outbound.jsonl");

function appendJsonLine(filePath, payload) {
  fs.mkdirSync(runtimeDir, { recursive: true });
  fs.appendFileSync(filePath, `${JSON.stringify(payload)}\n`, "utf-8");
}

export default {
  channel: "echo",
  setup() {
    fs.mkdirSync(runtimeDir, { recursive: true });
  },
  onInbound(message) {
    appendJsonLine(inboundLog, {
      ts: new Date().toISOString(),
      message,
    });
  },
  onOutbound(message) {
    appendJsonLine(outboundLog, {
      ts: new Date().toISOString(),
      message,
    });
  },
};
