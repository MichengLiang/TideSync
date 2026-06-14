from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from vision_agents.core import Agent, AgentLauncher, Runner, User
from vision_agents.plugins.getstream import Edge
from vision_agents.plugins.qwen import Realtime as QwenRealtime

load_dotenv()

DEFAULT_QWEN_MODEL = "qwen3.5-omni-flash-realtime"
DEFAULT_QWEN_BASE_URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
DEFAULT_QWEN_VOICE = "Tina"
DEFAULT_QWEN_FPS = 1

INSTRUCTIONS = "你是 TideSync 的实时全模态语音视频助手。请优先用简洁自然的中文回答用户，能看见画面时结合画面内容回答。"


@dataclass(frozen=True, slots=True)
class RealtimeSettings:
    model: str = DEFAULT_QWEN_MODEL
    base_url: str = DEFAULT_QWEN_BASE_URL
    voice: str = DEFAULT_QWEN_VOICE
    fps: int = DEFAULT_QWEN_FPS

    @classmethod
    def from_env(cls) -> RealtimeSettings:
        return cls(
            model=_env_text("QWEN_REALTIME_MODEL", DEFAULT_QWEN_MODEL),
            base_url=_env_text("QWEN_REALTIME_BASE_URL", DEFAULT_QWEN_BASE_URL),
            voice=_env_text("QWEN_REALTIME_VOICE", DEFAULT_QWEN_VOICE),
            fps=_env_int("QWEN_REALTIME_FPS", DEFAULT_QWEN_FPS),
        )


def _env_text(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return parsed


async def create_agent(**kwargs: object) -> Agent:
    settings = RealtimeSettings.from_env()
    llm = QwenRealtime(
        model=settings.model,
        base_url=settings.base_url,
        voice=settings.voice,
        fps=settings.fps,
        include_video=True,
    )
    return Agent(
        edge=Edge(),
        agent_user=User(name="TideSync Qwen Assistant", id="tidesync-agent"),
        instructions=INSTRUCTIONS,
        llm=llm,
    )


async def join_call(agent: Agent, call_type: str, call_id: str, **kwargs: object) -> None:
    call = await agent.create_call(call_type, call_id)
    async with agent.join(call):
        await agent.finish()


runner = Runner(AgentLauncher(create_agent=create_agent, join_call=join_call))


def main() -> None:
    runner.cli()


if __name__ == "__main__":
    main()
