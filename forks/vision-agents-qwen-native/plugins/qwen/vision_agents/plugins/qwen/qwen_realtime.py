import asyncio
import base64
import logging
import os
import uuid
from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal, cast

import aiortc
import av
from aiortc import VideoStreamTrack
from getstream.video.rtc import PcmData
from vision_agents.core.edge.types import Participant
from vision_agents.core.llm import Realtime
from vision_agents.core.llm.llm import LLMResponseDelta, LLMResponseFinal
from vision_agents.core.llm.llm_types import ToolSchema
from vision_agents.core.utils.video_forwarder import VideoForwarder
from vision_agents.core.utils.video_utils import frame_to_jpeg_bytes

from .client import Qwen3RealtimeClient

DEFAULT_MODEL = "qwen3.5-omni-flash-realtime"
DEFAULT_BASE_URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
DEFAULT_AUDIO_TRANSCRIPTION_MODEL = "qwen3-asr-flash-realtime"
PLUGIN_NAME = "Qwen3Realtime"
TurnDetectionMode = Literal["server_vad", "semantic_vad"]

logger = logging.getLogger(__name__)


class InputAudioState(StrEnum):
    TURN_EMPTY = "turn_empty"
    AUDIO_APPENDED = "audio_appended"
    SPEECH_STARTED = "speech_started"
    SPEECH_STOPPED = "speech_stopped"
    COMMITTED = "committed"
    CLEARED = "cleared"


class VideoPermissionState(StrEnum):
    NO_TRACK = "no_track"
    TRACK_AVAILABLE_WAITING_AUDIO = "track_available_waiting_audio"
    SEND_ALLOWED = "send_allowed"
    SEND_CLOSED_FOR_TURN = "send_closed_for_turn"
    TRACK_REMOVED = "track_removed"
    TRACK_RECONNECTED_WAITING_AUDIO = "track_reconnected_waiting_audio"
    SUSPENDED_AFTER_IMAGE_TIMING_ERROR = "suspended_after_image_timing_error"


class ResponseState(StrEnum):
    NO_RESPONSE = "no_response"
    RESPONSE_CREATED = "response_created"
    OUTPUT_ITEM_OPEN = "output_item_open"
    CONTENT_PART_OPEN = "content_part_open"
    CANCEL_REQUESTED = "cancel_requested"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"


class LocalAudioOutputState(StrEnum):
    NO_AUDIO_OUTPUT = "no_audio_output"
    AUDIO_OUTPUT_STREAMING = "audio_output_streaming"
    AUDIO_DONE_RECEIVED = "audio_done_received"
    AUDIO_OUTPUT_DONE_EMITTED = "audio_output_done_emitted"
    AUDIO_INTERRUPTED = "audio_interrupted"
    AUDIO_FLUSH_EMITTED = "audio_flush_emitted"
    STALE_AUDIO_BLOCKED = "stale_audio_blocked"


class TranscriptState(StrEnum):
    USER_TRANSCRIPT_EMPTY = "user_transcript_empty"
    USER_TRANSCRIPT_DELTA = "user_transcript_delta"
    USER_TRANSCRIPT_FINAL = "user_transcript_final"
    AGENT_TRANSCRIPT_EMPTY = "agent_transcript_empty"
    AGENT_TRANSCRIPT_DELTA = "agent_transcript_delta"
    AGENT_TRANSCRIPT_FINAL = "agent_transcript_final"
    TRANSCRIPT_INTERRUPTED_BOUNDARY = "transcript_interrupted_boundary"


class UsageState(StrEnum):
    USAGE_ABSENT = "usage_absent"
    USAGE_PARSED = "usage_parsed"
    USAGE_PARSE_FAILED = "usage_parse_failed"


class SearchUsageState(StrEnum):
    SEARCH_USAGE_MISSING = "search_usage_missing"
    SEARCH_USAGE_SEEN = "search_usage_seen"


class ErrorState(StrEnum):
    NO_ERROR = "no_error"
    CANCEL_ERROR = "cancel_error"
    INPUT_TIMING_ERROR = "input_timing_error"
    UNKNOWN_QWEN_ERROR = "unknown_qwen_error"


@dataclass(slots=True)
class QwenInputTurnState:
    input_audio: InputAudioState = InputAudioState.TURN_EMPTY
    video: VideoPermissionState = VideoPermissionState.TRACK_AVAILABLE_WAITING_AUDIO

    def mark_audio_appended(self) -> None:
        self.input_audio = InputAudioState.AUDIO_APPENDED
        self.video = VideoPermissionState.SEND_ALLOWED

    def mark_speech_started(self) -> None:
        self.input_audio = InputAudioState.SPEECH_STARTED
        self.video = VideoPermissionState.SEND_ALLOWED

    def close_for_speech_stopped(self) -> None:
        self.input_audio = InputAudioState.SPEECH_STOPPED
        self.video = VideoPermissionState.SEND_CLOSED_FOR_TURN

    def close_for_commit(self) -> None:
        self.input_audio = InputAudioState.COMMITTED
        self.video = VideoPermissionState.SEND_CLOSED_FOR_TURN

    def close_for_clear(self) -> None:
        self.input_audio = InputAudioState.CLEARED
        self.video = VideoPermissionState.SEND_CLOSED_FOR_TURN

    def mark_track_removed(self) -> None:
        self.video = VideoPermissionState.TRACK_REMOVED

    def mark_track_reconnected(self) -> None:
        self.input_audio = InputAudioState.TURN_EMPTY
        self.video = VideoPermissionState.TRACK_RECONNECTED_WAITING_AUDIO

    def suspend_after_image_timing_error(self) -> None:
        self.video = VideoPermissionState.SUSPENDED_AFTER_IMAGE_TIMING_ERROR

    def can_send_image(self) -> bool:
        return self.video is VideoPermissionState.SEND_ALLOWED

    def snapshot(self) -> dict[str, str]:
        return {"input_audio": self.input_audio.value, "video": self.video.value}


@dataclass(slots=True)
class QwenUsageSnapshot:
    response_id: str | None = None
    raw_usage: Any | None = None
    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    input_token_details: dict[str, Any] | None = None
    output_token_details: dict[str, Any] | None = None
    search_usage: dict[str, Any] | None = None
    parse_error: str | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "raw_usage": self.raw_usage,
            "total_tokens": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "input_token_details": self.input_token_details,
            "output_token_details": self.output_token_details,
            "search_usage": self.search_usage,
            "parse_error": self.parse_error,
        }


@dataclass(slots=True)
class QwenCancelErrorSnapshot:
    event_id: str | None = None
    type: str | None = None
    code: str | None = None
    message: str | None = None
    param: str | None = None

    def snapshot(self) -> dict[str, str | None]:
        return {
            "event_id": self.event_id,
            "type": self.type,
            "code": self.code,
            "message": self.message,
            "param": self.param,
        }


@dataclass(slots=True)
class QwenInterruptionState:
    interrupted_response_ids: set[str] = field(default_factory=set)
    stale_audio_blocked: int = 0
    stale_transcript_blocked: int = 0
    stale_completion_blocked: int = 0

    def mark_interrupted(self, response_id: str | None) -> None:
        if response_id:
            self.interrupted_response_ids.add(response_id)

    def is_interrupted(self, response_id: str | None) -> bool:
        return response_id is not None and response_id in self.interrupted_response_ids

    def snapshot(self) -> dict[str, object]:
        return {
            "interrupted_response_ids": sorted(self.interrupted_response_ids),
            "stale_audio_blocked": self.stale_audio_blocked,
            "stale_transcript_blocked": self.stale_transcript_blocked,
            "stale_completion_blocked": self.stale_completion_blocked,
        }


@dataclass(slots=True)
class QwenResponseProjection:
    response: ResponseState = ResponseState.NO_RESPONSE
    audio_output: LocalAudioOutputState = LocalAudioOutputState.NO_AUDIO_OUTPUT
    user_transcript: TranscriptState = TranscriptState.USER_TRANSCRIPT_EMPTY
    agent_transcript: TranscriptState = TranscriptState.AGENT_TRANSCRIPT_EMPTY
    usage: UsageState = UsageState.USAGE_ABSENT
    search: SearchUsageState = SearchUsageState.SEARCH_USAGE_MISSING
    error: ErrorState = ErrorState.NO_ERROR
    response_id: str | None = None
    item_id: str | None = None
    conversation_item_id: str | None = None
    content_part_type: str | None = None
    agent_speech_started: bool = False
    agent_speech_ended: bool = False
    agent_transcript_text: str = ""
    usage_snapshot: QwenUsageSnapshot | None = None
    cancel_error: QwenCancelErrorSnapshot | None = None

    def begin_response(self, response_id: str | None) -> None:
        self.response = ResponseState.RESPONSE_CREATED
        self.audio_output = LocalAudioOutputState.NO_AUDIO_OUTPUT
        self.agent_transcript = TranscriptState.AGENT_TRANSCRIPT_EMPTY
        self.usage = UsageState.USAGE_ABSENT
        self.search = SearchUsageState.SEARCH_USAGE_MISSING
        self.response_id = response_id
        self.item_id = None
        self.conversation_item_id = None
        self.content_part_type = None
        self.agent_speech_started = False
        self.agent_speech_ended = False
        self.agent_transcript_text = ""
        self.usage_snapshot = None
        self.cancel_error = None

    def snapshot(self) -> dict[str, str | None]:
        return {
            "response_id": self.response_id,
            "item_id": self.item_id,
            "conversation_item_id": self.conversation_item_id,
            "content_part_type": self.content_part_type,
            "response": self.response.value,
            "audio_output": self.audio_output.value,
            "user_transcript": self.user_transcript.value,
            "agent_transcript": self.agent_transcript.value,
            "usage": self.usage.value,
            "search": self.search.value,
            "error": self.error.value,
        }


class Qwen3Realtime(Realtime):
    provider_name = "qwen_realtime"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        base_url: str | None = None,
        voice: str = "Tina",
        fps: int = 1,
        include_video: bool = False,
        video_width: int = 1280,
        video_height: int = 720,
        audio_transcription_model: str = DEFAULT_AUDIO_TRANSCRIPTION_MODEL,
        turn_detection: TurnDetectionMode | None = "server_vad",
        vad_threshold: float = 0.1,
        vad_prefix_padding_ms: int = 500,
        vad_silence_duration_ms: int = 900,
        tools: list[ToolSchema | dict[str, Any]] | None = None,
        enable_search: bool = False,
        search_options: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(fps=fps)
        self.model = model
        self.voice = voice
        self.session_id = str(uuid.uuid4())

        self._base_url = base_url or DEFAULT_BASE_URL

        api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = cast(str, api_key)

        self._video_forwarder: VideoForwarder | None = None
        self._include_video = include_video
        self._real_client: Qwen3RealtimeClient | None = None
        self._processing_task: asyncio.Task | None = None
        self._video_width = video_width
        self._video_height = video_height
        self._executor = ThreadPoolExecutor(max_workers=1)

        self._is_responding = False
        self._current_response_id = None
        self._current_item_id = None
        self._current_participant: Participant | None = None
        self._input_turn_state = QwenInputTurnState()
        self._response_projection = QwenResponseProjection()
        self._interruption_state = QwenInterruptionState()
        self._audio_transcription_model = audio_transcription_model
        self._turn_detection = turn_detection
        self._vad_threshold = vad_threshold
        self._vad_prefix_padding_ms = vad_prefix_padding_ms
        self._vad_silence_duration_ms = vad_silence_duration_ms
        self._tools = list(tools or [])
        self._enable_search = enable_search
        self._search_options = dict(search_options or {})

    async def connect(self) -> None:
        # Stop the processing task first in case we're reconnecting
        await self._stop_processing_task()

        session_config = self._build_session_config()
        self._real_client = Qwen3RealtimeClient(
            api_key=self._api_key,
            base_url=self._base_url,
            model=self.model,
            config=session_config,
        )
        await self._real_client.connect()
        self._on_connected(session_config=session_config)
        logger.debug(f"Started Qwen3Realtime session at {self._base_url}")

        # Start the loop task
        self._start_processing_task()

    def _build_session_config(self) -> dict[str, Any]:
        if self._tools and self._enable_search:
            raise ValueError("Qwen realtime tools and enable_search are mutually exclusive")

        session_config: dict[str, Any] = {
            "modalities": ["text", "audio"],
            "voice": self.voice,
            "instructions": self._instructions,
            "input_audio_format": "pcm",
            "output_audio_format": "pcm",
            # Qwen3.5 contract docs identify this ASR model; live tolerance for older
            # gummy examples remains an external compatibility question.
            "input_audio_transcription": {"model": self._audio_transcription_model},
            "turn_detection": self._build_turn_detection_config(),
        }
        if self._tools:
            session_config["tools"] = self._convert_tools_to_provider_format(self._tools)
        if self._enable_search:
            session_config["enable_search"] = True
            if self._search_options:
                session_config["search_options"] = self._search_options
        return session_config

    def _build_turn_detection_config(self) -> dict[str, Any] | None:
        if self._turn_detection is None:
            return None
        if self._turn_detection not in ("server_vad", "semantic_vad"):
            raise ValueError("turn_detection must be 'server_vad', 'semantic_vad', or None")
        return {
            "type": self._turn_detection,
            "threshold": self._vad_threshold,
            "prefix_padding_ms": self._vad_prefix_padding_ms,
            "silence_duration_ms": self._vad_silence_duration_ms,
        }

    def _convert_tools_to_provider_format(self, tools: list[ToolSchema | dict[str, Any]]) -> list[dict[str, Any]]:
        qwen_tools: list[dict[str, Any]] = []
        for tool in tools:
            if tool.get("type") == "function" and isinstance(tool.get("function"), dict):
                qwen_tools.append(dict(tool))
                continue
            function: dict[str, Any] = {"name": tool["name"]}
            if description := tool.get("description"):
                function["description"] = description
            if parameters := tool.get("parameters_schema"):
                function["parameters"] = parameters
            qwen_tools.append({"type": "function", "function": function})
        return qwen_tools

    async def commit_audio_and_create_response(self) -> None:
        await self._client.commit_audio()
        self._input_turn_state.close_for_commit()
        await self._client.create_response()

    async def clear_audio(self) -> None:
        await self._client.clear_audio()
        self._input_turn_state.close_for_clear()

    async def simple_audio_response(self, pcm: PcmData, participant: Participant | None = None) -> None:
        if not self.connected:
            return
        self._current_participant = participant
        await self._client.send_audio(pcm=pcm)
        self._input_turn_state.mark_audio_appended()

    def _qwen_state_snapshot(self) -> dict[str, str]:
        return self._input_turn_state.snapshot()

    def _qwen_response_snapshot(self) -> dict[str, str | None]:
        return self._response_projection.snapshot()

    def _qwen_usage_snapshot(self) -> dict[str, Any]:
        usage = self._response_projection.usage_snapshot or QwenUsageSnapshot()
        return usage.snapshot()

    def _qwen_interruption_snapshot(self) -> dict[str, object]:
        return self._interruption_state.snapshot()

    def _qwen_cancel_error_snapshot(self) -> dict[str, str | None]:
        cancel_error = self._response_projection.cancel_error or QwenCancelErrorSnapshot()
        return cancel_error.snapshot()

    async def simple_response(
        self,
        text: str,
        participant: Participant | None = None,
    ) -> AsyncIterator[LLMResponseDelta | LLMResponseFinal]:
        logger.warning(f'Cannot reply to "{text}"; reason - Qwen3Realtime does not support text inputs')
        yield LLMResponseFinal()

    async def close(self) -> None:
        self._on_disconnected()
        await self.stop_watching_video_track()
        if self._processing_task is not None:
            self._processing_task.cancel()
            await self._processing_task

        self._executor.shutdown(wait=False)

        if self._real_client is not None:
            await self._real_client.close()
            self._real_client = None

    async def watch_video_track(
        self,
        track: aiortc.mediastreams.MediaStreamTrack,
        shared_forwarder: VideoForwarder | None = None,
    ) -> None:
        """
        Start sending video frames using VideoForwarder.

        Args:
            track: Video track to watch
            shared_forwarder: Optional shared VideoForwarder to use instead of creating a new one
        """

        # This method can be called multiple times with different forwarders
        # Remove handler from old forwarder if it exists
        await self.stop_watching_video_track()
        await self._on_video_track_reconnected()

        self._video_forwarder = shared_forwarder or VideoForwarder(
            input_track=cast(VideoStreamTrack, track),
            max_buffer=5,
            fps=float(self.fps),
            name="qwen3realtime_forwarder",
        )

        # Add frame handler (starts automatically)
        self._video_forwarder.add_frame_handler(self._send_video_frame, fps=self.fps)
        logger.info(f"Started video forwarding with {self.fps} FPS")

    async def _send_video_frame(self, frame: av.VideoFrame) -> None:
        """
        Send a video frame to Qwen3 Realtime API using send_realtime_input

        Parameters:
            frame: Video frame to send.
        """
        if not self._input_turn_state.can_send_image():
            # Qwen image permission is scoped to the current input turn. Historical
            # audio from an older turn or track cannot authorize this frame.
            return

        loop = asyncio.get_running_loop()

        # Run frame conversion in a separate thread to avoid blocking the loop.
        jpg_bytes = await loop.run_in_executor(
            self._executor,
            frame_to_jpeg_bytes,
            frame,
            self._video_width,
            self._video_height,
        )

        try:
            await self._client.send_frame(jpg_bytes)
        except Exception as e:
            logger.exception("Failed to send a video frame to Qwen3 Realtime API")
            self._emit_error_event(error=e, context="send_frame")

    async def stop_watching_video_track(self) -> None:
        if self._video_forwarder is not None:
            await self._video_forwarder.remove_frame_handler(self._send_video_frame)
            self._video_forwarder = None
            self._input_turn_state.mark_track_removed()
            logger.info("🛑 Stopped video forwarding to Qwen (participant left)")

    async def _on_video_track_reconnected(self) -> None:
        self._input_turn_state.mark_track_reconnected()

    @property
    def _client(self) -> Qwen3RealtimeClient:
        if self._real_client is None:
            raise ValueError("The Qwen3Realtime session is not established yet")
        return self._real_client

    async def _processing_loop(self) -> None:
        logger.debug("Start processing events by Qwen3Realtime")
        try:
            await self._process_events()
        except asyncio.CancelledError:
            logger.debug("Stop processing events by Qwen3Realtime")

    def _start_processing_task(self) -> None:
        self._processing_task = asyncio.create_task(self._processing_loop())

    async def _stop_processing_task(self) -> None:
        if self._processing_task is not None:
            self._processing_task.cancel()
            await self._processing_task

    async def _process_events(self) -> None:
        async for event in self._client.read():
            event_type = event.get("type")
            if event_type == "error":
                error = event["error"]
                logger.error(
                    f"Error received from Qwen3Realtime API: {error}",
                )
                if _is_image_timing_error(error):
                    self._input_turn_state.suspend_after_image_timing_error()
                    self._response_projection.error = ErrorState.INPUT_TIMING_ERROR
                elif _is_cancel_error(error):
                    self._record_cancel_error(event)
                else:
                    self._response_projection.error = ErrorState.UNKNOWN_QWEN_ERROR
                self._emit_error_event(
                    error=Exception(str(error)),
                    context="qwen_realtime_api",
                )
                continue

            elif event_type == "session.created":
                logger.debug("Qwen3Realtime session initialized successfully")

            elif event_type == "response.created":
                self._handle_response_created(event)
            elif event_type == "response.output_item.added":
                self._handle_response_output_item_added(event)
            elif event_type == "conversation.item.created":
                self._handle_conversation_item_created(event)
            elif event_type == "response.content_part.added":
                self._handle_response_content_part_added(event)
            elif event_type == "response.content_part.done":
                self._handle_response_content_part_done(event)
            elif event_type == "response.output_item.done":
                self._handle_response_output_item_done(event)
            elif event_type == "response.done":
                self._handle_response_done(event)
            elif event_type == "input_audio_buffer.speech_started":
                self._input_turn_state.mark_speech_started()
                self._emit_user_speech_started()
                await self._on_interruption()
            elif event_type == "input_audio_buffer.speech_stopped":
                self._input_turn_state.close_for_speech_stopped()
                self._emit_user_speech_ended()
            elif event_type == "input_audio_buffer.committed":
                self._input_turn_state.close_for_commit()
            elif event_type == "response.audio.delta":
                self._handle_response_audio_delta(event)
            elif event_type == "response.audio.done":
                self._handle_response_audio_done(event)
            elif event_type == "conversation.item.input_audio_transcription.delta":
                transcript = event.get("delta", "")
                if transcript:
                    self._response_projection.user_transcript = TranscriptState.USER_TRANSCRIPT_DELTA
                    self._emit_user_speech_transcription(text=transcript, mode="delta")
            elif event_type == "conversation.item.input_audio_transcription.completed":
                transcript = event.get("transcript", "")
                if transcript:
                    self._response_projection.user_transcript = TranscriptState.USER_TRANSCRIPT_FINAL
                    self._emit_user_speech_transcription(text=transcript, mode="final")
            elif event_type == "response.audio_transcript.delta":
                self._handle_response_audio_transcript_delta(event)
            elif event_type == "response.audio_transcript.done":
                self._handle_response_audio_transcript_done(event)
            elif event_type == "response.text.delta":
                self._handle_response_text_delta(event)

    def _handle_response_created(self, event: dict[str, Any]) -> None:
        response_id = _extract_response_id(event)
        self._current_response_id = response_id
        self._is_responding = True
        self._response_projection.begin_response(response_id)
        self._ensure_agent_speech_started(response_id)

    def _handle_response_output_item_added(self, event: dict[str, Any]) -> None:
        self._current_item_id = event.get("item", {}).get("id")
        self._response_projection.item_id = self._current_item_id
        self._response_projection.response = ResponseState.OUTPUT_ITEM_OPEN

    def _handle_conversation_item_created(self, event: dict[str, Any]) -> None:
        self._response_projection.conversation_item_id = event.get("item", {}).get("id")

    def _handle_response_content_part_added(self, event: dict[str, Any]) -> None:
        self._response_projection.response = ResponseState.CONTENT_PART_OPEN
        part = event.get("part", {})
        if isinstance(part, dict):
            self._response_projection.content_part_type = part.get("type")

    def _handle_response_content_part_done(self, event: dict[str, Any]) -> None:
        part = event.get("part", {})
        if isinstance(part, dict) and part.get("type"):
            self._response_projection.content_part_type = part["type"]

    def _handle_response_output_item_done(self, event: dict[str, Any]) -> None:
        item_id = event.get("item", {}).get("id")
        if item_id:
            self._current_item_id = item_id
            self._response_projection.item_id = item_id

    def _handle_response_done(self, event: dict[str, Any]) -> None:
        response_id = _extract_response_id(event) or self._current_response_id
        if self._is_stale_response(response_id):
            self._interruption_state.stale_completion_blocked += 1
            return
        self._response_projection.response_id = response_id
        self._response_projection.response = ResponseState.COMPLETED
        if "usage" in event:
            self._parse_response_usage(response_id=response_id, usage=event.get("usage"))
        elif self._response_projection.usage is UsageState.USAGE_ABSENT:
            self._response_projection.search = SearchUsageState.SEARCH_USAGE_MISSING
        # response.done is a lifecycle and usage boundary. The Qwen contract provides
        # transcript finality through response.audio_transcript.done, so emitting an
        # empty final here would invent assistant text the service did not send.
        self._is_responding = False
        self._current_response_id = None
        self._current_item_id = None

    def _handle_response_audio_delta(self, event: dict[str, Any]) -> None:
        response_id = _extract_response_id(event) or self._current_response_id
        if self._is_stale_response(response_id):
            self._interruption_state.stale_audio_blocked += 1
            self._response_projection.audio_output = LocalAudioOutputState.STALE_AUDIO_BLOCKED
            return
        self._response_projection.audio_output = LocalAudioOutputState.AUDIO_OUTPUT_STREAMING
        audio_bytes = base64.b64decode(event["delta"])
        pcm = PcmData.from_bytes(audio_bytes, 24000)
        self._ensure_agent_speech_started(response_id)
        self._emit_audio_output_event(pcm=pcm, response_id=response_id)

    def _handle_response_audio_done(self, event: dict[str, Any]) -> None:
        response_id = _extract_response_id(event) or self._current_response_id
        if self._is_stale_response(response_id):
            self._interruption_state.stale_completion_blocked += 1
            return
        self._response_projection.audio_output = LocalAudioOutputState.AUDIO_DONE_RECEIVED
        self._emit_audio_output_done_event(response_id=response_id, interrupted=False)
        self._response_projection.audio_output = LocalAudioOutputState.AUDIO_OUTPUT_DONE_EMITTED
        self._emit_agent_speech_ended(response_id=response_id, interrupted=False)
        self._response_projection.agent_speech_ended = True

    def _handle_response_audio_transcript_delta(self, event: dict[str, Any]) -> None:
        response_id = _extract_response_id(event) or self._current_response_id
        if self._is_stale_response(response_id):
            self._interruption_state.stale_transcript_blocked += 1
            self._response_projection.agent_transcript = TranscriptState.TRANSCRIPT_INTERRUPTED_BOUNDARY
            return
        delta = event.get("delta", "")
        if not delta:
            return
        self._response_projection.agent_transcript = TranscriptState.AGENT_TRANSCRIPT_DELTA
        self._response_projection.agent_transcript_text += delta
        self._emit_agent_speech_transcription(text=delta, mode="delta")

    def _handle_response_audio_transcript_done(self, event: dict[str, Any]) -> None:
        response_id = _extract_response_id(event) or self._current_response_id
        if self._is_stale_response(response_id):
            self._interruption_state.stale_transcript_blocked += 1
            self._response_projection.agent_transcript = TranscriptState.TRANSCRIPT_INTERRUPTED_BOUNDARY
            return
        transcript = event.get("transcript")
        if transcript is None:
            transcript = event.get("text")
        if transcript is None:
            transcript = self._response_projection.agent_transcript_text
        transcript = str(transcript)
        self._response_projection.agent_transcript = TranscriptState.AGENT_TRANSCRIPT_FINAL
        self._response_projection.agent_transcript_text = transcript
        self._emit_agent_speech_transcription(text=transcript, mode="final")

    def _handle_response_text_delta(self, event: dict[str, Any]) -> None:
        response_id = _extract_response_id(event) or self._current_response_id
        if self._is_stale_response(response_id):
            self._interruption_state.stale_transcript_blocked += 1
            self._response_projection.agent_transcript = TranscriptState.TRANSCRIPT_INTERRUPTED_BOUNDARY

    def _ensure_agent_speech_started(self, response_id: str | None) -> None:
        if self._response_projection.agent_speech_started:
            return
        self._response_projection.agent_speech_started = True
        self._emit_agent_speech_started(response_id=response_id)

    def _parse_response_usage(self, *, response_id: str | None, usage: object) -> None:
        usage_snapshot = QwenUsageSnapshot(response_id=response_id, raw_usage=usage)
        try:
            if not isinstance(usage, dict):
                raise TypeError(f"usage must be a dict, got {type(usage).__name__}")
            usage_snapshot.total_tokens = _optional_int(usage.get("total_tokens"))
            usage_snapshot.input_tokens = _optional_int(usage.get("input_tokens"))
            usage_snapshot.output_tokens = _optional_int(usage.get("output_tokens"))
            usage_snapshot.input_token_details = _optional_dict(usage.get("input_token_details"))
            usage_snapshot.output_token_details = _optional_dict(usage.get("output_token_details"))
            plugins = usage.get("plugins")
            if isinstance(plugins, dict):
                usage_snapshot.search_usage = _optional_dict(plugins.get("search"))
            self._response_projection.usage = UsageState.USAGE_PARSED
        except Exception as exc:
            usage_snapshot.parse_error = str(exc)
            self._response_projection.usage = UsageState.USAGE_PARSE_FAILED
        self._response_projection.search = SearchUsageState.SEARCH_USAGE_SEEN if usage_snapshot.search_usage is not None else SearchUsageState.SEARCH_USAGE_MISSING
        self._response_projection.usage_snapshot = usage_snapshot

    def _is_stale_response(self, response_id: str | None) -> bool:
        # Qwen does not guarantee response.cancel prevents already-in-flight
        # deltas, so replayed response ids are blocked before core projection.
        return self._interruption_state.is_interrupted(response_id)

    async def _on_interruption(self) -> None:
        """Handle user interruption of the current response."""
        if not self._should_interrupt_current_response():
            return

        response_id = self._current_response_id or self._response_projection.response_id
        self._response_projection.response = ResponseState.CANCEL_REQUESTED
        self._interruption_state.mark_interrupted(response_id)
        self._emit_local_interruption(response_id)

        if response_id:
            await self._client.cancel_response()

        self._is_responding = False
        self._current_response_id = None
        self._current_item_id = None

    def _should_interrupt_current_response(self) -> bool:
        if self._current_response_id or self._is_responding:
            return True
        return (
            self._response_projection.response
            in {
                ResponseState.RESPONSE_CREATED,
                ResponseState.OUTPUT_ITEM_OPEN,
                ResponseState.CONTENT_PART_OPEN,
                ResponseState.CANCEL_REQUESTED,
            }
            or self._response_projection.audio_output
            in {
                LocalAudioOutputState.AUDIO_OUTPUT_STREAMING,
                LocalAudioOutputState.AUDIO_DONE_RECEIVED,
                LocalAudioOutputState.AUDIO_OUTPUT_DONE_EMITTED,
            }
            or self._response_projection.agent_transcript is TranscriptState.AGENT_TRANSCRIPT_DELTA
        )

    def _emit_local_interruption(self, response_id: str | None) -> None:
        self._response_projection.response = ResponseState.INTERRUPTED
        self._response_projection.audio_output = LocalAudioOutputState.AUDIO_INTERRUPTED
        self._emit_audio_output_done_event(response_id=response_id, interrupted=True)
        self._response_projection.audio_output = LocalAudioOutputState.AUDIO_FLUSH_EMITTED
        if not self._response_projection.agent_speech_ended:
            self._emit_agent_speech_ended(response_id=response_id, interrupted=True)
            self._response_projection.agent_speech_ended = True
        if self._response_projection.agent_transcript_text:
            self._response_projection.agent_transcript = TranscriptState.TRANSCRIPT_INTERRUPTED_BOUNDARY

    def _record_cancel_error(self, event: dict[str, Any]) -> None:
        error = event.get("error", {})
        if not isinstance(error, dict):
            error = {}
        self._response_projection.error = ErrorState.CANCEL_ERROR
        self._response_projection.cancel_error = QwenCancelErrorSnapshot(
            event_id=event.get("event_id") if isinstance(event.get("event_id"), str) else None,
            type=error.get("type") if isinstance(error.get("type"), str) else None,
            code=error.get("code") if isinstance(error.get("code"), str) else None,
            message=error.get("message") if isinstance(error.get("message"), str) else None,
            param=error.get("param") if isinstance(error.get("param"), str) else None,
        )


def _is_image_timing_error(error: dict[str, Any]) -> bool:
    code = str(error.get("code", "")).lower()
    message = str(error.get("message", "")).lower()
    param = str(error.get("param", "")).lower()
    text = " ".join((code, message, param))
    return "image" in text and ("before" in text or "timing" in text or "audio" in text or "input_image_buffer" in text)


def _is_cancel_error(error: dict[str, Any]) -> bool:
    code = str(error.get("code", "")).lower()
    message = str(error.get("message", "")).lower()
    param = str(error.get("param", "")).lower()
    text = " ".join((code, message, param))
    return "cancel" in text or "cancellable" in text or "response.cancel" in text


def _extract_response_id(event: dict[str, Any]) -> str | None:
    response = event.get("response")
    if isinstance(response, dict) and isinstance(response.get("id"), str):
        return response["id"]
    response_id = event.get("response_id")
    if isinstance(response_id, str):
        return response_id
    return None


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError("boolean token counts are invalid")
    if isinstance(value, int):
        return value
    raise TypeError(f"token count must be an int or None, got {type(value).__name__}")


def _optional_dict(value: object) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    raise TypeError(f"usage detail must be a dict or None, got {type(value).__name__}")
