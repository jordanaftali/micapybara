"""The pytest plugin. Installed automatically with the package.

After every test session, Mica reads the results and reacts. Turn her off for a
run with `pytest --no-capy`, or always with MICAPYBARA_QUIET=1.
She never fails or slows down your tests: any problem here is silently skipped.
"""

from __future__ import annotations

import os
import time

from . import messages, render, state
from .sprite import frame


def pytest_addoption(parser):
    parser.addoption("--no-capy", action="store_true", default=False, help="Hide Micapybara for this run.")


def _enabled(config) -> bool:
    if config.getoption("--no-capy") or os.environ.get("MICAPYBARA_QUIET"):
        return False
    if config.getoption("collectonly", default=False):
        return False
    return not hasattr(config, "workerinput")  # skip pytest-xdist workers


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not _enabled(config):
        return
    try:
        stats = terminalreporter.stats
        passed = len(stats.get("passed", []))
        failed = len(stats.get("failed", [])) + len(stats.get("error", []))
        if not passed and not failed:
            return
        pet = state.load()
        pet.record_tests(passed, failed)
        state.save(pet)

        tw = terminalreporter._tw
        color = render.use_color(getattr(tw, "_file", None)) or os.environ.get("FORCE_COLOR")
        mood = "worried" if failed else "happy"
        tw.line("")
        dance = (mood == "happy" and color and not os.environ.get("CI")
                 and hasattr(tw, "_file") and tw._file.isatty())
        if dance:  # a short dance, redrawn in place
            art = render.to_ansi(frame(mood, 0), color=True)
            rows = art.count("\n") + 1
            for i in range(12):
                tw.write(render.to_ansi(frame(mood, i), color=True) + "\n")
                tw.flush()
                time.sleep(0.12)
                if i < 11:
                    tw.write(f"\x1b[{rows}A\x1b[J")
        else:
            tw.line(render.to_ansi(frame(mood, 0), color=bool(color)))
        tw.line(messages.after_tests(pet, passed, failed))
        tw.line(messages.meter(pet.happiness))
    except Exception:  # Mica must never break a test run
        return
