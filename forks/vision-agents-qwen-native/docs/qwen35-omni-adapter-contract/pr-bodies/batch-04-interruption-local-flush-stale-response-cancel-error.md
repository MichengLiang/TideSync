## Summary

This PR implements Batch 04 of the Qwen3.5 Omni Realtime WebSocket adapter contract: barge-in interruption state, local audio flush projection, stale response isolation, and cancel-error evidence.

## Scope

- Turns `input_audio_buffer.speech_started` into a real interruption path when agent output or locally playable output is active.
- Emits `RealtimeAudioOutputDone(interrupted=True)` and `RealtimeAgentSpeechEnded(interrupted=True)` before relying on remote cancel success.
- Sends `response.cancel` when a current response id is cancellable.
- Records interrupted response ids and blocks late stale audio, transcript, text delta, and completion events for those ids.
- Preserves structured cancel-error fields needed by Batch 04 replay tests.
- Adds deterministic replay tests for barge-in, cancel error, stale delayed deltas, and a non-stale follow-up response.

## Repository Rationale

`vision-agents-qwen-native` is the controlled TideSync fork carrying the Qwen realtime adapter used by the runtime path. The 09 contract book requires Qwen interruption behavior to be projected through Vision Agents core carriers and deterministic adapter state, not just remote `response.cancel` or logs. This PR keeps the change inside the controlled adapter and replay tests, with no core, client, root dependency, or TideSync outer runtime edits.

## Contract Coverage

- `speech-started-interrupts-current-response`: covered by `test_speech_started_interrupts_active_response_and_flushes_local_audio`.
- `cancel-error-does-not-block-local-flush`: covered by `test_cancel_error_does_not_block_local_flush_or_stale_isolation`.
- `stale-delta-after-interrupt-blocked`: covered by `test_stale_audio_and_transcript_deltas_after_interrupt_are_blocked`.
- Later valid response id after interruption: covered by `test_follow_up_response_after_interrupt_is_not_treated_as_stale`.

The adapter uses existing core carriers: `RealtimeAudioOutputDone(interrupted=True)` triggers `RealtimeInferenceFlow.interrupt()`, and `RealtimeAgentSpeechEnded(interrupted=True)` projects the agent turn interruption. No core runtime changes are required for this batch.

## Verification

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `1 passed`
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `24 passed, 2 skipped`
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `2 files already formatted`

The pytest commands emit the existing narrow-test coverage warnings that `tidesync` was not imported and no coverage data was collected.

## Live Verification / Blockers

Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability for this batch. Replay tests are the required evidence surface for Batch 04. The `interruption-latency-measured` `should` item remains unmeasured for the same reason.

## Rollback Impact

Rolling back this PR would return the adapter to the prior interruption behavior: `speech_started` may send remote `response.cancel`, but local audio flush would not be triggered, stale delayed response events could re-enter current output, and cancel errors would not have deterministic structured projection.
