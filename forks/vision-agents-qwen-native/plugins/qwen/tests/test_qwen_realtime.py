import asyncio
import base64
import json
import os
from collections.abc import AsyncIterator, Iterator
from typing import Any, ClassVar

import dotenv
import numpy as np
import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiortc.mediastreams import MediaStreamTrack
from av import VideoFrame
from getstream.video.rtc import PcmData
from vision_agents.core.edge.types import Participant
from vision_agents.core.llm.realtime import (
    RealtimeAgentSpeechEnded,
    RealtimeAgentSpeechStarted,
    RealtimeAgentTranscript,
    RealtimeAudioOutput,
    RealtimeAudioOutputDone,
    RealtimeUserSpeechEnded,
    RealtimeUserSpeechStarted,
    RealtimeUserTranscript,
)
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
        self.server_events: list[dict[str, Any]] = []
        FakeQwenClient.instances.append(self)

    async def connect(self) -> None:
        self.events.append({"type": "session.update", "session": self.config})

    async def close(self) -> None:
        return None

    async def read(self) -> AsyncIterator[dict[str, Any]]:
        for event in self.server_events:
            yield event

    async def send_audio(self, pcm: PcmData) -> None:
        self.events.append({"type": "input_audio_buffer.append", "audio": "fake-audio"})

    async def commit_audio(self) -> None:
        self.events.append({"type": "input_audio_buffer.commit"})

    async def create_response(self) -> None:
        self.events.append({"type": "response.create"})

    async def clear_audio(self) -> None:
        self.events.append({"type": "input_audio_buffer.clear"})

    async def send_frame(self, frame_bytes: bytes) -> None:
        self.events.append({"type": "input_image_buffer.append", "image": "fake-image"})


def fake_pcm() -> PcmData:
    return PcmData(sample_rate=16000, format="s16", samples=np.zeros(160, dtype=np.int16))


def fake_frame() -> VideoFrame:
    return VideoFrame(2, 2, "rgb24")


def qwen_audio_delta(payload: bytes = b"\x00\x00\x01\x00") -> str:
    return base64.b64encode(payload).decode()


def fake_participant() -> Participant:
    return Participant(original=None, user_id="user-1", id="participant-1")


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
    await rt.simple_audio_response(fake_pcm())
    await rt.commit_audio_and_create_response()

    client = fake_qwen_client.instances[0]
    assert client.config["turn_detection"] is None
    assert [event["type"] for event in client.events] == [
        "session.update",
        "input_audio_buffer.append",
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
async def test_video_frame_not_sent_before_current_turn_audio(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "video gate"

    await rt.connect()
    await rt._send_video_frame(fake_frame())

    client = fake_qwen_client.instances[0]
    assert [event["type"] for event in client.events] == ["session.update"]
    assert rt._qwen_state_snapshot() == {
        "input_audio": "turn_empty",
        "video": "track_available_waiting_audio",
    }


@pytest.mark.contract
async def test_video_frame_sent_after_current_turn_audio(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "video gate"

    await rt.connect()
    await rt.simple_audio_response(fake_pcm())
    await rt._send_video_frame(fake_frame())

    client = fake_qwen_client.instances[0]
    assert [event["type"] for event in client.events] == [
        "session.update",
        "input_audio_buffer.append",
        "input_image_buffer.append",
    ]
    assert rt._qwen_state_snapshot() == {
        "input_audio": "audio_appended",
        "video": "send_allowed",
    }


@pytest.mark.contract
async def test_speech_events_update_turn_and_close_image_window(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "speech events"
    participant = fake_participant()

    await rt.connect()
    await rt.simple_audio_response(fake_pcm(), participant=participant)
    client = fake_qwen_client.instances[0]
    client.server_events.extend(
        [
            {"type": "input_audio_buffer.speech_started"},
            {"type": "input_audio_buffer.speech_stopped"},
        ]
    )

    await rt._process_events()
    await rt._send_video_frame(fake_frame())

    assert [type(event) for event in rt.output.peek()] == [
        RealtimeUserSpeechStarted,
        RealtimeUserSpeechEnded,
    ]
    assert [event["type"] for event in client.events] == [
        "session.update",
        "input_audio_buffer.append",
    ]
    assert rt._qwen_state_snapshot() == {
        "input_audio": "speech_stopped",
        "video": "send_closed_for_turn",
    }


@pytest.mark.contract
async def test_manual_commit_and_clear_close_image_window(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    committed = Realtime(api_key="test-key", turn_detection=None)
    committed._instructions = "manual commit"
    await committed.connect()
    await committed.simple_audio_response(fake_pcm())
    await committed.commit_audio_and_create_response()
    await committed._send_video_frame(fake_frame())

    cleared = Realtime(api_key="test-key", turn_detection=None)
    cleared._instructions = "manual clear"
    await cleared.connect()
    await cleared.simple_audio_response(fake_pcm())
    await cleared.clear_audio()
    await cleared._send_video_frame(fake_frame())

    committed_events = [event["type"] for event in fake_qwen_client.instances[0].events]
    cleared_events = [event["type"] for event in fake_qwen_client.instances[1].events]
    assert committed_events == [
        "session.update",
        "input_audio_buffer.append",
        "input_audio_buffer.commit",
        "response.create",
    ]
    assert cleared_events == [
        "session.update",
        "input_audio_buffer.append",
        "input_audio_buffer.clear",
    ]
    assert committed._qwen_state_snapshot() == {
        "input_audio": "committed",
        "video": "send_closed_for_turn",
    }
    assert cleared._qwen_state_snapshot() == {
        "input_audio": "cleared",
        "video": "send_closed_for_turn",
    }


@pytest.mark.contract
async def test_input_audio_buffer_committed_event_closes_image_window(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "server committed"

    await rt.connect()
    await rt.simple_audio_response(fake_pcm())
    client = fake_qwen_client.instances[0]
    client.server_events.append({"type": "input_audio_buffer.committed"})

    await rt._process_events()
    await rt._send_video_frame(fake_frame())

    assert [event["type"] for event in client.events] == [
        "session.update",
        "input_audio_buffer.append",
    ]
    assert rt._qwen_state_snapshot() == {
        "input_audio": "committed",
        "video": "send_closed_for_turn",
    }


@pytest.mark.contract
async def test_track_reconnect_waits_for_current_turn_audio(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "track reconnect"

    await rt.connect()
    await rt.simple_audio_response(fake_pcm())
    await rt._send_video_frame(fake_frame())
    await rt.stop_watching_video_track()
    await rt._on_video_track_reconnected()
    await rt._send_video_frame(fake_frame())
    await rt.simple_audio_response(fake_pcm())
    await rt._send_video_frame(fake_frame())

    client = fake_qwen_client.instances[0]
    assert [event["type"] for event in client.events] == [
        "session.update",
        "input_audio_buffer.append",
        "input_image_buffer.append",
        "input_audio_buffer.append",
        "input_image_buffer.append",
    ]
    assert rt._qwen_state_snapshot() == {
        "input_audio": "audio_appended",
        "video": "send_allowed",
    }


@pytest.mark.contract
async def test_image_timing_error_suspends_until_new_audio_turn(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "image timing error"

    await rt.connect()
    await rt.simple_audio_response(fake_pcm())
    await rt._send_video_frame(fake_frame())
    client = fake_qwen_client.instances[0]
    client.server_events.append(
        {
            "type": "error",
            "error": {
                "code": "invalid_request_error",
                "message": "append image before append audio",
                "param": "input_image_buffer",
            },
        }
    )

    await rt._process_events()
    await rt._send_video_frame(fake_frame())
    await rt.simple_audio_response(fake_pcm())
    await rt._send_video_frame(fake_frame())

    assert [event["type"] for event in client.events] == [
        "session.update",
        "input_audio_buffer.append",
        "input_image_buffer.append",
        "input_audio_buffer.append",
        "input_image_buffer.append",
    ]
    assert rt._qwen_state_snapshot() == {
        "input_audio": "audio_appended",
        "video": "send_allowed",
    }


@pytest.mark.contract
async def test_response_audio_delta_and_done_emit_output_boundary(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "audio done"

    await rt.connect()
    client = fake_qwen_client.instances[0]
    client.server_events.extend(
        [
            {"type": "response.created", "response": {"id": "resp_1"}},
            {"type": "response.audio.delta", "response_id": "resp_1", "delta": qwen_audio_delta()},
            {"type": "response.audio.done", "response_id": "resp_1"},
        ]
    )

    await rt._process_events()

    events = rt.output.peek()
    assert [type(event) for event in events] == [
        RealtimeAgentSpeechStarted,
        RealtimeAudioOutput,
        RealtimeAudioOutputDone,
        RealtimeAgentSpeechEnded,
    ]
    assert events[0].response_id == "resp_1"
    assert events[1].response_id == "resp_1"
    assert events[1].data.sample_rate == 24000
    assert events[2].response_id == "resp_1"
    assert events[2].interrupted is False
    assert events[3].response_id == "resp_1"
    assert events[3].interrupted is False
    assert rt._qwen_response_snapshot()["audio_output"] == "audio_output_done_emitted"


@pytest.mark.contract
async def test_audio_transcript_delta_and_done_emit_non_empty_final(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "transcript done"

    await rt.connect()
    client = fake_qwen_client.instances[0]
    client.server_events.extend(
        [
            {"type": "response.created", "response": {"id": "resp_1"}},
            {"type": "response.audio_transcript.delta", "response_id": "resp_1", "delta": "hello "},
            {"type": "response.audio_transcript.delta", "response_id": "resp_1", "delta": "world"},
            {"type": "response.audio_transcript.done", "response_id": "resp_1", "transcript": "hello world"},
            {"type": "response.done", "response": {"id": "resp_1"}},
        ]
    )

    await rt._process_events()

    transcripts = [event for event in rt.output.peek() if isinstance(event, RealtimeAgentTranscript)]
    assert [(event.mode, event.text) for event in transcripts] == [
        ("delta", "hello "),
        ("delta", "world"),
        ("final", "hello world"),
    ]
    assert rt._qwen_response_snapshot()["agent_transcript"] == "agent_transcript_final"


@pytest.mark.contract
async def test_audio_transcript_done_uses_accumulated_delta_when_done_omits_text(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "transcript fallback"

    await rt.connect()
    client = fake_qwen_client.instances[0]
    client.server_events.extend(
        [
            {"type": "response.audio_transcript.delta", "delta": "fallback "},
            {"type": "response.audio_transcript.delta", "delta": "text"},
            {"type": "response.audio_transcript.done"},
        ]
    )

    await rt._process_events()

    transcripts = [event for event in rt.output.peek() if isinstance(event, RealtimeAgentTranscript)]
    assert transcripts[-1].mode == "final"
    assert transcripts[-1].text == "fallback text"


@pytest.mark.contract
async def test_response_done_parses_usage_and_does_not_emit_empty_transcript_final(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "usage"
    usage = {
        "total_tokens": 42,
        "input_tokens": 10,
        "output_tokens": 32,
        "input_token_details": {"audio_tokens": 7},
        "output_token_details": {"text_tokens": 12, "audio_tokens": 20},
        "plugins": {"search": {"count": 2, "strategy": "standard", "sources": ["doc-1"]}},
    }

    await rt.connect()
    client = fake_qwen_client.instances[0]
    client.server_events.extend(
        [
            {"type": "response.created", "response": {"id": "resp_usage"}},
            {"type": "response.done", "response": {"id": "resp_usage"}, "usage": usage},
        ]
    )

    await rt._process_events()

    assert not [event for event in rt.output.peek() if isinstance(event, RealtimeAgentTranscript) and event.mode == "final" and event.text == ""]
    snapshot = rt._qwen_response_snapshot()
    assert snapshot["response"] == "completed"
    assert snapshot["usage"] == "usage_parsed"
    assert snapshot["search"] == "search_usage_seen"
    usage_snapshot = rt._qwen_usage_snapshot()
    assert usage_snapshot["response_id"] == "resp_usage"
    assert usage_snapshot["total_tokens"] == 42
    assert usage_snapshot["input_tokens"] == 10
    assert usage_snapshot["output_tokens"] == 32
    assert usage_snapshot["input_token_details"] == {"audio_tokens": 7}
    assert usage_snapshot["output_token_details"] == {"text_tokens": 12, "audio_tokens": 20}
    assert usage_snapshot["raw_usage"] == usage
    assert usage_snapshot["search_usage"] == {"count": 2, "strategy": "standard", "sources": ["doc-1"]}


@pytest.mark.contract
async def test_response_done_usage_parse_failure_retains_raw_payload(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "usage parse failure"
    invalid_usage = {"total_tokens": "not-an-int"}

    await rt.connect()
    client = fake_qwen_client.instances[0]
    client.server_events.append(
        {
            "type": "response.done",
            "response": {"id": "resp_bad_usage"},
            "usage": invalid_usage,
        }
    )

    await rt._process_events()

    snapshot = rt._qwen_response_snapshot()
    usage_snapshot = rt._qwen_usage_snapshot()
    assert snapshot["usage"] == "usage_parse_failed"
    assert usage_snapshot["response_id"] == "resp_bad_usage"
    assert usage_snapshot["raw_usage"] == invalid_usage
    assert usage_snapshot["parse_error"] == "token count must be an int or None, got str"


@pytest.mark.contract
async def test_response_lifecycle_events_update_state_projection(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "lifecycle"

    await rt.connect()
    client = fake_qwen_client.instances[0]
    client.server_events.extend(
        [
            {"type": "response.created", "response": {"id": "resp_lifecycle"}},
            {
                "type": "response.output_item.added",
                "response_id": "resp_lifecycle",
                "item": {"id": "item_1"},
            },
            {
                "type": "conversation.item.created",
                "response_id": "resp_lifecycle",
                "item": {"id": "conv_item_1"},
            },
            {
                "type": "response.content_part.added",
                "response_id": "resp_lifecycle",
                "item_id": "item_1",
                "part": {"type": "audio"},
            },
            {
                "type": "response.content_part.done",
                "response_id": "resp_lifecycle",
                "item_id": "item_1",
                "part": {"type": "audio"},
            },
            {
                "type": "response.output_item.done",
                "response_id": "resp_lifecycle",
                "item": {"id": "item_1"},
            },
            {"type": "response.done", "response": {"id": "resp_lifecycle"}},
        ]
    )

    await rt._process_events()

    assert rt._qwen_response_snapshot() == {
        "response_id": "resp_lifecycle",
        "item_id": "item_1",
        "conversation_item_id": "conv_item_1",
        "content_part_type": "audio",
        "response": "completed",
        "audio_output": "no_audio_output",
        "user_transcript": "user_transcript_empty",
        "agent_transcript": "agent_transcript_empty",
        "usage": "usage_absent",
        "search": "search_usage_missing",
    }


@pytest.mark.contract
async def test_user_input_audio_transcription_delta_and_completed_emit_transcripts(
    fake_qwen_client: type[FakeQwenClient],
) -> None:
    rt = Realtime(api_key="test-key")
    rt._instructions = "user transcript"
    participant = fake_participant()

    await rt.connect()
    await rt.simple_audio_response(fake_pcm(), participant=participant)
    client = fake_qwen_client.instances[0]
    client.server_events.extend(
        [
            {"type": "conversation.item.input_audio_transcription.delta", "delta": "user "},
            {"type": "conversation.item.input_audio_transcription.completed", "transcript": "user final"},
        ]
    )

    await rt._process_events()

    user_transcripts = [event for event in rt.output.peek() if isinstance(event, RealtimeUserTranscript)]
    assert [(event.mode, event.text) for event in user_transcripts] == [
        ("delta", "user "),
        ("final", "user final"),
    ]
    assert rt._qwen_response_snapshot()["user_transcript"] == "user_transcript_final"


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
