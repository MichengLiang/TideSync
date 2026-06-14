import asyncio
import base64
import logging
import os
import uuid
from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
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
                self._emit_error_event(
                    error=Exception(str(error)),
                    context="qwen_realtime_api",
                )
                continue

            elif event_type == "session.created":
                logger.debug("Qwen3Realtime session initialized successfully")

            elif event_type == "response.created":
                self._current_response_id = event.get("response", {}).get("id")
                self._is_responding = True
            elif event_type == "response.output_item.added":
                self._current_item_id = event.get("item", {}).get("id")
            elif event_type == "response.done":
                self._emit_agent_speech_transcription(text="", mode="final")
                self._is_responding = False
                self._current_response_id = None
                self._current_item_id = None
            elif event_type == "input_audio_buffer.speech_started":
                self._input_turn_state.mark_speech_started()
                self._emit_user_speech_started()
                if self._is_responding:
                    await self._on_interruption()
            elif event_type == "input_audio_buffer.speech_stopped":
                self._input_turn_state.close_for_speech_stopped()
                self._emit_user_speech_ended()
            elif event_type == "input_audio_buffer.committed":
                self._input_turn_state.close_for_commit()
            elif event_type == "response.audio.delta":
                audio_bytes = base64.b64decode(event["delta"])
                pcm = PcmData.from_bytes(audio_bytes, 24000)
                self._emit_audio_output_event(pcm=pcm)
            elif event_type == "conversation.item.input_audio_transcription.completed":
                transcript = event.get("transcript", "")
                if transcript:
                    self._emit_user_speech_transcription(text=transcript, mode="final")
            elif event_type == "response.audio_transcript.delta":
                delta = event.get("delta", "")
                if delta:
                    self._emit_agent_speech_transcription(text=delta, mode="delta")

    async def _on_interruption(self) -> None:
        """Handle user interruption of the current response."""
        if not self._is_responding:
            return

        if self._current_response_id:
            await self._client.cancel_response()

        self._is_responding = False
        self._current_response_id = None
        self._current_item_id = None


def _is_image_timing_error(error: dict[str, Any]) -> bool:
    code = str(error.get("code", "")).lower()
    message = str(error.get("message", "")).lower()
    param = str(error.get("param", "")).lower()
    text = " ".join((code, message, param))
    return "image" in text and ("before" in text or "timing" in text or "audio" in text or "input_image_buffer" in text)
