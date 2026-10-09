from datetime import timedelta

import pytest
from pydantic import ValidationError

from micapybara import state
from micapybara.state import PetState, now


def test_defaults():
    s = PetState()
    assert (s.name, s.happiness, s.streak, s.mood) == ("Mica", 60, 0, "content")


def test_pydantic_rejects_bad_values():
    with pytest.raises(ValidationError):
        PetState(happiness=150)
    with pytest.raises(ValidationError):
        PetState(name="")
    with pytest.raises(ValidationError):
        PetState(name="x" * 21)
    with pytest.raises(ValidationError):
        PetState(name="bad\x1bname")
    with pytest.raises(ValidationError):
        PetState(last_result="maybe")


def test_passing_tests_make_her_happy():
    s = PetState()
    s.record_tests(passed=12, failed=0)
    assert (s.happiness, s.streak, s.last_result, s.mood) == (70, 1, "passed", "happy")


def test_failing_tests_worry_her_and_reset_the_streak():
    s = PetState(streak=4, happiness=80)
    s.record_tests(passed=10, failed=2)
    assert (s.happiness, s.streak, s.mood) == (65, 0, "worried")


def test_happiness_stays_between_0_and_100():
    s = PetState(happiness=98)
    s.record_tests(5, 0)
    assert s.happiness == 100
    s = PetState(happiness=5)
    s.record_tests(0, 1)
    assert s.happiness == 0


def test_best_streak_is_kept():
    s = PetState()
    for _ in range(3):
        s.record_tests(1, 0)
    s.record_tests(1, 1)
    assert (s.streak, s.best_streak) == (0, 3)


def test_orange_has_a_one_hour_cooldown():
    s = PetState()
    assert s.feed() is True
    assert s.feed() is False
    assert (s.oranges, s.happiness) == (1, 65)
    s.last_fed = now() - timedelta(hours=2)
    assert s.feed() is True


def test_she_gets_sleepy_and_sadder_when_ignored():
    s = PetState(happiness=80, last_result="passed", last_seen=now() - timedelta(days=3))
    assert s.mood == "sleepy"
    assert s.effective_happiness == 65
    s.record_tests(1, 0)
    assert s.happiness == 80 - 15 + 10
    assert s.mood == "happy"


def test_save_and_load_round_trip(home):
    s = PetState(name="Bia", happiness=77)
    state.save(s)
    loaded = state.load()
    assert (loaded.name, loaded.happiness) == ("Bia", 77)
    assert state.state_path().parent == home


def test_a_broken_save_file_starts_fresh(home):
    state.state_path().parent.mkdir(parents=True, exist_ok=True)
    state.state_path().write_text('{"happiness": 9000}')
    assert state.load().happiness == 60
    state.state_path().write_text("not json at all")
    assert state.load().name == "Mica"
