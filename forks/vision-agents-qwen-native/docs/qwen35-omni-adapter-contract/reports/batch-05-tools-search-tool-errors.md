# Batch 05 Report: Tools Search And Tool Errors

Branch: `feature/qwen35-tools-search-tool-errors`

Implementation commit SHA: `9e97bcf`

## Files Changed

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-05-tools-search-tool-errors.md`

No unrelated working-tree changes were observed during this batch.

## Contract IDs Covered

- `function-call-events-contract`
- `tool-search-usage-state`
- `tool-schema-contract`
- `tool-call-contract`
- `search-contract`
- `usage-contract`
- `metrics-projection-contract`
- `tool-error-contract`
- `tool-schema-sent-in-session-update`
- `function-call-executes-and-returns-output`
- `tool-error-returns-explainable-output`
- `search-config-sent-and-usage-retained`
- `event-replay-tests`
- `fake-websocket-tests`
- `state-machine-tests`

## Implementation Summary

Batch 05 extends the Qwen realtime adapter with adapter-local tool schema and function-call handling. The adapter now combines constructor-supplied tools with `self.function_registry.get_tool_schemas()` before building `session.update.session.tools`. Registry `ToolSchema` values are mapped to the Qwen function schema shape with `type: "function"` and `function.name`, `function.description`, and `function.parameters`.

The tools/search mutual exclusion check now uses the merged tool set, so both constructor tools and registry tools reject `enable_search=True` before any session is created. The session config still does not send unsupported `tool_choice` or `parallel_tool_calls`.

The adapter now handles `response.function_call_arguments.delta` as observation state and `response.function_call_arguments.done` as the complete invocation source. Done events extract `call_id`, tool name, and arguments, parse string arguments as JSON, call the Vision Agents function registry through `self.call_function(name, arguments)`, send `conversation.item.create(function_call_output)` with the original `call_id`, and then send `response.create`.

Tool execution is scheduled in adapter-owned async tasks so the WebSocket reader does not permanently block on function execution. Completed or pending `call_id` values are deduplicated so replayed done events cannot double-run a tool or double-send output. Tests use `_wait_for_tool_tasks()` to make this asynchronous path deterministic.

Tool failure paths for unknown tools, invalid JSON, and execution exceptions all send explainable JSON tool outputs and then request a response. This keeps the Qwen tool call from remaining permanently pending while staying inside Batch 05 scope.

## Assertion Results

| Assertion | Result | Evidence |
|---|---|---|
| `tool-schema-sent-in-session-update` | PASS | `test_registry_tool_schema_is_sent_in_session_update` registers `lookup_order` through `function_registry`, connects the adapter, and asserts `session.update.session.tools` contains the Qwen function schema. It also asserts no `tool_choice` or `parallel_tool_calls` fields are sent and that `_qwen_tool_snapshot()["tools_registered"] == 1`. |
| `function-call-executes-and-returns-output` | PASS | `test_function_call_done_executes_registry_tool_and_requests_response` replays `response.function_call_arguments.delta` and `response.function_call_arguments.done`; asserts the registry tool receives `{"order_id": "order-123"}`, fake client sends `conversation.item.create` and `response.create`, the original `call_id` is preserved, output JSON is stable, and tool state reaches ready, succeeded, output sent, and response requested. |
| `tool-error-returns-explainable-output` | PASS | `test_function_call_errors_return_explainable_tool_output` covers unknown tool and invalid JSON. `test_function_call_execution_exception_returns_explainable_tool_output` covers a registry execution exception. All assert explainable JSON output with the original `call_id`, `conversation.item.create`, `response.create`, and visible `tool_failed` state. |
| `search-config-sent-and-usage-retained` | PASS | Existing tests remain passing: `test_tools_and_search_config_payloads_do_not_include_unsupported_fields` asserts `enable_search` and `search_options.enable_source`; `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final` asserts `usage.plugins.search` is retained in `_qwen_usage_snapshot()`. |

Additional coverage:

- `test_registry_tools_and_search_are_rejected_before_session_update` proves registry tools participate in the tools/search mutual exclusion rule before fake client construction.
- Existing Batch 01 through Batch 04 replay tests are preserved in the full Qwen test run.

## Tool State Projection Summary

Batch 05 adds `QwenToolCallState` and exposes it through `_qwen_tool_snapshot()` for deterministic tests. The snapshot covers the required tool state responsibilities:

- `tools_registered`
- `function_call_delta_seen`
- `function_call_ready`
- `tool_running`
- `tool_succeeded`
- `tool_failed`
- `tool_output_sent`
- `tool_response_requested`

It also records the latest `call_id`, tool `name`, parsed `arguments`, serialized `output`, and explainable `error` text. This is an adapter-private test projection, not a new core event surface.

## Function Call Success And Error Replay Summary

Success replay:

1. Registry tool `lookup_order` is registered with an explicit JSON parameter schema.
2. Fake Qwen sends `response.function_call_arguments.delta` with `call_id="call_1"`.
3. Fake Qwen sends `response.function_call_arguments.done` with `name="lookup_order"` and JSON string arguments.
4. Adapter parses arguments, runs `lookup_order`, serializes the dict result as stable JSON, sends `conversation.item.create(function_call_output)`, and sends `response.create`.

Error replay:

1. Unknown tool requests generate `{"ok": false, "error": "Unknown tool '<name>'"}`.
2. Invalid JSON arguments generate an explainable `Invalid tool arguments JSON` output.
3. Tool execution exceptions generate `{"ok": false, "error": "Tool '<name>' failed: <message>"}`.
4. All error paths preserve the original `call_id`, send function-call output, send `response.create`, and mark `tool_failed`.

## Search And Usage Preservation

The Batch 03 usage parser remains unchanged. It still retains total/input/output token fields, token detail dictionaries, raw usage, and `usage.plugins.search` when present. The search session config still sends `enable_search=True` and `search_options` when configured, and search remains mutually exclusive with tools.

## Test Commands And Output Summary

- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py::test_registry_tool_schema_is_sent_in_session_update forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py::test_registry_tools_and_search_are_rejected_before_session_update forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py::test_function_call_done_executes_registry_tool_and_requests_response forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py::test_function_call_errors_return_explainable_tool_output forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py::test_function_call_execution_exception_returns_explainable_tool_output`
  - Red result before implementation: `6 failed`.
  - Failure summary: registry tools were absent from session config, registry tools did not trigger tools/search rejection, and the adapter had no `_wait_for_tool_tasks()` or function-call handling surface.
  - Green result after implementation: `6 passed`.
- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Warning: known narrow-test coverage warnings: `Module tidesync was never imported`, `No data was collected`, and no coverage report.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `31 passed, 2 skipped`.
  - Warning: same known coverage no-data warnings; skipped tests are existing live integration tests.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `2 files already formatted`.

## Known Unknowns And Live Verification Blockers

- Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability for this batch.
- The implementation accepts tested common Qwen event shapes for `call_id`, `name`, and `arguments`; broader undocumented payload variants remain live compatibility unknowns.
- Tool execution timeout policy is not changed in this batch. The implementation uses adapter-owned async tasks and does not introduce a new contract-level timeout surface.

## Explicit Non-Goals Left For Future Batches

- Batch 06: full structured Qwen error taxonomy, reconnect state reset, session config error closure, and final conformance closure.
- New Vision Agents core event surfaces or public metrics surfaces for provider tool state.
- Live service validation for exact Qwen function-call payload variants.
- Text-only output support.
