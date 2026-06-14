# Handoff: Batch 05 Tools Search And Tool Errors

Role: persistent builder subagent
Model requirement: `gpt-5.5`, reasoning `high`, `fork_context=false`
Branch: `feature/qwen35-tools-search-tool-errors`

You are not alone in the codebase. Do not revert edits made by others. If you encounter unrelated changes, preserve them, work around them, and report them. If you are unsure whether a change is unrelated, ask the coordinator before proceeding.

## Mission

Implement the fifth post-baseline contract slice for the controlled Vision Agents Qwen adapter in TideSync:

1. Include Vision Agents `FunctionRegistry` tools in Qwen `session.update.session.tools`.
2. Handle Qwen `response.function_call_arguments.delta` as observation/accumulation state.
3. Handle Qwen `response.function_call_arguments.done` by parsing JSON arguments, invoking the Vision Agents function registry, sending `conversation.item.create(function_call_output)`, and sending `response.create`.
4. Convert unknown tools, invalid JSON arguments, and tool execution exceptions into an explainable tool failure output instead of leaving the tool call pending.
5. Preserve the existing search configuration, tools/search mutual exclusion, usage retention, and search usage retention behavior from earlier batches.
6. Add deterministic replay tests for function-call success and tool error paths.
7. Produce a batch report and PR body draft.
8. Commit only the files for this batch.

Do not implement Batch 06 full structured Qwen error taxonomy, reconnect state reset, session config error closure, live conformance closure, or new core event surfaces in this batch unless you first ask the coordinator and receive approval.

## Required Reading

Read these files and line ranges before editing:

1. Object and boundary:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/010-artifact-identity.adoc:14-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/040-system-boundary.adoc:20-25`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:48-52`

2. Current system facts:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/040-vision-agents-core-carriers.adoc:29-36`

3. Batch 05 target contract:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:49-64`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:64-73`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/070-tools-search-usage-contract.adoc:1-41`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:27-32`

4. Batch 05 assertions and evidence:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/070-tools-search-usage-assertions.adoc:1-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:34-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

5. Current accepted batch evidence:
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage-review.md`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error-review.md`

6. Current code:
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/llm/function_registry.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/llm/llm.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/llm/llm_types.py`
   - `tests/test_vision_agents_runtime_path.py`

## Current Baseline Facts

Batch 04 is merged to `main` at merge commit `a1ad59e`.

Important implementation facts at the Batch 05 starting point:

1. `Qwen3RealtimeClient` already has `send_function_call_output(call_id, output)` and `create_response()`.
2. `Qwen3Realtime` already converts constructor-supplied `tools` into Qwen function schema and rejects constructor tools with `enable_search=True`.
3. `Qwen3Realtime` does not yet automatically include tools registered through `self.function_registry`.
4. Core `LLM` owns `self.function_registry`, exposes `get_available_functions()`, and exposes `call_function(name, arguments)`.
5. Batch 03 already parses `response.done.usage`, retains raw usage, and preserves `plugins.search` in a test-visible projection.
6. Batch 04 already handles interruption and stale response isolation. Batch 05 must not regress those tests.

## Write Scope

You may edit:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-05-tools-search-tool-errors.md`

You may edit `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py` only if a deterministic test proves the existing `send_function_call_output()` or `create_response()` surface is insufficient.

Do not edit:

- The 09 contract book.
- TideSync outer `src/tidesync/agent.py`.
- Root dependency resolution.
- Batch 01 through Batch 04 reports, review reports, or PR bodies.
- Core runtime files unless you first ask the coordinator and receive approval. The current core registry and client event carriers are sufficient for Batch 05.

## Functional Requirements

Tool schema:

1. `session.update.session.tools` must include tools supplied through the constructor and tools registered through `self.function_registry`.
2. Registry `ToolSchema` objects must map to Qwen function schema with `type: "function"` and `function.name`, `function.description`, and `function.parameters`.
3. The adapter must continue to reject tools and search enabled together. This rejection must include constructor tools and registry tools.
4. The adapter must not send unsupported `tool_choice` or `parallel_tool_calls`.

Function-call event handling:

1. Handle `response.function_call_arguments.delta` and update a test-visible tool state such as `function_call_delta_seen`.
2. Handle `response.function_call_arguments.done` as the complete tool invocation source.
3. Extract tool name, `arguments`, and `call_id`. Accept common Qwen shapes if present, but do not invent a broad parser without tests.
4. Parse `arguments` as JSON when it is a string. If `arguments` is already a dict, use it directly. Invalid JSON must enter tool error state.
5. Invoke the Vision Agents function registry through `self.call_function(name, arguments)` or `self.function_registry.call_function(name, arguments)`.
6. Run tool execution without permanently blocking the WebSocket reader. Use the existing Realtime background tool-task helper or an equivalent bounded async task pattern already available in core.
7. On success, send `conversation.item.create(function_call_output)` with the original `call_id`, then send `response.create`.
8. On unknown tool, invalid arguments, or execution exception, send an explainable tool failure output with the original `call_id`, then send `response.create`.
9. Tool errors must be visible in adapter state or another deterministic test surface. A log line alone is not evidence.
10. Tool execution must not swallow interruption/stale-response protections from Batch 04.

Tool state projection:

1. Expose a deterministic state snapshot for tool/search/usage state, or extend the existing Qwen response snapshot if that is cleaner.
2. Cover at least these tool state responsibilities: `tools_registered`, `function_call_delta_seen`, `function_call_ready`, `tool_running`, `tool_succeeded`, `tool_failed`, `tool_output_sent`, and `tool_response_requested`.
3. Preserve existing usage and search snapshots from Batch 03.

Search and usage:

1. Preserve `enable_search` and `search_options.enable_source` config behavior.
2. Preserve tools/search mutual exclusion.
3. Preserve `response.done` usage parsing and raw usage retention.
4. Preserve `usage.plugins.search` retention.
5. Batch 05 may add tests that explicitly tie search config and search usage evidence together, but should not refactor usage projection without need.

Testing:

1. Add a registry-tool session config test proving a registered tool enters `session.update.session.tools`.
2. Add a function-call success replay test. It must assert registry invocation, function_call_output send event, response.create send event, and tool state progression.
3. Add at least one unknown-tool replay test and one invalid-JSON replay test, or one table-driven test covering both.
4. Add a tool execution exception test if the implementation shape makes it meaningfully different from unknown-tool and invalid-JSON.
5. Assert that tool error outputs are explainable and include the original call id.
6. Preserve existing search config and search usage tests.
7. Preserve all Batch 01 through Batch 04 tests.
8. Keep existing live integration tests skipped.

Design constraints:

1. Keep a single source of truth for tool call state and pending call ids.
2. Keep provider mapping in the Qwen adapter; do not move Qwen-specific function call JSON into core.
3. Keep function call result serialization deterministic in tests. If a tool returns a dict/list, encode it as stable JSON or document and test the chosen representation.
4. Comments should explain contract reasons that code alone cannot show, especially why tool failures still send function_call_output and response.create.
5. Do not expand into a full structured Qwen error taxonomy. Tool errors need deterministic state and explainable output; Batch 06 owns broader error closure.

## Commands To Run

At minimum, run:

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

If a command fails because of a pre-existing unrelated issue, record the exact command, failure summary, and why it is unrelated in the batch report.

## Report Requirements

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors.md` with:

- Branch name and commit SHA.
- Files changed.
- Contract IDs covered.
- Assertion results for:
  - `tool-schema-sent-in-session-update`
  - `function-call-executes-and-returns-output`
  - `tool-error-returns-explainable-output`
  - `search-config-sent-and-usage-retained`
- Tool state projection summary.
- Function call success/error replay summary.
- Test commands and output summary.
- Known unknowns or live verification blockers.
- Explicit non-goals left for future batches.

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-05-tools-search-tool-errors.md` with a PR-ready body containing:

- Summary.
- Scope.
- Repository rationale.
- Contract coverage.
- Verification.
- Live verification / blockers.
- Rollback impact.

Long explanations belong in these files, not in chat.

## Commit Requirements

Create the topic branch first:

```bash
git switch -c feature/qwen35-tools-search-tool-errors
```

Commit only this batch's files. Because this is a shared workbench, use path-specific staging/commit. New files must be tracked before commit.

Use a detailed commit message. Recommended subject:

```text
feat: execute Qwen function calls through registry
```

The body should mention the 09 contract book, registry tool schema injection, function call replay, tool failure output, search/usage preservation, event replay tests, and non-goals.

## Final Chat Response

Return only a short status:

- `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
- Branch name.
- Commit SHA if committed.
- Report file path.
- PR body draft path.
- Test commands run.
- Any question for the coordinator.

If you are unsure about scope, ask the coordinator before implementing.
