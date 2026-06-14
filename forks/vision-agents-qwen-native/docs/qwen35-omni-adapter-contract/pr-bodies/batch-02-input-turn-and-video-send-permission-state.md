## Summary

This PR implements Batch 02 of the Qwen3.5 Omni Realtime WebSocket adapter contract: current input-turn state and video send-permission state.

The Qwen adapter no longer uses historical `_audio_emitted_once` as the video gate. It now keeps an explicit input-turn/video state object, updates it on audio append, speech started/stopped, committed, Manual commit/clear, track removal/reconnect, and image timing errors, and exposes a test-visible state projection.

## Scope

- `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
  - Adds `InputAudioState`, `VideoPermissionState`, and `QwenInputTurnState`.
  - Replaces historical audio gating with current-turn video permission.
  - Closes image sending on speech stopped, committed, Manual commit, Manual clear, track removal, track reconnect, and image timing errors.
  - Emits existing core user speech started/ended events for Qwen `input_audio_buffer.speech_started` and `input_audio_buffer.speech_stopped`.
  - Keeps structured error modeling out of scope except for the narrow image timing detector.
- `plugins/qwen/tests/test_qwen_realtime.py`
  - Adds fake-client/event tests for current-turn image gating, speech event projection, Manual commit/clear, committed server event, track reconnect, and image timing error suspension.
- `docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md`
  - Records assertion results, verification commands, blockers, and non-goals.
- `docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state-review.md`
  - Records the independent review result for final reviewed HEAD `8b5423c`.
- `docs/qwen35-omni-adapter-contract/coordinator-state.md`
  - Records the coordinator promotion decision and next batch boundary.

## Repository Rationale

The changed runtime files live inside the controlled `vision-agents-qwen-native` fork that TideSync loads through local editable dependencies. Video/image timing is provider behavior: TideSync outer agent code cannot enforce Qwen's current-input-turn audio-before-image contract after frames enter the Qwen adapter.

This PR belongs in the controlled fork because the 09 contract requires Qwen adapter state to be reviewable in the TideSync PR diff and covered by repeatable fake/event evidence.

## Contract Coverage

- `speech-events-map-to-user-turn`: covered by replaying Qwen speech started/stopped events and asserting core speech started/ended events.
- `image-not-sent-before-turn-audio`: covered by sending a frame before current-turn audio and asserting no image append.
- `image-window-closes-after-speech-stopped`: covered by speech stopped replay and committed event replay.
- `image-timing-error-suspends-sending`: covered by structured Qwen error injection and send-log assertions.
- `track-reconnect-waits-for-current-audio`: covered by removal/reconnect plus before/after audio frame checks.

## Verification

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Note: root pytest coverage settings emitted no-data warnings because the narrow test did not import `tidesync`.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `13 passed, 2 skipped`.
  - Note: the skipped tests are the existing live integration tests; coverage emitted the same no-data warning because plugin tests are outside the configured `tidesync` coverage package.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `3 files already formatted`.
- Independent review:
  - Result: `APPROVED_WITH_NOTES`.
  - Report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state-review.md`.

## Live Verification / Blockers

Live API smoke was not run. No valid API key, cost authorization, or live service availability was provided to this executor.

The following remain live compatibility unknowns:

- Exact live Qwen error payload variants for image timing violations.
- Live event ordering around `speech_stopped`, `input_audio_buffer.committed`, and track reconnect behavior.

## Rollback Impact

Rolling this PR back returns the adapter to historical audio gating for images. A single previous audio append would again authorize later tracks or later turns to send images before current-turn audio, and speech stopped, Manual commit/clear, track reconnect, and image timing errors would no longer close or suspend image sending for the current turn.
