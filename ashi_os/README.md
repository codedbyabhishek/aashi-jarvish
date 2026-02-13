# ASHI OS Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5

## Scope
- LLM router (Ollama primary + OpenAI fallback)
- System prompt policy
- Vector memory (Chroma)
- Context manager
- Structured logging + audit log
- FastAPI service for chat and memory endpoints
- Voice command pipeline (STT + wake phrase + TTS)
- Continuous listening runtime (file inbox queue)
- Tool execution layer (system/files/browser/code/email/scheduler)
- Strategic planning engine (plan decomposition + risk scoring + confirmation tokens)
- Multi-agent coordinator (research/execution/validation/memory/supervisor)

## Run
```bash
cd "/Users/abhishekkumar/Documents/New project"
source .venv/bin/activate
pip install -e .
ANONYMIZED_TELEMETRY=False uvicorn ashi_os.api.app:app --reload --port 8787
```

## Endpoints
- `GET /health`
- `GET /status/providers`
- `POST /chat`
- `POST /memory/add`
- `POST /memory/search`
- `POST /voice/command-file`
- `POST /voice/start`
- `POST /voice/stop`
- `GET /voice/status`
- `POST /voice/mic/start`
- `POST /voice/mic/stop`
- `GET /voice/mic/status`
- `GET /tools/catalog`
- `POST /tools/execute`
- `POST /scheduler/jobs`
- `GET /scheduler/jobs`
- `POST /scheduler/run-due`
- `GET /agents/status`
- `POST /agents/run`

## Startup Performance
- `MEMORY_ON_CHAT=false` (default) keeps chat startup non-blocking.
- Semantic memory retrieval runs only when you call memory endpoints.
- Set `MEMORY_ON_CHAT=true` after first embedding model warm-up if desired.

## Phase 2 Continuous Listening
Input queue folder:
- `./data/voice/inbox`

Processed archive folder:
- `./data/voice/processed`

Set env options if needed:
- `WAKE_PHRASE=hey aashi`
- `DEFAULT_TTS_VOICE=Samantha`
- `VOICE_POLL_INTERVAL_SEC=1.0`

Start continuous listener:
```bash
curl -s -X POST http://127.0.0.1:8787/voice/start \
  -H 'content-type: application/json' \
  -d '{"session_id":"voice-main","speak_reply":true}'
```

Check status:
```bash
curl -s http://127.0.0.1:8787/voice/status
```

Drop voice files (wav/mp3) into inbox:
- `./data/voice/inbox`

Stop listener:
```bash
curl -s -X POST http://127.0.0.1:8787/voice/stop
```

## Phase 2 Microphone Capture
Install mic capture dependencies:
```bash
source .venv/bin/activate
pip install sounddevice numpy
```

Start microphone chunk capture:
```bash
curl -s -X POST http://127.0.0.1:8787/voice/mic/start
```

Check mic status:
```bash
curl -s http://127.0.0.1:8787/voice/mic/status
```

Stop microphone capture:
```bash
curl -s -X POST http://127.0.0.1:8787/voice/mic/stop
```

## Security Notes
- Secrets are loaded from env, never hardcoded.
- Audit logs redact token-like patterns.
- Destructive command patterns are blocked with confirmation requirement.
- Continuous listener only executes wake-phrase gated commands.
- Filesystem tool cannot escape workspace root.
- File deletion requires explicit `confirm=true`.
- Code runner allows only safe command prefixes and blocks destructive tokens.
- High-risk chat intents trigger confirmation token challenge before execution.

## Phase 4 Chat Contract
`POST /chat` now returns planning + risk metadata:
- `plan.objective`
- `plan.steps[]`
- `risk.level` (`low|medium|high`)
- `risk.score`
- `risk.reasons[]`
- `confirmation_required`
- `confirmation_token` (when confirmation is required)

If confirmation is required, continue with:
```bash
curl -s -X POST http://127.0.0.1:8787/chat \
  -H 'content-type: application/json' \
  -d '{"session_id":"phase4","user_message":"confirm <token>"}'
```

## Phase 5 Multi-Agent Contract
Coordinator agents:
- `research` - gather memory context for objective
- `execution` - map plan steps to tool calls
- `validation` - verify execution outcomes
- `memory` - store post-run reflection
- `supervisor` - produce mission summary

Run in dry mode:
```bash
curl -s -X POST http://127.0.0.1:8787/agents/run \
  -H 'content-type: application/json' \
  -d '{"session_id":"agent-1","objective":"list files and summarize","auto_execute":false}'
```

Run with tool execution:
```bash
curl -s -X POST http://127.0.0.1:8787/agents/run \
  -H 'content-type: application/json' \
  -d '{"session_id":"agent-1","objective":"write file data/ops.txt::ready","auto_execute":true}'
```

## Phase 3 Tool Execution Examples
List supported tools:
```bash
curl -s http://127.0.0.1:8787/tools/catalog
```

Execute a safe filesystem action:
```bash
curl -s -X POST http://127.0.0.1:8787/tools/execute \\
  -H 'content-type: application/json' \\
  -d '{
    "session_id":"ops-1",
    "tool":"filesystem",
    "action":"list",
    "params":{"path":"."}
  }'
```

Schedule a job and run due tasks:
```bash
curl -s -X POST http://127.0.0.1:8787/scheduler/jobs \\
  -H 'content-type: application/json' \\
  -d '{
    "session_id":"ops-1",
    "run_at":"1970-01-01T00:00:00+00:00",
    "tool":"filesystem",
    "action":"write",
    "params":{"path":"data/phase3.txt","content":"phase3 online"}
  }'

curl -s -X POST http://127.0.0.1:8787/scheduler/run-due
```
