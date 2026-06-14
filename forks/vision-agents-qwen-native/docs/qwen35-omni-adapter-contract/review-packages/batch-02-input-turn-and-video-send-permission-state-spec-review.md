# Review Package: Batch 02 Input Turn And Video Send-Permission State

Review role: independent spec reviewer

Do not fix code during this review. Produce findings only. Long findings must be written to:

`forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state-review.md`

## Review Object

Review the implementation produced by the builder for:

- Handoff: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/handoffs/batch-02-input-turn-and-video-send-permission-state.md`
- Expected branch: `feature/qwen35-input-turn-video-state`
- Expected builder report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md`
- Expected PR body draft: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-02-input-turn-and-video-send-permission-state.md`

## Review Basis

Required contract sources:

- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/020-qwen-official-contract.adoc:20-25`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/030-vision-agents-qwen-adapter.adoc:31-36`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/050-gap-map.adoc:20-25`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/030-client-event-contract.adoc:29-41`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:13-23`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:22-35`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:20-25`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/040-event-mapping-assertions.adoc:6-23`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/060-video-turn-assertions.adoc:1-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

Implementation files likely in scope:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- Batch report and PR body draft files

## Required Checks

Spec compliance:

1. Verify the implementation stays within Batch 02 and does not implement broad interruption, response lifecycle, usage, tools, search, reconnect, or structured error work.
2. Verify `_audio_emitted_once` is no longer the sole video permission source.
3. Verify current-turn audio append opens image sending only for the current turn.
4. Verify `input_audio_buffer.speech_stopped` closes current-turn image sending and records or projects the relevant state.
5. Verify Manual commit closes current-turn image sending.
6. Verify Manual clear closes or resets current-turn image sending.
7. Verify track removal and reconnect force the next track to wait for current-turn audio.
8. Verify a Qwen image timing error suspends image sending until a new valid audio turn reopens permission.
9. Verify fake tests do not contact the live Qwen service.
10. Verify the runtime import path test still passes or the report explains a real blocker.
11. Verify the builder report and PR body draft exist at the fork work-area paths and contain required evidence fields.

Code quality risks:

1. Flag duplicate or conflicting state sources for input-turn and video permission.
2. Flag hidden state with no test-visible projection.
3. Flag broad event-loop or interruption refactors that belong to later batches.
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
