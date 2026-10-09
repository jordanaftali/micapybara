"""Run real pytest sessions inside the tests (with pytester) and check Mica reacts."""

from micapybara import state


def test_green_run_makes_her_dance(pytester, home, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    pytester.makepyfile("def test_a(): assert True\ndef test_b(): assert 1 + 1 == 2")
    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines(["*Mica is dancing! 2 tests passed.*", "*70/100*"])
    assert state.load().streak == 1


def test_red_run_worries_her(pytester, home, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    pytester.makepyfile("def test_ok(): pass\ndef test_bad(): assert False")
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(["*Mica is worried. 1 test failed.*"])
    assert state.load().last_result == "failed"


def test_she_never_changes_the_exit_code(pytester, home):
    pytester.makepyfile("def test_bad(): assert False")
    assert pytester.runpytest().ret == 1
    pytester.makepyfile("def test_ok(): pass")
    assert pytester.runpytest().ret == 0


def test_no_capy_flag_hides_her(pytester, home):
    pytester.makepyfile("def test_a(): pass")
    result = pytester.runpytest("--no-capy")
    assert "Mica" not in result.stdout.str()
    assert state.load().runs == 0


def test_quiet_env_hides_her(pytester, home, monkeypatch):
    monkeypatch.setenv("MICAPYBARA_QUIET", "1")
    pytester.makepyfile("def test_a(): pass")
    assert "Mica" not in pytester.runpytest().stdout.str()


def test_a_broken_save_file_does_not_break_tests(pytester, home):
    state.state_path().parent.mkdir(parents=True, exist_ok=True)
    state.state_path().write_text("{oops")
    pytester.makepyfile("def test_a(): pass")
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
    assert "Mica is dancing" in result.stdout.str()
