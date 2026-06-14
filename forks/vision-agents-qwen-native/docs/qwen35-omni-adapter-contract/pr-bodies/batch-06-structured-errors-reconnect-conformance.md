## Summary

This PR implements Batch 06 of the Qwen3.5 Omni Realtime WebSocket adapter contract: structured Qwen error preservation, remaining error-state classification, failed-session send suppression, recoverable reconnect reset behavior, usage-parse error projection, and the final conformance statement for the 09 contract book.

## Scope

- Preserves Qwen `error` event fields in `_qwen_error_snapshot()`: `event_id`, `type`, `code`, `message`, `param`, raw error, state, impact scope, and recoverability.
- Adds session lifecycle projection through `_qwen_session_snapshot()`.
- Classifies session config, audio format, transcription model, image/input timing, cancel, tool schema, tool execution, tools/search conflict, usage parse, recoverable connection, terminal connection, and unknown Qwen errors.
- Fails/restricts the session after session configuration errors and blocks future audio, image, commit, clear, tool output, and `response.create` sends.
- Adds minimal reconnect callbacks to the existing Qwen client reconnect path so the adapter can reset stale local state for recoverable close codes `1011`, `1012`, `1013`, and `1014`.
- Preserves Batch 04 cancel-error behavior and Batch 05 tool-error behavior.
- Preserves raw usage retention and adds visible `usage_parse_error`.
- Adds the final conformance statement at `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`.

## Repository Rationale

`vision-agents-qwen-native` is the controlled TideSync fork carrying the Qwen realtime adapter used by the runtime path. The 09 contract book requires Qwen error handling, reconnect behavior, usage evidence, and final PR conformance evidence to be deterministic and reviewable. This PR keeps protocol mapping and state projection inside the Qwen adapter and uses only a narrow client callback hook around the pre-existing reconnect behavior.

## Contract Coverage

- `qwen-error-keeps-structured-fields`: covered by `test_qwen_error_keeps_structured_fields_and_impact_scope`.
- `recoverable-connection-resets-state`: covered by `test_recoverable_reconnect_resets_state_and_resends_session_update` for close codes `1011`, `1012`, `1013`, and `1014`.
- `session-config-error-fails-session`: covered by `test_session_config_error_fails_session_and_blocks_future_sends`.
- `usage-parse-error-retains-raw`: covered by `test_response_done_usage_parse_failure_retains_raw_payload`.

The final conformance statement summarizes assertion results across Batches 00 through 06 and points to the accepted batch reports and review reports.

## Verification

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `1 passed`
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `37 passed, 2 skipped`
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `3 files already formatted`

Pytest emits the existing narrow-test coverage warnings that `tidesync` was not imported and no coverage data was collected.

## Final Conformance Statement

- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`

## Live Verification / Blockers

Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability. Live interruption latency and undocumented payload variants remain unknown; deterministic fake WebSocket and replay tests are the Batch 06 evidence surface.

## Rollback Impact

Rolling back this PR would remove structured Qwen error snapshots, session failure send suppression, recoverable reconnect state reset, usage parse error projection, and the final conformance statement. The adapter would return to the Batch 05 baseline where generic Qwen errors were not fully test-readable and recoverable reconnects were not reflected in adapter state.
