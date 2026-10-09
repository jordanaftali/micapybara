"""The `capy` command.

    capy              see how Mica is doing
    capy feed         give her an orange (once an hour)
    capy dance        make her dance
    capy name Bia     rename her
    capy stats        streaks and totals
    capy reset        start over
"""

from __future__ import annotations

import argparse
import sys
import time

from pydantic import ValidationError

from . import messages, render, state
from .sprite import frame


def _show(mood: str, color: bool, i: int = 0) -> None:
    print(render.to_ansi(frame(mood, i), color=color))


def _animate(mood: str, color: bool, loops: int = 2) -> None:
    if not color or not sys.stdout.isatty():
        _show(mood, color)
        return
    first = render.to_ansi(frame(mood, 0))
    rows = first.count("\n") + 1
    n = 6 * loops
    for i in range(n):
        print(render.to_ansi(frame(mood, i)), flush=True)
        time.sleep(0.13)
        if i < n - 1:
            print(f"\x1b[{rows}A\x1b[J", end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="capy", description="Micapybara: a pixel capybara who lives in your terminal.")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("feed", help="give Mica an orange")
    sub.add_parser("dance", help="make Mica dance")
    sub.add_parser("stats", help="streaks and totals")
    sub.add_parser("reset", help="start over")
    name = sub.add_parser("name", help="rename your capybara")
    name.add_argument("new_name")
    args = parser.parse_args(argv)

    pet = state.load()
    color = render.use_color()

    if args.cmd == "feed":
        if pet.feed():
            state.save(pet)
            _animate("happy", color, loops=1)
            print(f"{pet.name} ate the orange. Delicious.")
        else:
            _show(pet.mood, color)
            print(f"{pet.name} is still full. Try again in a bit.")
        print(messages.meter(pet.happiness))
    elif args.cmd == "dance":
        _animate("happy", color)
        print(f"{pet.name} dances. No reason needed.")
    elif args.cmd == "name":
        try:
            pet = pet.model_copy(update={"name": args.new_name})
            pet = state.PetState.model_validate(pet.model_dump())
        except ValidationError as err:
            print(f"That name won't work: {err.errors()[0]['msg']}", file=sys.stderr)
            return 1
        state.save(pet)
        _show("happy", color)
        print(f"Hi, I'm {pet.name} now.")
    elif args.cmd == "stats":
        print(f"{pet.name}")
        print(f"  happiness     {messages.meter(pet.effective_happiness)}")
        print(f"  mood          {pet.mood}")
        print(f"  test runs     {pet.runs}")
        print(f"  green streak  {pet.streak} (best {pet.best_streak})")
        print(f"  oranges eaten {pet.oranges}")
    elif args.cmd == "reset":
        state.save(state.PetState())
        print("Started over with a fresh capybara.")
    else:
        mood = pet.mood
        _animate(mood, color, loops=1) if mood == "happy" else _show(mood, color)
        print(messages.status(pet))
        print(messages.meter(pet.effective_happiness))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
