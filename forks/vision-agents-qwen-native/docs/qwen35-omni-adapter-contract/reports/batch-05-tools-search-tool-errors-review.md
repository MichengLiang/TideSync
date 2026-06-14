# Batch 05 Review: Tools Search And Tool Errors

Review verdict: `APPROVED_WITH_NOTES`

Reviewed commit SHA: `c994f473bfc6021afad39f1d0b6cf26b56f1f851`

Implementation commit reviewed: `9e97bcf83d8e3ed16c428dc73a72788f734d2ddd`

Branch reviewed: `feature/qwen35-tools-search-tool-errors`

## Contract Coverage Table

| Review check | Result | Evidence |
|---|---|---|
| Registry tools appear in `session.update.session.tools` | PASS | `_collect_tools()` merges constructor tools and `get_available_functions()` in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:438-464`; `_build_session_config()` emits the merged tools in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:455-456`. `test_registry_tool_schema_is_sent_in_session_update` asserts the Qwen function schema and registered count in `plugins/qwen/tests/test_qwen_realtime.py:259-297`. |
| Constructor-supplied tools still appear in Qwen schema | PASS | `_collect_tools()` preserves `self._tools` before registry tools in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:463-464`. Existing constructor-tool session assertions remain in `plugins/qwen/tests/test_qwen_realtime.py:220-256`. |
| Tools/search mutual exclusion includes registry and constructor tools | PASS | `_build_session_config()` rejects any merged tool list with `enable_search=True` before client construction in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:438-442`. Constructor-tool rejection remains covered by `test_tools_and_search_are_rejected_before_session_update`; registry-tool rejection is covered in `plugins/qwen/tests/test_qwen_realtime.py:300-313`. |
| Unsupported `tool_choice` and `parallel_tool_calls` are not sent | PASS | `_build_session_config()` does not add either field in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:444-461`; constructor and registry tests assert absence in `plugins/qwen/tests/test_qwen_realtime.py:254-256` and `:295-296`. |
| `response.function_call_arguments.delta` updates observable state without execution | PASS | Delta events call `_handle_function_call_arguments_delta()` only, which records delta state in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:719-720` and `:832-836`. The success replay asserts `function_call_delta_seen=True` after processing in `plugins/qwen/tests/test_qwen_realtime.py:374-388`. |
| `response.function_call_arguments.done` extracts name, arguments, and `call_id` from tested Qwen shapes | PASS | Done events schedule `_run_function_call()` in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:838-844`; helper extraction covers top-level, item, function, and item.function shapes in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:1013-1054`. Tests cover the top-level payload shape in `plugins/qwen/tests/test_qwen_realtime.py:341-354`, `:397-412`, and `:467-473`. |
| JSON argument parsing is deterministic and invalid JSON enters tool error state | PASS | `_parse_tool_arguments()` accepts dicts and JSON object strings, rejects non-object decoded values, and raises on invalid JSON in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:1057-1067`; invalid JSON replay asserts explainable output and `tool_failed` in `plugins/qwen/tests/test_qwen_realtime.py:391-450`. |
| Successful tool execution calls registry, sends function output, preserves `call_id`, and sends `response.create` | PASS | `_run_function_call()` checks registry, calls `self.call_function(name, arguments)`, serializes output, and delegates to `_send_tool_output_and_request_response()` in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:846-876`. `_send_tool_output_and_request_response()` sends `conversation.item.create(function_call_output)` then `response.create` in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:886-892`. Success replay asserts registry invocation, `call_id`, stable output, and send sequence in `plugins/qwen/tests/test_qwen_realtime.py:316-388`. |
| Unknown tools and tool execution exceptions produce explainable output and send `response.create` | PASS | Unknown tools and execution exceptions call `_send_tool_failure()` in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:860-884`; tests cover unknown tool, invalid JSON, and execution exception in `plugins/qwen/tests/test_qwen_realtime.py:391-491`. |
| WebSocket reader is not permanently blocked by tool execution | PASS | Done handling schedules `asyncio.create_task()` and stores the task instead of awaiting tool execution in the reader loop in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:838-844`; tests make the background path deterministic through `_wait_for_tool_tasks()` in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:647-650` and test calls at `plugins/qwen/tests/test_qwen_realtime.py:358-359`, `:433-434`, and `:476-477`. |
| Tool state projection covers Batch 05 responsibilities | PASS with note | `QwenToolCallState` exposes `tools_registered`, delta, ready, running, succeeded, failed, output sent, response requested, call id, name, arguments, output, and error through `_qwen_tool_snapshot()` in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:223-306` and `:525-526`. Note: the snapshot is latest-call oriented, not a per-call history; this is enough for current deterministic replay tests but should be revisited if concurrent/multiple tool calls become in-scope. |
| Batch 03 usage/search usage retention remains intact | PASS | Usage parsing and search usage retention remain in `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:900-918`; search config and search usage tests pass in the full suite, including `plugins/qwen/tests/test_qwen_realtime.py:220-256` and `:797-835`. |
| Batch 04 interruption and stale response tests still pass | PASS | The full Qwen suite includes the Batch 04 tests, including `test_speech_started_interrupts_active_response_and_flushes_local_audio`, `test_cancel_error_does_not_block_local_flush_or_stale_isolation`, `test_stale_audio_and_transcript_deltas_after_interrupt_are_blocked`, and `test_speech_started_interrupts_after_response_done_when_local_audio_remains_risky`; all passed in the fresh run. |
| Scope avoids Batch 06 drift | PASS | Implementation commit `9e97bcf` changes only `qwen_realtime.py` and `test_qwen_realtime.py`; final commit `c994f47` adds the Batch 05 report and PR body. No core runtime changes, client changes, reconnect closure, full structured Qwen error taxonomy, root dependency churn, or TideSync outer runtime edits were introduced. |

## Findings

No blocking findings.

### Note: Tool state projection is latest-call oriented

`QwenToolCallState` stores one current `call_id`, name, arguments, output, and error, plus a dedupe set for pending or finished call ids. This satisfies the Batch 05 replay evidence and state-responsibility checks for a single function call path, but it is not a full per-call history if Qwen later emits multiple function calls in one response. The handoff did not require parallel tool-call support, and the adapter deliberately does not send `parallel_tool_calls`, so this is a non-blocking note.

### Note: Broader live Qwen payload variants remain unverified

The implementation includes helper extraction for common top-level and nested Qwen payload shapes, but deterministic tests cover the top-level shape used in the replay package. The builder report correctly lists broader undocumented function-call payload variants as a live compatibility unknown. This is not a Batch 05 blocker because the package says to accept common Qwen shapes if present without inventing broad parsers without tests.

## Test Evidence Reviewed

Fresh commands run from `/home/t103o/workbench/micheng-ts/projects/TideSync`:

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
```

Result: `1 passed`. The command emitted the known narrow-test coverage warnings: `Module tidesync was never imported`, `No data was collected`, and no coverage report.

```bash
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
```

Result: `31 passed, 2 skipped`. The skipped tests are the existing live integration tests. The same known coverage warnings appeared.

```bash
uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

Result: `All checks passed!`

```bash
uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

Result: `2 files already formatted`.

The tests use `FakeQwenClient` and replayed server events; no live Qwen service contact occurs in the Batch 05 evidence path. The live integration tests remain skipped.

## Missing Evidence

- Live Qwen service verification was not run; the builder report records missing explicit API key, cost authorization, and service availability.
- Broader undocumented function-call payload variants are not live-verified.
- Batch 06 items remain intentionally out of scope: full structured error taxonomy, reconnect state reset, session config error closure, final conformance closure, and text-only output support.

## Builder Report And PR Body

The builder report exists at:

`forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors.md`

The PR body draft exists at:

`forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-05-tools-search-tool-errors.md`

Both are at fork work-area paths and contain the required Batch 05 evidence fields, verification summaries, live blockers, rollback impact, and explicit Batch 06 non-goals.

## Recommendation For Coordinator Promotion Decision

Batch 05 may be promoted. The required Batch 05 tool schema, function-call success/error, search/usage preservation, and earlier-batch regression checks are covered by deterministic tests, and the required local verification commands pass at reviewed HEAD `c994f473bfc6021afad39f1d0b6cf26b56f1f851`.
