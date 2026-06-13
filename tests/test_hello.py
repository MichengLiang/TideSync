from vision_agents.core import Runner

from tidesync.agent import RealtimeSettings, runner


def test_realtime_settings_default_to_mainland_qwen_flash(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_REALTIME_MODEL", raising=False)
    monkeypatch.delenv("QWEN_REALTIME_BASE_URL", raising=False)
    monkeypatch.delenv("QWEN_REALTIME_VOICE", raising=False)
    monkeypatch.delenv("QWEN_REALTIME_FPS", raising=False)

    settings = RealtimeSettings.from_env()

    assert settings.model == "qwen3.5-omni-flash-realtime"
    assert settings.base_url == "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    assert settings.voice == "Tina"
    assert settings.fps == 1


def test_realtime_settings_read_overrides(monkeypatch) -> None:
    monkeypatch.setenv("QWEN_REALTIME_MODEL", "custom-model")
    monkeypatch.setenv("QWEN_REALTIME_BASE_URL", "wss://example.test/realtime")
    monkeypatch.setenv("QWEN_REALTIME_VOICE", "Ethan")
    monkeypatch.setenv("QWEN_REALTIME_FPS", "2")

    settings = RealtimeSettings.from_env()

    assert settings.model == "custom-model"
    assert settings.base_url == "wss://example.test/realtime"
    assert settings.voice == "Ethan"
    assert settings.fps == 2


def test_realtime_settings_reject_invalid_fps(monkeypatch) -> None:
    monkeypatch.setenv("QWEN_REALTIME_FPS", "0")

    try:
        RealtimeSettings.from_env()
    except ValueError as exc:
        assert "QWEN_REALTIME_FPS must be greater than 0" in str(exc)
    else:
        raise AssertionError("expected invalid fps to raise ValueError")


def test_runner_is_vision_agents_runner() -> None:
    assert isinstance(runner, Runner)
