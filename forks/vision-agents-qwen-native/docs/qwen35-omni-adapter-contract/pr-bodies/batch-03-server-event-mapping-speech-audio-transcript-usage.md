## Summary

This PR implements Batch 03 of the Qwen3.5 Omni Realtime WebSocket adapter contract: non-interruption server event mapping for response lifecycle, audio output done, assistant/user transcripts, and `response.done.usage`.

## Scope

- Adds a test-visible Qwen response projection for response lifecycle, local audio output, transcript, usage, and search usage states.
- Maps `response.audio.done` to `RealtimeAudioOutputDone(interrupted=False)` and agent speech ended.
- Maps `response.audio_transcript.done` to assistant transcript final using server text or accumulated deltas.
- Stops treating `response.done` as an empty assistant transcript final.
- Parses and retains `response.done.usage`, including raw usage and `plugins.search`.
- Adds replay tests for Batch 03 assertions and preserves existing skipped live tests.
- Records independent review and coordinator promotion evidence for final reviewed HEAD `223cc13`.

## Repository Rationale

`vision-agents-qwen-native` is the controlled TideSync fork that carries the Qwen realtime adapter used by the runtime path. The 09 contract book requires Qwen server events to enter Vision Agents core events or a test-visible projection rather than private logs. This PR keeps the change in the controlled adapter and replay tests so the behavior is reviewable in TideSync PR diff and repeatable without live Qwen service access.

## Contract Coverage

- `audio-delta-and-done-map-to-output`: covered by `test_response_audio_delta_and_done_emit_output_boundary`.
- `transcript-delta-and-done-map-to-final`: covered by `test_audio_transcript_delta_and_done_emit_non_empty_final` and `test_audio_transcript_done_uses_accumulated_delta_when_done_omits_text`.
- `response-done-parses-usage`: covered by `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final`.
- Usage parse failure raw retention: covered by `test_response_done_usage_parse_failure_retains_raw_payload`.
- Response lifecycle projection: covered by `test_response_lifecycle_events_update_state_projection`.
- User transcript delta/completed mapping: covered by `test_user_input_audio_transcription_delta_and_completed_emit_transcripts`.

Projection boundary: `RealtimeAudioOutput`, `RealtimeAudioOutputDone`, and agent speech events can carry `response_id`. Current core transcript event types do not carry response ids, and current core has no clear public usage event surface for full raw provider usage, so transcript/usage evidence is exposed through adapter test projections and documented in the Batch 03 report.

## Verification

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `1 passed`
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `20 passed, 2 skipped`
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `2 files already formatted`
- Independent review:
  - Result: `APPROVED_WITH_NOTES`.
  - Report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage-review.md`.

The pytest commands emit the existing narrow-test coverage warnings that `tidesync` was not imported and no coverage data was collected.

## Live Verification / Blockers

Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability for this batch. Replay tests are the required evidence surface for Batch 03.

## Rollback Impact

Rolling back this PR would return the adapter to the prior partial server-event mapping: no explicit audio done boundary, assistant transcript final still missing from transcript done, usage/search usage not retained, response lifecycle state not test-visible, and `response.done` again serving as an empty assistant transcript final substitute.
