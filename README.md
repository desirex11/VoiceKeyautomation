# Voice keyword automations

A lightweight Python listener that transcribes microphone audio, looks for configured keywords, and triggers expansive automations without persisting transcripts. It supports OpenAI Whisper for high-quality speech recognition and a fallback SpeechRecognition/Sphinx engine.

## Setup

1. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set an OpenAI API key when using Whisper:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

## Configure actions

Map keywords to the actions you want in `config.yml` (see `config.example.yml`). You can combine multiple actions per keyword:

- **shell**: Run any local command, script, or CLI.
- **shortcut**: Trigger macOS Shortcuts by name (allows passing `args`).
- **applescript**: Run inline AppleScript for applet or UI automation.
- **http**: Call webhooks or APIs with arbitrary payloads.

Example:

```yaml
"turn on studio":
  shell: ["python", "studio_lights.py", "on"]
  http:
    url: "https://hooks.example.com/lights"
    json:
      state: "on"

"record demo":
  shortcut: "Start Screen Recording"
  applescript: 'tell application "Music" to pause'
```

## Run the listener

```bash
python keyword_listener.py --config config.yml --engine whisper
```

- Use `--engine sr` to run purely with SpeechRecognition/Sphinx.
- The script only keeps transcripts in memory long enough to match keywords and logs only matched keywords.

## Extend integrations

Actions are defined in `actions.py`; add your own `Action` subclass to integrate anything callable—shell scripts, applets, HTTP APIs, or device-specific CLIs. Combine multiple actions per keyword with `CompositeAction` for orchestrated workflows.
