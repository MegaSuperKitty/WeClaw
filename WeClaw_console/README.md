# WeClaw Console

Browser-based management console for WeClaw.

## Start

From the project root:

```powershell
python -m pip install -r requirements.txt
python entry_weclaw_console.py
```

Alternative package entry:

```powershell
python -m WeClaw_console
```

Open `http://127.0.0.1:7788`.

## Positioning

The Web Console is the primary entrypoint for the project. Use it to:

- start chat sessions
- configure model profiles
- manage files, search, cron, and heartbeat
- configure and launch QQ and Discord channels
- keep direct channel scripts as advanced entrypoints only

## Direct Channel Scripts

```powershell
python channels/cli.py
python channels/adapters/qq.py
python channels/adapters/discord.py
```

## Notes

- Default bind host is `127.0.0.1`.
- Default port is `7788`.
- Existing `qq:*`, `cli:*`, and `web:*` sessions remain visible in the console.
- Runtime data is resolved from `WE_CLAW_HOME` / `~/.weclaw`, not the old project-root state directories.
