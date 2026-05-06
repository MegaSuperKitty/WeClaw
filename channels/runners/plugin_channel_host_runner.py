# -*- coding: utf-8 -*-
"""Runner for the workspace-backed plugin channel host."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from channels.common import AGENT_ID
from integrations.plugin_channel_host import PluginChannelHostRuntime


def main() -> None:
    runtime = PluginChannelHostRuntime(str(PROJECT_ROOT), agent_id=AGENT_ID)
    prepared = runtime.ensure_ready()

    env = os.environ.copy()
    env.setdefault("WECLAW_PLUGIN_CHANNEL_PLUGIN_DIRS", os.pathsep.join(runtime.runtime_plugin_dirs()))

    completed = subprocess.run(
        [prepared.node_bin, prepared.dist_entry],
        cwd=prepared.runtime_root,
        check=False,
        env=env,
    )
    raise SystemExit(int(completed.returncode or 0))


if __name__ == "__main__":
    main()
