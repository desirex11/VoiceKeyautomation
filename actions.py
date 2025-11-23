import os
import subprocess
from dataclasses import dataclass
from typing import Dict, Iterable, List


class Action:
    """Represents an actionable side effect triggered by a keyword."""

    def run(self) -> None:
        raise NotImplementedError


@dataclass
class ShellCommandAction(Action):
    command: List[str]
    env: Dict[str, str] | None = None

    def run(self) -> None:
        merged_env = os.environ.copy()
        if self.env:
            merged_env.update(self.env)
        subprocess.run(self.command, env=merged_env, check=True)


@dataclass
class AppleShortcutAction(Action):
    name: str
    args: List[str] | None = None

    def run(self) -> None:
        # Uses the macOS Shortcuts CLI for broad compatibility with system and applet automation.
        command = ["shortcuts", "run", self.name]
        if self.args:
            command.extend(self.args)
        subprocess.run(command, check=True)


@dataclass
class AppleScriptAction(Action):
    script: str

    def run(self) -> None:
        subprocess.run(["osascript", "-e", self.script], check=True)


@dataclass
class HTTPAction(Action):
    url: str
    method: str = "POST"
    json: Dict | None = None
    headers: Dict[str, str] | None = None

    def run(self) -> None:
        import requests

        response = requests.request(self.method, self.url, json=self.json, headers=self.headers)
        response.raise_for_status()


@dataclass
class CompositeAction(Action):
    actions: Iterable[Action]

    def run(self) -> None:
        for action in self.actions:
            action.run()
