# Voice keyword automations

A lightweight Python listener that transcribes microphone audio, looks for configured keywords, and triggers expansive automations without persisting transcripts. It supports OpenAI Whisper for high-quality speech recognition and a fallback SpeechRecognition/Sphinx engine.

<details>
<summary>Quick start</summary>

1. Install dependencies (or install the CLI):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   To install the CLI with an entry point named `hiandbye` (so you can run it without `python`):
   ```bash
   pip install .
   # or during development
   pip install -e .
   ```

2. Set an OpenAI API key when using Whisper:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

3. Run the listener:
   ```bash
   python keyword_listener.py --config config.yml --engine whisper
   # or if installed as a CLI
   hiandbye --config config.yml --engine whisper
   ```

   - Use `--engine sr` to run purely with SpeechRecognition/Sphinx.
   - Transcripts stay in memory only long enough to match keywords; only matched keywords are logged.

</details>

## Keyword-to-action mapping

Define keywords in `config.yml` (see `config.example.yml`) and map them to one or more actions. Multiple actions can be combined per keyword to build workflows.

## Connector guide (macOS 15+)

Popular connectors are organized below with setup notes, when to use them, and sample configurations.

### Shell commands

Best for local scripts, CLIs, or anything runnable in a terminal.

- **Requirements:** Any executable reachable in your shell. Include env vars inline if needed.
- **Great for:** Homebrew CLIs (e.g., `blueutil`, `networksetup`), Python scripts, node tools.

Example keywords:

```yaml
"toggle wifi":
  shell: ["networksetup", "-setairportpower", "en0", "off"]

"start dev server":
  shell:
    - "bash"
    - "-lc"
    - "source ~/.zshrc && cd ~/code/app && npm run dev"
```

### macOS Shortcuts (built-in on macOS 15)

Use the Shortcuts CLI to tap into system-level automations and third-party integrations exposed via Shortcuts.

- **Requirements:** Sign into iCloud so Shortcuts sync; ensure the shortcut is runnable from the `shortcuts` CLI (macOS 15 includes it by default).
- **Great for:** HomeKit scenes, Reminders/Calendar entries, Files automation, Music, and many third-party applets.

Example keywords:

```yaml
"good morning":
  shortcut: "Morning Routine"  # e.g., HomeKit lights + play playlist

"log weight":
  shortcut: "Health - Log Weight"
  args: ["182"]  # Shortcuts input arguments
```

### AppleScript

Run inline AppleScript for UI scripting or app automation where Shortcuts does not expose a hook.

- **Requirements:** Enable "Automation" permissions for Terminal/Python in System Settings → Privacy & Security → Automation when prompted.
- **Great for:** Controlling apps like Music, Safari, Keynote; clicking menu items; typing keystrokes.

Example keywords:

```yaml
"pause music":
  applescript: 'tell application "Music" to pause'

"focus notes":
  applescript: |
    tell application "Notes"
      activate
      show folder "Personal"
    end tell
```

### HTTP / Webhooks

Call any HTTP endpoint to fan out into web services or automation hubs.

- **Requirements:** Network access; include auth headers or tokens as needed.
- **Great for:** Home Assistant, IFTTT/Zapier webhooks, Slack/Teams webhooks, Notion APIs, custom servers.

Example keywords:

```yaml
"set away mode":
  http:
    url: "https://homeassistant.local:8123/api/services/input_boolean/turn_on"
    headers:
      Authorization: "Bearer YOUR_LONG_LIVED_TOKEN"
    json:
      entity_id: "input_boolean.away"

"message team":
  http:
    url: "https://hooks.slack.com/services/T000/B000/XXXX"
    json:
      text: "Running late; starting WFH"
```

### Composite workflows

Chain multiple actions for a single keyword to orchestrate larger routines.

```yaml
"studio ready":
  shell: ["python", "scripts/lights.py", "on"]
  shortcut: "Open Streaming Apps"
  http:
    url: "https://hooks.zapier.com/hooks/catch/123/abc"
    json:
      status: "studio-live"
```

## Audio engines

- **Whisper (OpenAI):** Highest accuracy; requires `OPENAI_API_KEY`.
- **SpeechRecognition/Sphinx:** Offline-friendly fallback; specify `--engine sr`.

## Extend integrations

Actions live in `actions.py`; add an `Action` subclass to support other connectors (e.g., gRPC calls, message queues). Combine them with `CompositeAction` to build repeatable workflows without persisting transcripts.
