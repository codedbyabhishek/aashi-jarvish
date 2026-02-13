# ASHI OS Phase 1

## Scope
- LLM router (Ollama primary + OpenAI fallback)
- System prompt policy
- Vector memory (Chroma)
- Context manager
- Structured logging + audit log
- FastAPI service for chat and memory endpoints

## Run
```bash
cd "/Users/abhishekkumar/Documents/New project"
source .venv/bin/activate
pip install -e .
uvicorn ashi_os.api.app:app --reload --port 8787
```

## Endpoints
- `GET /health`
- `GET /status/providers`
- `POST /chat`
- `POST /memory/add`
- `POST /memory/search`
- `POST /voice/command-file`

## Quick Test
```bash
curl -s http://127.0.0.1:8787/health

curl -s -X POST http://127.0.0.1:8787/chat \
  -H 'content-type: application/json' \
  -d '{"session_id":"demo","user_message":"Create a 3-step plan to set up wake word"}'
```

## Security Notes
- Secrets are loaded from env, never hardcoded.
- Audit logs redact token-like patterns.
- Destructive command patterns are blocked with confirmation requirement.

## Startup Performance
- `MEMORY_ON_CHAT=false` (default) keeps chat startup non-blocking.
- Semantic memory retrieval runs only when you call memory endpoints.
- Set `MEMORY_ON_CHAT=true` after first embedding model warm-up if desired.

## Phase 2 Voice Interface (Scaffold)
- `ashi_os/voice/stt.py`: speech-to-text from file (OpenAI transcription)
- `ashi_os/voice/wake_word.py`: wake phrase parsing (`hey aashi`)
- `ashi_os/voice/tts.py`: text-to-speech via macOS `say`
- `ashi_os/voice/listener.py`: end-to-end voice command pipeline
