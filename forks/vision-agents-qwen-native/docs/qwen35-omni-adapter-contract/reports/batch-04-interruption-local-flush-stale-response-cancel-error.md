# Batch 04 Report: Interruption Local Flush Stale Response And Cancel Error

Branch: `feature/qwen35-interruption-state`

Implementation commit SHA: `830f914`

Review-fix commit SHA: `105ee3f`

## Files Changed

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-04-interruption-local-flush-stale-response-cancel-error.md`

No unrelated working-tree changes were observed during initial implementation. During the review-fix pass, the reviewer report existed as an untracked local file at `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error-review.md`; it was preserved and not staged.

## Contract IDs Covered

- `interruption-trigger-contract`
- `remote-cancel-contract`
- `local-flush-contract`
- `stale-response-contract`
- `turn-redirection-contract`
- `error-events-contract`
- `structured-error-contract`
- `speech-started-interrupts-current-response`
- `cancel-error-does-not-block-local-flush`
- `stale-delta-after-interrupt-blocked`
- `event-replay-tests`
- `state-machine-tests`

## Implementation Summary

Batch 04 extends the existing Qwen response projection with interruption state, cancel-error state, local-audio interrupted/flushed states, stale-audio blocking, and transcript interruption boundary states. It adds a single `QwenInterruptionState` that records interrupted response ids and stale audio/transcript/completion block counts.

The adapter now handles `input_audio_buffer.speech_started` as a real barge-in path when a response, local audio output, or unfinished assistant transcript is active. A review fix removed the call-site `_is_responding` gate so `_should_interrupt_current_response()` is reachable when `_is_responding` has already been cleared but response projection or local audio state still carries stale-response risk. The path emits the existing core public carriers:

- `RealtimeUserSpeechStarted`
- `RealtimeAudioOutputDone(interrupted=True, response_id=<interrupted id>)`
- `RealtimeAgentSpeechEnded(interrupted=True, response_id=<interrupted id>)`

The local flush path runs before any remote cancel acknowledgement. If a current response id exists, the adapter sends `response.cancel` and records that response id as interrupted. Late events for interrupted response ids are blocked before they can re-enter current core projection.

The adapter preserves structured cancel-error fields in `_qwen_cancel_error_snapshot()` for deterministic tests: `event_id`, `error.type`, `error.code`, `error.message`, and `error.param`.

## Assertion Results

| Assertion | Result | Evidence |
|---|---|---|
| `speech-started-interrupts-current-response` | PASS | `test_speech_started_interrupts_active_response_and_flushes_local_audio` replays `resp_1` audio/transcript output followed by `input_audio_buffer.speech_started`; asserts user speech started, interrupted audio done, interrupted agent speech ended, `response.cancel`, `interrupted`, `audio_flush_emitted`, transcript interruption boundary, and interrupted response id tracking. `test_speech_started_interrupts_after_response_done_when_local_audio_remains_risky` covers the review finding where `_is_responding` is already false after `response.done` but local audio/response projection state still requires interruption and stale isolation. |
| `cancel-error-does-not-block-local-flush` | PASS | `test_cancel_error_does_not_block_local_flush_or_stale_isolation` replays local interruption followed by a no-cancellable-response error and a late `resp_1` audio delta; asserts local flush remains interrupted/flushed, only pre-interrupt audio is emitted, stale isolation remains active, and structured cancel error fields are retained. |
| `stale-delta-after-interrupt-blocked` | PASS | `test_stale_audio_and_transcript_deltas_after_interrupt_are_blocked` replays late audio delta, transcript delta, transcript done, and response done for interrupted `resp_1`; asserts no second playable audio, no stale transcript completion, interrupted state is retained, and stale block counters increment. |

Additional coverage:

- `test_follow_up_response_after_interrupt_is_not_treated_as_stale` proves a later valid `resp_2` can still emit audio and transcript after `resp_1` interruption.
- `test_speech_started_interrupts_after_response_done_when_local_audio_remains_risky` proves `speech_started` still enters the interruption path after `response.done` clears `_is_responding`, and blocks a late `resp_1` audio delta.
- Existing Batch 01 through Batch 03 tests are preserved.

## Local Flush And Stale Isolation State Summary

The response projection now includes:

- `response="cancel_requested"` while entering remote cancel.
- `response="interrupted"` after local interruption has been projected.
- `audio_output="audio_interrupted"` during local interruption and `audio_output="audio_flush_emitted"` after `RealtimeAudioOutputDone(interrupted=True)` is emitted.
- `audio_output="stale_audio_blocked"` when a late interrupted response audio delta is dropped.
- `agent_transcript="transcript_interrupted_boundary"` when unfinished assistant transcript text is interrupted or late transcript events are blocked.

`QwenInterruptionState` is the source of truth for interrupted response ids and stale event counters. It blocks `response.audio.delta`, `response.audio.done`, `response.audio_transcript.delta`, `response.audio_transcript.done`, `response.text.delta`, and `response.done` for interrupted response ids. This keeps late `response.cancel` fallout from becoming current playable output or a completed assistant answer.

## Cancel-Error Projection Summary

Cancel errors are detected from Qwen `error` payload fields that mention cancel, cancellable, or `response.cancel`. The adapter records the structured subset required by Batch 04:

- `event_id`
- `error.type`
- `error.code`
- `error.message`
- `error.param`

The cancel-error path does not reset response state, local audio state, or interrupted response ids. Existing image timing error behavior is preserved and still suspends video sending.

## Test Commands And Output Summary

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Warning: known narrow-test coverage warnings: `Module tidesync was never imported`, `No data was collected`, and no coverage report.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `25 passed, 2 skipped`.
  - Warning: same known coverage no-data warnings; skipped tests are existing live integration tests.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `2 files already formatted`.

Additional TDD evidence:

- Before implementation, `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py` failed on the new Batch 04 replay tests because no interrupted local audio done event was emitted, cancel error did not retain local flush state, and stale `resp_1` audio still entered output.
- During the review fix, `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py::test_speech_started_interrupts_after_response_done_when_local_audio_remains_risky` failed before the code change because a late `resp_1` audio delta emitted a second playable `RealtimeAudioOutput` after `response.done` and `speech_started`.

## Known Unknowns And Live Verification Blockers

- Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability for this batch.
- The `interruption-latency-measured` assertion is a `should` item and was not measured in live smoke because live verification is blocked. No product SLO or measurement environment is defined in this batch.
- The cancel-error detector intentionally covers the Batch 04 subset. Full structured error taxonomy, recoverability decisions, and reconnect state reset remain future work.

## Explicit Non-Goals Left For Future Batches

- Batch 05: tool execution, search flow, function call handling, and tool errors.
- Batch 06: full structured Qwen error model, reconnect state reset, final evidence closure, and full PR conformance closure.
- Text-only output support remains unimplemented; Batch 04 only blocks stale `response.text.delta` for interrupted response ids.
