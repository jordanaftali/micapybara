from micapybara import cli, state
from micapybara.render import to_ansi
from micapybara.sprite import MOODS, W, frame


def test_every_mood_has_frames_of_the_right_size():
    for mood, frames in MOODS.items():
        assert frames, mood
        for f in frames:
            assert len(f) == 26 and all(len(row) == W for row in f)


def test_color_render_uses_truecolor_half_blocks():
    art = to_ansi(frame("happy"), color=True)
    assert "\x1b[38;2;" in art and "▀" in art
    assert len(art.splitlines()) <= 13


def test_no_color_render_has_no_escape_codes():
    art = to_ansi(frame("worried"), color=False)
    assert "\x1b" not in art and "█" in art


def test_frames_wrap_around():
    assert frame("happy", 6) is frame("happy", 0)


def test_cli_status(home, capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert cli.main([]) == 0
    out = capsys.readouterr().out
    assert "Mica is calm" in out and "60/100" in out


def test_cli_feed_then_full(home, capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    cli.main(["feed"])
    cli.main(["feed"])
    out = capsys.readouterr().out
    assert "ate the orange" in out and "still full" in out
    assert state.load().oranges == 1


def test_cli_rename_is_validated(home, capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert cli.main(["name", "Bia"]) == 0
    assert state.load().name == "Bia"
    assert cli.main(["name", "x" * 30]) == 1
    assert state.load().name == "Bia"


def test_cli_stats(home, capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    cli.main(["stats"])
    assert "green streak" in capsys.readouterr().out
