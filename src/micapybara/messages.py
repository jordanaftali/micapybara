"""What Mica says. Kept separate so the words are easy to edit."""

from __future__ import annotations

from .state import PetState


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def after_tests(s: PetState, passed: int, failed: int) -> str:
    if failed:
        return f"{s.name} is worried. {plural(failed, 'test')} failed. She believes in you."
    if s.streak >= 5:
        return f"{s.name} is dancing! {plural(passed, 'test')} passed. {s.streak} green runs in a row."
    return f"{s.name} is dancing! {plural(passed, 'test')} passed."


def status(s: PetState) -> str:
    return {
        "happy": f"{s.name} is happy and vibing.",
        "content": f"{s.name} is calm, chewing grass. Run your tests to cheer her up.",
        "worried": f"{s.name} is worried about your last test run.",
        "sleepy": f"{s.name} fell asleep. It's been a while since your last test run.",
    }[s.mood]


def meter(happiness: int, width: int = 20) -> str:
    filled = round(happiness / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + f"] {happiness}/100"
