import argparse
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence

import speech_recognition as sr

from actions import (
    Action,
    AppleScriptAction,
    AppleShortcutAction,
    CompositeAction,
    HTTPAction,
    ShellCommandAction,
)

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore


@dataclass
class KeywordBinding:
    keyword: str
    action: Action


class KeywordDispatcher:
    def __init__(self, bindings: Iterable[KeywordBinding]):
        self._bindings = list(bindings)
        self._keyword_index: Mapping[str, List[Action]] = defaultdict(list)
        for binding in self._bindings:
            self._keyword_index[binding.keyword.lower()].append(binding.action)

    def dispatch(self, text: str) -> List[str]:
        """Return matched keywords and run their actions without persisting text."""
        lowered = text.lower()
        matched: List[str] = []
        for keyword, actions in self._keyword_index.items():
            if keyword in lowered:
                matched.append(keyword)
                for action in actions:
                    action.run()
        return matched


class Transcriber:
    def transcribe(self, audio_data: sr.AudioData) -> str:
        raise NotImplementedError


class WhisperTranscriber(Transcriber):
    def __init__(self, model: str = "whisper-1") -> None:
        if OpenAI is None:
            raise ImportError("openai package is required for Whisper transcription")
        self.client = OpenAI()
        self.model = model

    def transcribe(self, audio_data: sr.AudioData) -> str:
        # Uses in-memory WAV bytes; never writes text or audio to disk.
        wav_bytes = audio_data.get_wav_data()
        response = self.client.audio.transcriptions.create(model=self.model, file=("capture.wav", wav_bytes))
        return response.text


class SpeechRecognitionTranscriber(Transcriber):
    def __init__(self, recognizer: sr.Recognizer | None = None) -> None:
        self.recognizer = recognizer or sr.Recognizer()

    def transcribe(self, audio_data: sr.AudioData) -> str:
        # Uses the recognizer's offline Sphinx engine when available; otherwise falls back to Google.
        try:
            return self.recognizer.recognize_sphinx(audio_data)
        except Exception:
            return self.recognizer.recognize_google(audio_data)


class KeywordListener:
    def __init__(
        self,
        dispatcher: KeywordDispatcher,
        transcriber: Transcriber,
        recognizer: sr.Recognizer | None = None,
        microphone: sr.Microphone | None = None,
    ) -> None:
        self.dispatcher = dispatcher
        self.transcriber = transcriber
        self.recognizer = recognizer or sr.Recognizer()
        self.microphone = microphone or sr.Microphone()

    def run(self) -> None:
        while True:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
            transcript = self.transcriber.transcribe(audio)
            matched = self.dispatcher.dispatch(transcript)
            if matched:
                logging.info("Triggered keywords: %s", ", ".join(matched))


def build_bindings(config: Mapping[str, Mapping]) -> List[KeywordBinding]:
    bindings: List[KeywordBinding] = []
    for keyword, action_config in config.items():
        actions = _build_actions(action_config)
        if len(actions) == 1:
            action = actions[0]
        else:
            action = CompositeAction(actions)
        bindings.append(KeywordBinding(keyword=keyword, action=action))
    return bindings


def _build_actions(action_config: Mapping) -> List[Action]:
    actions: List[Action] = []
    if "shell" in action_config:
        actions.append(ShellCommandAction(command=action_config["shell"]))
    if "shortcut" in action_config:
        actions.append(AppleShortcutAction(name=action_config["shortcut"], args=action_config.get("args")))
    if "applescript" in action_config:
        actions.append(AppleScriptAction(script=action_config["applescript"]))
    if "http" in action_config:
        http_cfg = action_config["http"]
        actions.append(
            HTTPAction(
                url=http_cfg["url"],
                method=http_cfg.get("method", "POST"),
                json=http_cfg.get("json"),
                headers=http_cfg.get("headers"),
            )
        )
    if not actions:
        raise ValueError("No actions configured for keyword")
    return actions


def load_config(path: str) -> Dict[str, Mapping]:
    import yaml

    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Listen for keywords and trigger automations")
    parser.add_argument("--config", required=True, help="Path to YAML config mapping keywords to actions")
    parser.add_argument("--engine", choices=["whisper", "sr"], default="whisper")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    dispatcher = KeywordDispatcher(build_bindings(config))
    recognizer = sr.Recognizer()

    if args.engine == "whisper":
        transcriber: Transcriber = WhisperTranscriber()
    else:
        transcriber = SpeechRecognitionTranscriber(recognizer)

    listener = KeywordListener(dispatcher=dispatcher, transcriber=transcriber, recognizer=recognizer)
    listener.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    main()
