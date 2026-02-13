# Aashi - Your Personal Jarvish

Aashi is a structured, modular personal assistant you can run locally from terminal.

## Architecture
- `aashi/config.py` - runtime config (memory path, voice folder, model)
- `aashi/memory.py` - persistent state store (`notes`, voice settings)
- `aashi/voice.py` - system voice and custom audio-file playback
- `aashi/ai.py` - optional OpenAI response provider
- `aashi/assistant.py` - command routing and assistant orchestration
- `main.py` - terminal chat runner

## Features
- Clean command-based assistant loop
- Local memory persistence in `aashi_memory.json`
- Offline-first operation
- Optional cloud AI responses (`OPENAI_API_KEY`)
- Voice output with system voices or your own file from `./save`

## Quick Start

```bash
cd "/Users/abhishekkumar/Documents/New project"
python3 -m venv .venv
source .venv/bin/activate
python3 main.py
```

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
- `voicefiles`
- `voicefile <filename>`
- `voice on`
- `voice off`
- `exit` / `quit`

## Custom Voice File
1. Put your file in `./save` (for example `myvoice.wav` or `myvoice.mp3`).
2. In Aashi:
   - `voicefiles`
   - `voicefile myvoice.wav`
   - `voice on`

Aashi will play your selected file for each response in file mode.

## Optional OpenAI Setup
If you want dynamic AI responses (internet required):

```bash
pip install openai
export OPENAI_API_KEY="your_key_here"
python3 main.py
```
