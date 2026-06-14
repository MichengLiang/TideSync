# Review Package: Batch 05 Tools Search And Tool Errors

Review role: independent spec reviewer

Do not fix code during this review. Produce findings only. Long findings must be written to:

`forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors-review.md`

## Review Object

Review the implementation produced by the builder for:

- Handoff: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/handoffs/batch-05-tools-search-tool-errors.md`
- Expected branch: `feature/qwen35-tools-search-tool-errors`
- Expected builder report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors.md`
- Expected PR body draft: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-05-tools-search-tool-errors.md`

## Review Basis

Required contract sources:

- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:48-52`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/040-vision-agents-core-carriers.adoc:29-36`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:49-64`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:64-73`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/070-tools-search-usage-contract.adoc:1-41`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:27-32`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/070-tools-search-usage-assertions.adoc:1-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:34-40`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

Implementation files likely in scope:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py` only if the builder changed it
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- Batch report and PR body draft files

## Required Checks

Spec compliance:

1. Verify registered Vision Agents `FunctionRegistry` tools appear in Qwen `session.update.session.tools`.
2. Verify constructor-supplied tools still appear in Qwen function schema.
3. Verify tools/search mutual exclusion includes registry tools and constructor tools.
4. Verify unsupported `tool_choice` and `parallel_tool_calls` are not sent.
5. Verify `response.function_call_arguments.delta` updates observable function-call state without pretending to execute incomplete arguments.
6. Verify `response.function_call_arguments.done` extracts name, arguments, and call_id from the tested Qwen payload shape.
7. Verify JSON argument parsing is deterministic and invalid JSON enters tool error state.
8. Verify successful tool execution calls the Vision Agents registry, sends `conversation.item.create(function_call_output)`, preserves the original `call_id`, and sends `response.create`.
9. Verify unknown tools and tool execution exceptions produce explainable failure output and send `response.create`.
10. Verify the WebSocket reader is not permanently blocked by tool execution. Background task behavior must be awaited or otherwise made deterministic in tests.
11. Verify tool state projection covers registered, delta seen, ready, running, succeeded, failed, output sent, and response requested responsibilities.
12. Verify Batch 03 usage/search usage retention remains intact.
13. Verify Batch 04 interruption and stale response tests still pass.
14. Verify implementation stays within Batch 05 and does not implement Batch 06 full structured errors/reconnect closure.

Evidence checks:

1. Verify event replay tests cover function-call success.
2. Verify event replay tests cover unknown tool and invalid JSON. If execution exception is implemented, verify it is covered too.
3. Verify search config and search usage evidence remains present.
4. Verify tests do not contact the live Qwen service.
5. Verify the runtime import path test still passes or the report explains a real blocker.
6. Verify the builder report and PR body draft exist at the fork work-area paths and contain required evidence fields.

Code quality risks:

1. Flag duplicate or conflicting tool state sources.
2. Flag function-call execution that can leave tool calls permanently pending.
3. Flag result serialization that is nondeterministic or loses explainability.
4. Flag private logs used as the only tool-error evidence.
5. Flag broad core refactors, event-loop rewrites, or dependency churn.
6. Flag comments that restate code instead of explaining contract reasons.

## Output Format

The review report must contain:

- Review verdict: `APPROVED`, `APPROVED_WITH_NOTES`, or `CHANGES_REQUIRED`.
- Reviewed commit SHA.
- Contract coverage table.
- Findings ordered by severity with file and line references.
- Test evidence reviewed.
- Missing evidence, if any.
- Recommendation for coordinator promotion decision.

The chat response should be short and point to the review report path.
