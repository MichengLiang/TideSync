# Batch 03 Report: Server Event Mapping For Audio Transcript And Usage

Branch: `feature/qwen35-server-event-mapping`

Commit SHA: `PENDING_COMMIT`

## Files Changed

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-03-server-event-mapping-speech-audio-transcript-usage.md`

No unrelated working-tree changes were observed during this batch.

## Contract IDs Covered

- `response-lifecycle-events-contract`
- `audio-output-events-contract`
- `transcript-events-contract`
- `usage-events-contract`
- `usage-contract`
- `audio-delta-and-done-map-to-output`
- `transcript-delta-and-done-map-to-final`
- `response-done-parses-usage`
- `event-replay-tests`
- `state-machine-tests`
- `pr-conformance-statement`

## Implementation Summary

Batch 03 adds a dedicated test-visible `QwenResponseProjection` alongside the Batch 02 input-turn/video state. The response projection records response lifecycle, local audio output state, user and assistant transcript state, usage state, search usage state, response id, item ids, content part type, accumulated assistant transcript text, and the last usage snapshot.

The server reader now handles these non-interruption events:

- `response.created`
- `response.output_item.added`
- `conversation.item.created`
- `response.content_part.added`
- `response.content_part.done`
- `response.output_item.done`
- `response.audio.delta`
- `response.audio.done`
- `conversation.item.input_audio_transcription.delta`
- `conversation.item.input_audio_transcription.completed`
- `response.audio_transcript.delta`
- `response.audio_transcript.done`
- `response.done`

`response.done` now closes response state and parses usage. It no longer emits an empty assistant transcript final. Assistant transcript finality comes from `response.audio_transcript.done`, using the server-provided transcript when present and the locally accumulated delta text when the done payload omits text.

Usage parsing retains raw usage, top-level token fields, token details, and `usage.plugins.search` in `_qwen_usage_snapshot()`. If a present usage payload cannot be parsed, the raw payload is retained and the projection enters `usage_parse_failed` with a parse error. The current Vision Agents core surface has no obvious public metrics/event carrier for this full usage structure, so Batch 03 exposes usage through adapter test projection and records that metrics projection boundary here.

## Assertion Results

| Assertion | Result | Evidence |
|---|---|---|
| `audio-delta-and-done-map-to-output` | PASS | `test_response_audio_delta_and_done_emit_output_boundary` replays `response.created`, `response.audio.delta`, and `response.audio.done`; asserts `RealtimeAudioOutput(response_id="resp_1")`, `RealtimeAudioOutputDone(interrupted=False, response_id="resp_1")`, agent speech started/ended, 24 kHz PCM, and `audio_output_done_emitted`. |
| `transcript-delta-and-done-map-to-final` | PASS | `test_audio_transcript_delta_and_done_emit_non_empty_final` verifies delta events followed by a non-empty final from `response.audio_transcript.done`; `test_audio_transcript_done_uses_accumulated_delta_when_done_omits_text` verifies accumulated delta fallback. |
| `response-done-parses-usage` | PASS | `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final` verifies completed response state, raw usage retention, parsed token fields, and `plugins.search`; `test_response_done_usage_parse_failure_retains_raw_payload` verifies raw retention and parse failure state. |

## Response Lifecycle Coverage

`test_response_lifecycle_events_update_state_projection` replays `response.created`, `response.output_item.added`, `conversation.item.created`, `response.content_part.added`, `response.content_part.done`, `response.output_item.done`, and `response.done`. It asserts the response id, output item id, conversation item id, content part type, completed state, absent usage, missing search usage, and empty audio/transcript states.

Batch 03 intentionally does not implement stale response isolation after cancel. That belongs to Batch 04. Response ids are preserved on `RealtimeAudioOutput`, `RealtimeAudioOutputDone`, and agent speech started/ended events where Vision Agents core currently supports a `response_id` field. `RealtimeAgentTranscript` and `RealtimeUserTranscript` do not currently expose response ids, so transcript response-id projection remains limited to adapter state and replay evidence.

## Test Commands And Output Summary

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Warning: known narrow-test coverage warnings: `Module tidesync was never imported`, `No data was collected`, and no coverage report.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `20 passed, 2 skipped`.
  - Warning: same known coverage no-data warnings; skipped tests are existing live integration tests.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `2 files already formatted`.

Additional TDD evidence:

- Before implementation, `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py` failed on the new Batch 03 replay tests for missing audio done, transcript done, usage projection, lifecycle projection, user delta mapping, and the existing empty final from `response.done`.

## Known Unknowns And Live Verification Blockers

- Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability for this batch.
- The exact live payload variants for `response.audio_transcript.done` and usage plugin fields remain unverified. The implementation accepts `transcript`, falls back to `text`, then falls back to accumulated deltas.
- Core metrics/event projection for full usage and search usage is not implemented because the current Vision Agents core event types do not expose a clear usage carrier for the raw provider structure. Adapter test projection is the Batch 03 evidence surface.

## Explicit Non-Goals Left For Future Batches

- Batch 04: interruption flush path, stale response isolation after cancel, cancelled response id handling, and cancel error behavior.
- Batch 05: tool execution flow, function call argument assembly, function output send-back, and structured tool errors.
- Batch 06: structured Qwen error model, reconnect state reset, and full PR conformance closure.
- Text-only output mapping for `response.text.delta` and `response.text.done` was not added in Batch 03 because the current adapter session uses `modalities: ["text", "audio"]` for audio responses and the handoff only requires text-only support if explicitly implemented.
