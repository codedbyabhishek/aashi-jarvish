# Aashi - Your Personal Jarvish

Aashi is a structured, modular personal assistant you can run locally from terminal or desktop UI.

## Architecture
- `aashi/config.py` - runtime config (memory path, voice folder, model)
- `aashi/memory.py` - persistent state store (`notes`, voice settings)
- `aashi/ai.py` - AI brain (OpenAI LLM responder)
- `aashi/voice_input.py` - voice input (transcribe command audio files)
- `aashi/voice.py` - voice output (system voice and file playback)
- `aashi/clone_voice.py` - cloned voice output via ElevenLabs
- `aashi/system_control.py` - system actions (open apps/web, run shortcuts)
- `aashi/pipeline/input_layer.py` - normalize incoming input
- `aashi/pipeline/router.py` - intent detection + routing
- `aashi/pipeline/brain.py` - LLM reasoning layer
- `aashi/pipeline/planner.py` - task planning layer
- `aashi/pipeline/tools.py` - tool executor layer
- `aashi/pipeline/response.py` - response generation
- `aashi/assistant.py` - orchestrates the full pipeline
- `aashi/gui.py` - desktop UI (chat + controls)
- `main.py` - terminal runner
- `run_ui.py` - UI runner

## End-to-End Flow
- User Voice/Text
- Input Layer (Speech-to-Text)
- Intent Detection + Router
- AI Brain (LLM + Memory)
- Task Planner (Agent)
- Tool Executor Layer
- Response Generator
- Text-to-Speech

## Quick Start
```bash
cd "/Users/abhishekkumar/Documents/New project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run_ui.py
```

## ASHI Command Center UI
- 3-panel holographic command-center layout
- Animated ASHI core + waveform + live status indicators
- Activity rail for operational events
- Command history with `Up`/`Down`
- Keyboard shortcuts:
  - `Ctrl+Enter` -> execute input
  - `Ctrl+L` -> clear console
  - `Esc` -> focus command input
- Preset tactical buttons for common checks

## Commands
- `help`
- `time`
- `date`
- `notes`
- `save <text>`
- `voices`
- `voice <name>`
- `voice mode system`
- `voice mode file`
- `voice mode clone`
- `voicefiles`
- `voicefile <filename>`
- `listen <filename>`
- `clonevoice <filename> [name]`
- `clone status`
- `wake on`
- `wake off`
- `wake status`
- `wake phrase <text>`
- `setup openai`
- `setup elevenlabs`
- `setup status`
- `open app <name>`
- `open web <url>`
- `search web <query>`
- `run shortcut <name>`
- `voice on`
- `voice off`
- `exit` / `quit`

## Setup For Full Capabilities

### AI Brain + Voice Input (OpenAI)
```bash
pip install openai
export OPENAI_API_KEY="your_key_here"
```

### Cloned Voice Output (ElevenLabs)
```bash
export ELEVENLABS_API_KEY="your_key_here"
```

### Your Own Voice File
Put `.wav`/`.mp3` in `./save`, then in Aashi:
- `voicefile yourfile.wav`
- `clonevoice yourfile.wav Aashi Clone` (optional)
- `voice mode clone` (or `voice mode file`)
- `voice on`

## Wake-Word Flow (File Voice Input)
1. Add voice sample in `./save`.
2. Say command in audio including wake phrase (default: `hey aashi`).
3. Run `listen your_audio.wav`.
4. ASHI validates wake phrase and executes the detected command.
