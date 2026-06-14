import asyncio
import json
import os
from collections.abc import AsyncIterator, Iterator
from typing import Any, ClassVar

import dotenv
import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiortc.mediastreams import MediaStreamTrack
from getstream.video.rtc import PcmData
from vision_agents.core.llm.realtime import RealtimeAudioOutput
from vision_agents.plugins.qwen import Realtime, qwen_realtime
from vision_agents.plugins.qwen.client import Qwen3RealtimeClient

dotenv.load_dotenv()


class FakeQwenClient:
    instances: ClassVar[list["FakeQwenClient"]] = []

    def __init__(self, *, api_key: str, base_url: str, model: str, config: dict[str, Any]) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.config = config
        self.events: list[dict[str, Any]] = []
        FakeQwenClient.instances.append(self)

    async def connect(self) -> None:
        self.events.append({"type": "session.update", "session": self.config})

    async def close(self) -> None:
        return None

    async def read(self) -> AsyncIterator[dict[str, Any]]:
        while False:
            yield {}

    async def send_audio(self, pcm: PcmData) -> None:
        self.events.append({"type": "input_audio_buffer.append", "audio": "fake-audio"})

    async def commit_audio(self) -> None:
        self.events.append({"type": "input_audio_buffer.commit"})

    async def create_response(self) -> None:
        self.events.append({"type": "response.create"})


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    async def send(self, message: str) -> None:
        self.sent.append(json.loads(message))


@pytest.fixture(autouse=True)
def reset_fake_clients() -> Iterator[None]:
    FakeQwenClient.instances.clear()
    yield
    FakeQwenClient.instances.clear()


@pytest.fixture
def fake_qwen_client(monkeypatch: MonkeyPatch) -> type[FakeQwenClient]:
    monkeypatch.setattr(qwen_realtime, "Qwen3RealtimeClient", FakeQwenClient)
    return FakeQwenClient


@pytest.mark.contract
async def test_session_update_uses_qwen35_contract_defaults(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(
        api_key="test-key",
        model="qwen3.5-omni-flash-realtime",
        base_url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime",
        voice="Tina",
    )
    rt._instructions = "contract instructions"

    await rt.connect()

    client = fake_qwen_client.instances[0]
    assert client.model == "qwen3.5-omni-flash-realtime"
    assert client.base_url == "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    assert client.config == {
        "modalities": ["text", "audio"],
        "voice": "Tina",
        "instructions": "contract instructions",
        "input_audio_format": "pcm",
        "output_audio_format": "pcm",
        "input_audio_transcription": {"model": "qwen3-asr-flash-realtime"},
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.1,
            "prefix_padding_ms": 500,
            "silence_duration_ms": 900,
        },
    }
    assert client.events[0] == {"type": "session.update", "session": client.config}


@pytest.mark.contract
async def test_semantic_vad_is_visible_in_session_update(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key", turn_detection="semantic_vad")
    rt._instructions = "semantic vad"

    await rt.connect()

    session = fake_qwen_client.instances[0].config
    assert session["turn_detection"]["type"] == "semantic_vad"
    assert session["turn_detection"]["threshold"] == 0.1


@pytest.mark.contract
async def test_manual_mode_sends_null_turn_detection_and_response_create(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key", turn_detection=None)
    rt._instructions = "manual mode"

    await rt.connect()
    await rt.commit_audio_and_create_response()

    client = fake_qwen_client.instances[0]
    assert client.config["turn_detection"] is None
    assert [event["type"] for event in client.events] == [
        "session.update",
        "input_audio_buffer.commit",
        "response.create",
    ]


@pytest.mark.contract
async def test_tools_and_search_are_rejected_before_session_update(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(
        api_key="test-key",
        tools=[{"type": "function", "function": {"name": "lookup"}}],
        enable_search=True,
    )

    with pytest.raises(ValueError, match="tools and enable_search"):
        await rt.connect()

    assert fake_qwen_client.instances == []


@pytest.mark.contract
async def test_tools_and_search_config_payloads_do_not_include_unsupported_fields(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    tools_rt = Realtime(
        api_key="test-key",
        tools=[
            {
                "name": "lookup",
                "description": "Lookup a value",
                "parameters_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            }
        ],
    )
    tools_rt._instructions = "tools"
    await tools_rt.connect()

    search_rt = Realtime(
        api_key="test-key",
        enable_search=True,
        search_options={"enable_source": True},
    )
    search_rt._instructions = "search"
    await search_rt.connect()

    tools_session = fake_qwen_client.instances[0].config
    search_session = fake_qwen_client.instances[1].config
    assert tools_session["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Lookup a value",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        }
    ]
    assert search_session["enable_search"] is True
    assert search_session["search_options"] == {"enable_source": True}
    for session in (tools_session, search_session):
        assert "tool_choice" not in session
        assert "parallel_tool_calls" not in session


@pytest.mark.contract
async def test_client_sends_closed_event_set_payloads() -> None:
    client = Qwen3RealtimeClient(
        api_key="test-key",
        base_url="wss://example.test/realtime",
        model="qwen3.5-omni-flash-realtime",
        config={},
    )
    fake_ws = FakeWebSocket()
    client._real_ws = fake_ws

    await client.clear_audio()
    await client.send_function_call_output(call_id="call-123", output="tool result")
    await client.create_response()

    sent = fake_ws.sent
    assert [event["type"] for event in sent] == [
        "input_audio_buffer.clear",
        "conversation.item.create",
        "response.create",
    ]
    assert sent[1]["item"] == {
        "type": "function_call_output",
        "call_id": "call-123",
        "output": "tool result",
    }


@pytest.mark.skip()
@pytest.mark.integration
class TestQwen3RealtimeIntegration:
    """Integration tests for Qwen3Realtime connect flow"""

    @pytest.fixture
    async def llm(self) -> AsyncIterator[Realtime]:
        if not os.getenv("DASHSCOPE_API_KEY"):
            pytest.skip("DASHSCOPE_API_KEY not set")
        rt = Realtime(
            fps=1,
            vad_silence_duration_ms=0,
            vad_prefix_padding_ms=0,
            vad_threshold=0.1,
        )
        try:
            await rt.connect()
            await asyncio.sleep(5.0)
            yield rt
        finally:
            await rt.close()

    async def test_audio_sending_flow(self, llm: Realtime, mia_audio_16khz: PcmData, silence_1s_16khz: PcmData) -> None:
        """Test sending real audio data and verify connection remains stable"""
        # Send 1s of silence first
        await llm.simple_audio_response(silence_1s_16khz)
        # Send audio
        await llm.simple_audio_response(mia_audio_16khz)
        # Send silence again
        await llm.simple_audio_response(silence_1s_16khz)

        # Let it run for a few sec
        await asyncio.sleep(10.0)

        # Verify that the model replied with audio
        audio = [i for i in llm.output.peek() if isinstance(i, RealtimeAudioOutput)]
        assert len(audio) > 0

    async def test_video_sending_flow(
        self,
        llm: Realtime,
        bunny_video_track: MediaStreamTrack,
        describe_what_you_see_audio_16khz: PcmData,
        silence_1s_16khz: PcmData,
    ) -> None:
        """Test sending real video data and verify connection remains stable"""
        # Send 1s of silence first
        await llm.simple_audio_response(silence_1s_16khz)
        # Start video sender with low FPS to avoid overwhelming the connection
        await llm.watch_video_track(bunny_video_track)
        # Send audio to the model (it does not support text inputs)
        await llm.simple_audio_response(describe_what_you_see_audio_16khz)
        # Send silence again
        await llm.simple_audio_response(silence_1s_16khz)
        # Let it run for a few seconds
        await asyncio.sleep(10.0)

        # Stop video sender
        await llm.stop_watching_video_track()
        # Verify that the model replied
        audio = [i for i in llm.output.peek() if isinstance(i, RealtimeAudioOutput)]
        assert len(audio) > 0
