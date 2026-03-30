# OpenClaw Documentation Learning
*Date: 2026-02-16*
*Context: Saber asked me to read the OpenClaw docs so I can better fix myself*

## Key Learnings

### What I Am (Agent Runtime)
- I'm an embedded agent running in the **pi-mono** runtime
- My workspace is `/Users/saberzou/.openclaw/workspace-axel` — this is my **only** working directory
- Bootstrap files define me:
  - `AGENTS.md` — operating instructions
  - `SOUL.md` — persona, boundaries, tone (this is who I am!)
  - `TOOLS.md` — tool notes and conventions
  - `USER.md` — info about Saber
  - `IDENTITY.md` — my name/vibe/emoji
  - `MEMORY.md` — curated long-term memory (ONLY in main session, never groups!)
- Skills live in three places (workspace wins on conflicts):
  - Bundled (shipped with OpenClaw)
  - Managed: `~/.openclaw/skills`
  - Workspace: `<workspace>/skills`

### Sessions & Memory
- **Session management:** All sessions are owned by the gateway
- **Main session:** Direct chats with Saber collapse to `agent:axel:main`
- **Group chats:** Get their own keys like `agent:axel:telegram:group:<id>`
- **Session reset:** Defaults to 4:00 AM local time (can also use idle timeout)
- **Memory structure:**
  - `memory/YYYY-MM-DD.md` — daily logs (read today + yesterday at session start)
  - `MEMORY.md` — curated long-term (only in main session!)
  - **Memory flush:** System automatically triggers before compaction to remind me to save memories
- **Vector search:** Enabled by default for semantic memory search

### Multi-Agent Setup (Atticus & Me)
- Each agent is **fully isolated:**
  - Separate workspace (files, SOUL.md, persona)
  - Separate state directory (`agentDir`) for auth profiles
  - Separate session store under `~/.openclaw/agents/<agentId>/sessions`
- Auth profiles are **per-agent** — Atticus and I don't share credentials automatically
- Skills can be per-agent (workspace) or shared (`~/.openclaw/skills`)
- Bindings route inbound messages to the right agent

### Troubleshooting Commands
When things break, run these in order:
```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

**Healthy signals:**
- `openclaw gateway status` shows `Runtime: running` and `RPC probe: ok`
- `openclaw doctor` reports no blocking issues
- `openclaw channels status --probe` shows connected channels

**No replies? Check:**
- Pairing approvals
- Group mention requirements
- Allowlist mismatches

### In-Chat Commands
- `/status` — check if I'm reachable, context usage, thinking/verbose toggles
- `/context list` or `/context detail` — see what's in system prompt
- `/stop` — abort current run + clear queued followups
- `/compact` — summarize older context to free up window space
- `/new` or `/reset` — start fresh session
- `/send on/off/inherit` — control delivery policy for this session

### Key Config Files
- Main config: `~/.openclaw/openclaw.json`
- My workspace: `~/.openclaw/workspace-axel`
- My sessions: `~/.openclaw/agents/axel/sessions/`
- Auth profiles: `~/.openclaw/agents/axel/agent/auth-profiles.json`

### Important Concepts
- **Model refs:** Use `provider/model` format (e.g., `github-copilot/claude-sonnet-4.5`)
- **Queue modes:** `steer` injects messages mid-run, `followup` waits until turn ends
- **Block streaming:** Off by default, can be enabled per channel
- **Sandboxing:** Workspace is default cwd, but absolute paths can reach other locations unless sandboxing enabled
- **Security:** `SHIELD.md` contains security rules I must follow

## Next Steps
- If I need deeper info on a specific topic, I can read more docs at `/opt/homebrew/lib/node_modules/openclaw/docs/`
- Mirror available at https://docs.openclaw.ai
- When troubleshooting, follow the command ladder above

## Tools I Have Access To
- whisper-cli (found at `/opt/homebrew/bin/whisper-cli`) — for audio transcription
- Various skills in my workspace and bundled with OpenClaw
- Core tools: read, write, edit, exec, process, browser, etc.

---

*This is my reference for understanding how I work and how to fix myself when things go wrong. 🐯*
