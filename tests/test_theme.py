from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_voice_theme_has_no_red_tokens():
    css = (ROOT / "style.css").read_text()
    forbidden_tokens = [
        "255, 62, 62",
        "#ff3e3e",
        "#ff2727",
        "#ff6161",
        "rgba(255, 62",
    ]
    for token in forbidden_tokens:
        assert token not in css, f"found legacy red accent token: {token}"


def test_voice_experience_uses_dark_overrides():
    overrides = (ROOT / "AI" / "ai.css").read_text()
    assert "linear-gradient(160deg, #020203" in overrides
    assert "border-color: rgba(10, 189, 198" in overrides
    assert "voice-stage" in overrides

