# Batch 02 Report: Input Turn And Video Send-Permission State

Branch: `feature/qwen35-input-turn-video-state`

Implementation commit SHA: final commit on this branch; record with `git rev-parse --short HEAD` after commit.

## Files Changed

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-02-input-turn-and-video-send-permission-state.md`

## Contract IDs Covered

- `audio-append-contract`
- `image-append-contract`
- `input-buffer-events-contract`
- `input-audio-state`
- `video-frame-state`
- `image-timing-error-contract`
- `speech-events-map-to-user-turn`
- `image-not-sent-before-turn-audio`
- `image-window-closes-after-speech-stopped`
- `image-timing-error-suspends-sending`
- `track-reconnect-waits-for-current-audio`
- `event-replay-tests`
- `fake-websocket-tests`
- `state-machine-tests`

## Assertion Results

`speech-events-map-to-user-turn`: PASS.

Evidence: `test_speech_events_update_turn_and_close_image_window` replays `input_audio_buffer.speech_started` and `input_audio_buffer.speech_stopped`, asserts `RealtimeUserSpeechStarted` and `RealtimeUserSpeechEnded` appear in the provider output stream, and verifies the state projection moves to `input_audio: speech_stopped` and `video: send_closed_for_turn`.

`image-not-sent-before-turn-audio`: PASS.

Evidence: `test_video_frame_not_sent_before_current_turn_audio` calls `_send_video_frame()` before any current-turn audio append and asserts the fake client only saw `session.update`; state projection remains `turn_empty` / `track_available_waiting_audio`.

`image-window-closes-after-speech-stopped`: PASS.

Evidence: `test_speech_events_update_turn_and_close_image_window` verifies no image append is sent after a `speech_stopped` replay for the same turn. `test_input_audio_buffer_committed_event_closes_image_window` covers the related `input_audio_buffer.committed` server event.

`image-timing-error-suspends-sending`: PASS.

Evidence: `test_image_timing_error_suspends_until_new_audio_turn` injects a structured Qwen error with `code`, `message`, and `param` indicating image-before-audio timing. The adapter preserves error emission behavior, enters suspended video state, blocks the next frame, and allows sending again only after a new audio append establishes a valid turn.

`track-reconnect-waits-for-current-audio`: PASS.

Evidence: `test_track_reconnect_waits_for_current_turn_audio` sends one valid audio/image pair, simulates track removal and reconnect, proves the post-reconnect frame is blocked before new current-turn audio, then proves a new audio append reopens image permission.

## Test Commands And Output Summary

Red test runs before implementation:

- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py -q`
  - Result before implementation: `6 failed, 6 passed, 2 skipped`.
  - Expected failures: missing state projection, missing speech start/end projection, missing provider clear hook, missing reconnect hook, and image timing error not suspending sends.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py::test_input_audio_buffer_committed_event_closes_image_window -q`
  - Result before committed-event handling: `1 failed`.
  - Expected failure: `input_audio_buffer.committed` was ignored, so a later image append was sent.

Final verification:

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Note: pytest-cov emitted warnings that `tidesync` was not imported and no coverage data was collected. The command still passed; these warnings are caused by root coverage settings on a narrow import-path test.

- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `13 passed, 2 skipped`.
  - Note: pytest-cov emitted the same no-data warning because the command targets plugin tests outside the configured `tidesync` coverage package. The two skipped tests are the pre-existing live integration tests.

- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`

- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `3 files already formatted`.

## Known Unknowns And Live Verification Blockers

- Live Qwen image timing error payload variants remain unverified. The implementation uses conservative matching over `error.code`, `error.message`, and `error.param` and avoids replacing the future structured Qwen error model.
- Live service behavior for track reconnect, speech stopped, and committed event ordering was not verified because no API key, cost authorization, or service availability was provided to this executor.
- The current tests call provider internals directly for deterministic fake evidence. They do not exercise the real `VideoForwarder` timing loop.

## Explicit Non-Goals Left For Future Batches

- Full audio output done mapping.
- Transcript done mapping.
- `response.done` usage parsing.
- Interruption flush path, stale response isolation, and cancel error behavior.
- Tool execution flow and search usage parsing.
- Structured Qwen error model beyond the narrow image timing detector.
- Reconnect state reset beyond the local video-track permission reset needed for this batch.
