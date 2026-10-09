"""Mica's saved state, validated with Pydantic.

The state lives in a small JSON file (~/.micapybara/state.json, or the folder in
MICAPYBARA_HOME). If the file is hand-edited into something invalid, Pydantic
catches it and Mica starts fresh instead of crashing your test run.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

Mood = Literal["happy", "content", "worried", "sleepy"]

PASS_BONUS = 10
FAIL_PENALTY = 15
ORANGE_BONUS = 5
ORANGE_COOLDOWN = timedelta(hours=1)
DAILY_DECAY = 5
SLEEPY_AFTER = timedelta(days=2)


def now() -> datetime:
    return datetime.now(timezone.utc)


class PetState(BaseModel):
    name: str = Field(default="Mica", min_length=1, max_length=20)
    happiness: int = Field(default=60, ge=0, le=100)
    streak: int = Field(default=0, ge=0, description="Green test runs in a row.")
    best_streak: int = Field(default=0, ge=0)
    runs: int = Field(default=0, ge=0)
    oranges: int = Field(default=0, ge=0)
    last_result: Literal["none", "passed", "failed"] = "none"
    last_seen: datetime = Field(default_factory=now)
    last_fed: datetime | None = None

    @field_validator("name")
    @classmethod
    def printable_name(cls, v: str) -> str:
        v = v.strip()
        if not v or not v.isprintable():
            raise ValueError("name must be printable text")
        return v

    # ---------- what Mica feels ----------

    @property
    def mood(self) -> Mood:
        if now() - self.last_seen >= SLEEPY_AFTER:
            return "sleepy"
        if self.last_result == "failed":
            return "worried"
        return "happy" if self.happiness >= 70 else "content"

    @property
    def effective_happiness(self) -> int:
        """Happiness right now, counting the days since her last visit."""
        return max(0, self.happiness - DAILY_DECAY * (now() - self.last_seen).days)

    def decay(self) -> None:
        """Lose a little happiness for each full day without a visit."""
        days = (now() - self.last_seen).days
        if days > 0:
            self.happiness = max(0, self.happiness - DAILY_DECAY * days)

    # ---------- things that happen to Mica ----------

    def record_tests(self, passed: int, failed: int) -> None:
        self.decay()
        self.runs += 1
        if failed:
            self.last_result = "failed"
            self.streak = 0
            self.happiness = max(0, self.happiness - FAIL_PENALTY)
        elif passed:
            self.last_result = "passed"
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.happiness = min(100, self.happiness + PASS_BONUS)
        self.last_seen = now()

    def feed(self) -> bool:
        """Give Mica an orange. Returns False if she was fed less than an hour ago."""
        if self.last_fed and now() - self.last_fed < ORANGE_COOLDOWN:
            return False
        self.decay()
        self.oranges += 1
        self.happiness = min(100, self.happiness + ORANGE_BONUS)
        self.last_fed = self.last_seen = now()
        return True


# ---------- saving and loading ----------

def state_path() -> Path:
    home = os.environ.get("MICAPYBARA_HOME")
    return (Path(home) if home else Path.home() / ".micapybara") / "state.json"


def load() -> PetState:
    path = state_path()
    if not path.exists():
        return PetState()
    try:
        return PetState.model_validate_json(path.read_text(encoding="utf-8"))
    except (ValidationError, ValueError):
        return PetState()  # a broken file never breaks your tests


def save(state: PetState) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
