# Review Package: Batch 01 Session Config And Client Senders

Review role: independent spec reviewer

Do not fix code during this review. Produce findings only. Long findings must be written to:

`docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders-review.md`

## Review Object

Review the implementation produced by the builder for:

- Handoff: `docs/qwen35-omni-adapter-contract/handoffs/batch-01-session-config-and-client-senders.md`
- Expected branch: `feature/qwen35-session-config-contract`
- Expected builder report: `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`
- Expected PR body draft: `docs/qwen35-omni-adapter-contract/pr-bodies/batch-01-session-config-and-client-senders.md`

## Review Basis

Required contract sources:

- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/010-source-and-runtime-contract.adoc:1-32`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/020-session-config-contract.adoc:1-52`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/030-client-event-contract.adoc:1-55`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/020-runtime-source-assertions.adoc:1-61`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/030-session-config-assertions.adoc:1-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:1-55`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

Implementation files likely in scope:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- `src/tidesync/agent.py` if changed
- `tests/` if changed
- Batch report and PR body draft files

## Required Checks

Spec compliance:

1. Verify the implementation does not repeat baseline-only work and stays within batch 01 scope.
2. Verify `session.update.session` contains the required fields and sends `pcm` contract defaults.
3. Verify the input transcription default is not silently `gummy-realtime-v1` as the Qwen3.5 contract default.
4. Verify `server_vad`, `semantic_vad`, and Manual `turn_detection: null` are representable and tested.
5. Verify tools/search mutual exclusion is enforced before an illegal session update is sent.
6. Verify unsupported Qwen fields `tool_choice` and `parallel_tool_calls` are not sent.
7. Verify client senders exist and tests cover `input_audio_buffer.clear`, `conversation.item.create` for `function_call_output`, and `response.create`.
8. Verify fake/static tests do not contact the live Qwen service.
9. Verify the runtime import path test still passes or the report explains a real blocker.
10. Verify the builder report and PR body draft contain the required evidence fields.

Code quality risks:

1. Flag duplicate session config construction or raw dictionary drift.
2. Flag hidden contract state that cannot be asserted by tests.
3. Flag broad state-machine or event-mapping work that belongs to later batches.
4. Flag overbroad edits, unrelated refactors, or root dependency churn.
5. Flag comments that restate code instead of explaining contract reasons.

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
