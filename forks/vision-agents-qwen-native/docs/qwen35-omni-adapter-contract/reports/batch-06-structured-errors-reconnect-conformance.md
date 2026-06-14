# Batch 06 Report: Structured Errors Reconnect And Conformance Closure

Branch: `feature/qwen35-error-reconnect-conformance`

Implementation commit SHA: `3b26850`

## Files Changed

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-06-structured-errors-reconnect-conformance.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-06-structured-errors-reconnect-conformance.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`

No unrelated working-tree changes were observed during this batch.

## Contract IDs Covered

- `qwen-error-keeps-structured-fields`
- `recoverable-connection-resets-state`
- `session-config-error-fails-session`
- `usage-parse-error-retains-raw`
- `test-evidence-contract`
- `pr-conformance-statement`
- `upstream-provenance`

## Implementation Summary

Batch 06 adds adapter-local structured error and session state projections for the Qwen realtime adapter. Qwen `error` events now preserve `event_id`, `error.type`, `error.code`, `error.message`, `error.param`, the raw error object, an explicit error state, impact scope, and recoverability in `_qwen_error_snapshot()`.

The adapter classifies Qwen errors into the remaining contract states: input timing, cancel, session config, audio format, transcription model, tool schema, tool execution, search/tools conflict, usage parse, and unknown Qwen error. Session configuration, audio-format, and transcription-model errors fail the adapter session and block future audio, image, commit, clear, tool-output, and `response.create` sends through `_can_send_realtime_event()`.

The client now accepts minimal reconnect callbacks around its existing recoverable reconnect path. The adapter uses those callbacks to enter reconnecting state, record `connection_error_recoverable`, cancel pending tool tasks, clear stale response/current item/local audio/interruption state, reset input-turn video permission to `track_reconnected_waiting_audio`, and mark the session active again after the client reconnect sends `session.update`.

Usage parse failures keep the existing raw usage retention and now also project `usage_parse_error` in the response/error snapshots.

## Assertion Results

| Assertion | Result | Evidence |
|---|---|---|
| `qwen-error-keeps-structured-fields` | PASS | `test_qwen_error_keeps_structured_fields_and_impact_scope` replays a Qwen `error` with `event_id`, type, code, message, and param. It asserts `_qwen_error_snapshot()` preserves all fields, raw error, `session_config_error`, `impact_scope == ["session"]`, and `recoverable is False`. |
| `recoverable-connection-resets-state` | PASS | `test_recoverable_reconnect_resets_state_and_resends_session_update` covers close codes `1011`, `1012`, `1013`, and `1014`. Each replay proves a second `session.update`, session reactivation, response/current item reset, local audio reset, video permission reset, interruption ids cleared, pending tool state cleared, and post-reconnect video send blocked until new current-turn audio. |
| `session-config-error-fails-session` | PASS | `test_session_config_error_fails_session_and_blocks_future_sends` replays an invalid session config error, asserts `_qwen_session_snapshot()["state"] == "failed"`, then attempts audio, commit/response, clear, and image sends. The fake client records no events after the original `session.update`. |
| `usage-parse-error-retains-raw` | PASS | `test_response_done_usage_parse_failure_retains_raw_payload` asserts `usage_parse_failed`, raw invalid usage retention, parse error text, response error `usage_parse_error`, and `_qwen_error_snapshot()["impact_scope"] == ["usage"]`. |

## Error-State And Impact-Scope Summary

- `input_timing_error`: input turn and video permission impact; recoverable by new turn audio.
- `cancel_error`: response and local audio output impact; recoverable/local flush must continue.
- `session_config_error`: session impact; non-recoverable for the current session and blocks future sends.
- `audio_format_error`: session impact; non-recoverable for the current session.
- `transcription_model_error`: session impact; non-recoverable for the current session.
- `tool_schema_error`: session and tool impact; non-recoverable for session configuration.
- `tool_execution_error`: tool and response impact; recoverable by sending explainable tool output and requesting a response.
- `search_tools_conflict_error`: session and tool impact; rejected before session update.
- `usage_parse_error`: usage impact; raw usage retained.
- `connection_error_recoverable`: session, input turn, video permission, response, local audio output, and tool impact; recoverable reconnect resets stale local state.
- `connection_error_terminal`: enum state reserved for terminal connection classification; no terminal live replay was introduced in this batch.
- `unknown_qwen_error`: session impact by default; structured fields remain preserved.

## Reconnect Reset Summary

Recoverable reconnect start resets only reconnect-scoped adapter state: old response id, current item id, responding flag, input turn image permission, response projection, interruption ids, and pending tool tasks. Registered tool count is recomputed from the local registry after reset. The fake reconnect test proves the client sends `session.update` again and the adapter does not continue using stale video permission or old response/tool state.

## Final Conformance Statement

Final conformance statement path:

- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`

The statement records implementation scope, upstream provenance from `UPSTREAM.adoc`, runtime path evidence, assertion results across Batches 00 through 06, commands run, live verification blockers, deviations, unknowns, and rollback impact.

## Test Commands And Output Summary

- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py -k 'qwen_error_keeps_structured_fields or session_config_error_fails_session or recoverable_reconnect_resets_state or usage_parse_failure_retains_raw_payload'`
  - Red result before implementation: `7 failed, 32 deselected`.
  - Failure summary: missing `_qwen_error_snapshot()`, missing reconnect callbacks, session errors did not block sends, and usage parse failure did not set `usage_parse_error`.
  - Green result after implementation: `7 passed, 32 deselected`.
- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Warning: known narrow-test coverage warnings: `Module tidesync was never imported`, `No data was collected`, and no coverage report.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `37 passed, 2 skipped`.
  - Warning: same known coverage no-data warnings; skipped tests are existing live integration tests.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `3 files already formatted`.

## Known Unknowns, Live Blockers, And Deviations

- Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability.
- Live interruption latency remains unmeasured; this is a `PASS_WITH_NOTES` / live blocker rather than fake replay evidence.
- Broader undocumented Qwen error payload variants remain live compatibility unknowns. The adapter preserves structured fields for any dict-shaped Qwen error and classifies the tested contract shapes.
- No core `must` assertion is known to be failing after Batch 06 deterministic replay.

## Explicit Non-Goals Left Outside Batch 06

- Editing the 09 contract book.
- TideSync outer runtime changes.
- New core Vision Agents event carrier changes.
- Live service smoke, live interruption latency, or live undocumented payload discovery without credentials and cost authorization.
- New product behavior outside the controlled Qwen adapter contract.
