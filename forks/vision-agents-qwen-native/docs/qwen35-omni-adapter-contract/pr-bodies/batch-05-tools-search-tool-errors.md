## Summary

This PR implements Batch 05 of the Qwen3.5 Omni Realtime WebSocket adapter contract: registry tool schema injection, Qwen function-call execution through Vision Agents `FunctionRegistry`, explainable tool failure output, and preservation of existing search/usage behavior.

## Scope

- Includes constructor tools and registry tools in `session.update.session.tools`.
- Maps registry `ToolSchema` objects to Qwen function schemas.
- Rejects tools and `enable_search=True` together for both constructor tools and registry tools.
- Handles `response.function_call_arguments.delta` as observable tool state.
- Handles `response.function_call_arguments.done` by parsing arguments, executing the registry tool, sending `conversation.item.create(function_call_output)`, and sending `response.create`.
- Converts unknown tools, invalid JSON, and tool execution exceptions into explainable tool failure output with the original `call_id`.
- Adds deterministic fake WebSocket/event replay tests for success and error paths.
- Preserves search config, search usage retention, usage parsing, and Batch 01 through Batch 04 behavior.

## Repository Rationale

`vision-agents-qwen-native` is the controlled TideSync fork carrying the Qwen realtime adapter used by the runtime path. The 09 contract book requires Qwen tool calls, search configuration, and usage accounting to be visible in adapter behavior and repeatable tests. This PR keeps Qwen protocol mapping inside the Qwen adapter and uses the existing Vision Agents `FunctionRegistry`; no core runtime, root dependency, or TideSync outer runtime changes are required.

## Contract Coverage

- `tool-schema-sent-in-session-update`: covered by `test_registry_tool_schema_is_sent_in_session_update`.
- `function-call-executes-and-returns-output`: covered by `test_function_call_done_executes_registry_tool_and_requests_response`.
- `tool-error-returns-explainable-output`: covered by `test_function_call_errors_return_explainable_tool_output` and `test_function_call_execution_exception_returns_explainable_tool_output`.
- `search-config-sent-and-usage-retained`: covered by existing search config and search usage assertions in `test_tools_and_search_config_payloads_do_not_include_unsupported_fields` and `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final`.

The implementation exposes Batch 05 tool state through `_qwen_tool_snapshot()` for deterministic contract tests. It does not add new public core carriers.

## Verification

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `1 passed`
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `31 passed, 2 skipped`
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `2 files already formatted`

The pytest commands emit the existing narrow-test coverage warnings that `tidesync` was not imported and no coverage data was collected.

## Live Verification / Blockers

Live Qwen service verification was not run. It remains blocked by missing explicit API key, cost authorization, and service availability for this batch. Fake WebSocket and event replay tests are the required Batch 05 evidence surface.

Broader undocumented function-call payload variants remain live compatibility unknowns. Batch 06 still owns full structured Qwen error taxonomy, reconnect reset, session config error closure, and final conformance closure.

## Rollback Impact

Rolling back this PR would remove registry tool schema injection and Qwen function-call execution. The adapter would again leave Qwen function calls pending instead of returning tool output and requesting a follow-up response, and registry tools would not be represented in session configuration. Existing audio, interruption, search config, and usage behavior would return to the Batch 04 baseline.
