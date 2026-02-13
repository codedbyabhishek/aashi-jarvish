# Aashi - Your Personal Jarvish

Aashi is a lightweight personal assistant you can run locally from terminal.

## Features
- Natural chat loop in terminal
- Name/identity as **Aashi**
- Built-in commands (`help`, `time`, `date`, `notes`, `save`, `exit`)
- Local memory persistence in `aashi_memory.json`
- Optional OpenAI-powered responses if `OPENAI_API_KEY` is set and `openai` package is installed
- Voice output with either macOS system voice or your own audio file from `./save`

## Quick Start

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Run Aashi directly (works fully offline):

```bash
python3 main.py
```

3. Optional: enable OpenAI responses (requires internet access):

```bash
pip install openai
export OPENAI_API_KEY="your_key_here"
python3 main.py
```

## Commands
- `help` - show available commands
- `time` - current local time
- `date` - current local date
- `notes` - show saved notes
- `save <text>` - save a note
- `voices` - list available system voices
- `voice <name>` - set preferred system voice
- `voice mode system` - use system voice output
- `voice mode file` - use your own file from `./save`
- `voicefiles` - list audio files in `./save`
- `voicefile <filename>` - select an audio file from `./save`
- `voice on` / `voice off` - enable or disable spoken responses
- `exit` / `quit` - stop Aashi

## Your Own Voice File Setup
1. Put your file in `./save` (for example `myvoice.wav` or `myvoice.mp3`).
2. In Aashi, run:
   - `voicefiles`
   - `voicefile myvoice.wav`
   - `voice on`
3. Aashi will play your file for each response.

## Notes
- Without `OPENAI_API_KEY` and `openai`, Aashi still works with built-in assistant behavior.
- Memory is stored locally in JSON so your notes survive restarts.
- On macOS, Aashi uses `say` for system voice and `afplay` for custom audio files.
