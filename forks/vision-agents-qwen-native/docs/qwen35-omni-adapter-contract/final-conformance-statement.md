# Final Conformance Statement: Qwen3.5 Omni Realtime WebSocket Adapter Contract

Branch: `feature/qwen35-error-reconnect-conformance`

Implementation commit SHA: `3b26850`

Contract book: `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc`

## Implementation Scope

This closure covers the controlled Qwen adapter implementation in:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `tests/test_vision_agents_runtime_path.py`

Batch 06 adds structured Qwen error preservation, remaining error classifications, session config failure state, recoverable reconnect reset behavior, usage parse error closure, and this conformance statement. Prior accepted batches cover controlled source/import evidence, session config/client sends, input-turn video permission state, server event mapping, interruption/local flush/stale response/cancel error behavior, and tools/search/tool errors.

No 09 contract book files, TideSync outer runtime files, root dependency resolution, or core Vision Agents runtime files were edited in Batch 06.

## Upstream Source

Source provenance is recorded in `forks/vision-agents-qwen-native/UPSTREAM.adoc`:

- Repository: `https://github.com/GetStream/Vision-Agents`
- Tag: `v0.6.4`
- Commit: `9c5efe1ef4552efacef83de90a6b4870e2444c7b`
- Import date: `2026-06-14`
- Imported paths: `agents-core`, `plugins/qwen`, `plugins/getstream`
- Omitted paths: other plugins, examples, docs/assets/automation, upstream `.git`
- Local modification policy: local changes serve the Qwen3.5 Omni Realtime WebSocket adapter contract, TideSync dependency resolution, runtime import evidence, and adapter tests.

## Runtime Path Evidence

Runtime source evidence is provided by:

- `tests/test_vision_agents_runtime_path.py`
- Batch 00 accepted baseline in `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md`
- Batch 01 report/review evidence under `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/`

The required runtime-path command was run in Batch 06:

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`

## Assertion Results

| Assertion | Status | Evidence |
|---|---|---|
| `adapter-source-in-tidesync-pr` | PASS | Controlled fork exists under `forks/vision-agents-qwen-native`; Batch 00/01 evidence and runtime path test remain present. |
| `runtime-imports-controlled-adapter` | PASS | `uv run pytest tests/test_vision_agents_runtime_path.py` result: `1 passed`. |
| `dependency-resolution-reproducible` | PASS | Batch 00/01 evidence records local editable source resolution and `UPSTREAM.adoc`; no Batch 06 dependency changes. |
| `session-update-uses-qwen35-contract-values` | PASS | Batch 01 report and `test_session_update_uses_qwen35_contract_defaults`. |
| `semantic-vad-configurable` | PASS | Batch 01 report and `test_semantic_vad_is_visible_in_session_update`. |
| `manual-mode-configurable` | PASS | Batch 01 report and `test_manual_mode_sends_null_turn_detection_and_response_create`, including append before commit and `response.create`. |
| `tools-search-mutually-exclusive` | PASS | Batch 01 and Batch 05 reports; constructor and registry tools reject `enable_search=True` before session update. |
| `speech-events-map-to-user-turn` | PASS | Batch 03 report and `test_speech_events_update_turn_and_close_image_window`. |
| `audio-delta-and-done-map-to-output` | PASS | Batch 03 report and `test_response_audio_delta_and_done_emit_output_boundary`. |
| `transcript-delta-and-done-map-to-final` | PASS | Batch 03 report and transcript delta/done tests. |
| `response-done-parses-usage` | PASS | Batch 03 report and `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final`. |
| `speech-started-interrupts-current-response` | PASS | Batch 04 report/review and `test_speech_started_interrupts_active_response_and_flushes_local_audio`; review fix covers post-response local audio risk. |
| `cancel-error-does-not-block-local-flush` | PASS | Batch 04 report/review and `test_cancel_error_does_not_block_local_flush_or_stale_isolation`. |
| `stale-delta-after-interrupt-blocked` | PASS | Batch 04 report/review and stale audio/transcript replay tests. |
| `interruption-latency-measured` | BLOCKED | Live Qwen interruption latency was not measured. Blocked by missing explicit API key, cost authorization, and service availability. |
| `image-not-sent-before-turn-audio` | PASS | Batch 02 report and `test_video_frame_not_sent_before_current_turn_audio`. |
| `image-window-closes-after-speech-stopped` | PASS | Batch 02 report and speech/commit/clear close-window tests. |
| `image-timing-error-suspends-sending` | PASS | Batch 02/06 evidence and `test_image_timing_error_suspends_until_new_audio_turn`. |
| `track-reconnect-waits-for-current-audio` | PASS | Batch 02 report and `test_track_reconnect_waits_for_current_turn_audio`. |
| `tool-schema-sent-in-session-update` | PASS | Batch 05 report/review and `test_registry_tool_schema_is_sent_in_session_update`. |
| `function-call-executes-and-returns-output` | PASS | Batch 05 report/review and `test_function_call_done_executes_registry_tool_and_requests_response`. |
| `tool-error-returns-explainable-output` | PASS | Batch 05 report/review and tool error replay tests. |
| `search-config-sent-and-usage-retained` | PASS | Batch 05 report/review and search config/usage assertions. |
| `qwen-error-keeps-structured-fields` | PASS | Batch 06 report and `test_qwen_error_keeps_structured_fields_and_impact_scope`. |
| `recoverable-connection-resets-state` | PASS | Batch 06 report and `test_recoverable_reconnect_resets_state_and_resends_session_update` for `1011`, `1012`, `1013`, `1014`. |
| `session-config-error-fails-session` | PASS | Batch 06 report and `test_session_config_error_fails_session_and_blocks_future_sends`. |
| `usage-parse-error-retains-raw` | PASS | Batch 06 report and `test_response_done_usage_parse_failure_retains_raw_payload`. |

## Test Commands

Batch 06 verification commands:

- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py -k 'qwen_error_keeps_structured_fields or session_config_error_fails_session or recoverable_reconnect_resets_state or usage_parse_failure_retains_raw_payload'`
  - Red result before implementation: `7 failed, 32 deselected`
  - Green result after implementation: `7 passed, 32 deselected`
- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `37 passed, 2 skipped`
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `3 files already formatted`

The pytest commands emit the known narrow-test coverage warnings: `Module tidesync was never imported`, `No data was collected`, and no coverage report. The Qwen live integration tests remain skipped.

## Live Verification

Live Qwen smoke tests were not run. No explicit API key, cost authorization, or service availability was provided for this batch. Therefore live smoke, live interruption latency, and live undocumented payload variants are recorded as blockers/unknowns rather than completed evidence.

## Deviations

- `interruption-latency-measured` is blocked because live verification was not authorized or available.
- No core `must` assertion is known to be failing after deterministic fake WebSocket and replay verification.

## Unknowns

- Exact live Qwen behavior for undocumented error payload variants remains unknown.
- Live function-call payload variants beyond the deterministic replay shapes remain unknown.
- Live reconnect timing and service-side session behavior after transient close codes remains unmeasured beyond fake client evidence.

## Rollback Impact

Rolling back the Batch 06 PR would remove structured Qwen error snapshots, failed-session send suppression, recoverable reconnect adapter reset, usage parse error projection, and this final conformance statement. Rolling back the full Qwen adapter contract series would return TideSync to upstream Vision Agents Qwen behavior without the controlled Qwen3.5 Omni realtime contract guarantees, deterministic fake replay evidence, or final conformance evidence.
