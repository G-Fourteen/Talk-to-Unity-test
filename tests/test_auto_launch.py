from pathlib import Path

APP_JS = (Path(__file__).resolve().parents[1] / "AI" / "app.js").read_text()


def test_auto_start_without_landing_section():
    assert "const shouldAutoStartExperience = !launchButton && !landingSection;" in APP_JS
    assert "if (shouldAutoStartExperience)" in APP_JS
    assert "void startApplication();" in APP_JS

