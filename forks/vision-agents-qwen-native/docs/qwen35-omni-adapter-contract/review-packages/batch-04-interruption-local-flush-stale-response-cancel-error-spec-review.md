# Review Package: Batch 04 Interruption Local Flush Stale Response And Cancel Error

Review role: independent spec reviewer

Do not fix code during this review. Produce findings only. Long findings must be written to:

`forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error-review.md`

## Review Object

Review the implementation produced by the builder for:

- Handoff: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/handoffs/batch-04-interruption-local-flush-stale-response-cancel-error.md`
- Expected branch: `feature/qwen35-interruption-state`
- Expected builder report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error.md`
- Expected PR body draft: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-04-interruption-local-flush-stale-response-cancel-error.md`

## Review Basis

Required contract sources:

- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/040-vision-agents-core-carriers.adoc:6-27`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/050-gap-map.adoc:33-38`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:13-22`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:33-47`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:65-70`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:36-63`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:75-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/060-interruption-contract.adoc:1-44`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:6-18`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/050-interruption-assertions.adoc:1-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:37-45`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

Implementation files likely in scope:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- Batch report and PR body draft files

## Required Checks

Spec compliance:

1. Verify `input_audio_buffer.speech_started` always emits `RealtimeUserSpeechStarted`.
2. Verify interruption entry does not depend only on `_is_responding`; it must consider response state, local audio output state, unfinished transcript state, or equivalent state that covers local playable output and stale response risk.
3. Verify interruption emits `RealtimeAudioOutputDone(interrupted=True)` or the available equivalent public flush carrier.
4. Verify interruption emits `RealtimeAgentSpeechEnded(interrupted=True)` or the available equivalent agent turn boundary.
5. Verify `response.cancel` is sent when a cancellable current response exists.
6. Verify local flush and stale isolation do not depend on remote cancel success.
7. Verify Qwen cancel errors preserve structured fields needed by tests and do not restore normal response streaming/completed state.
8. Verify interrupted response ids are recorded as cancelled/interrupted.
9. Verify late `response.audio.delta`, `response.audio_transcript.delta`, `response.text.delta`, and completion events for interrupted response ids cannot become current playable output or final assistant transcript.
10. Verify a later non-stale response id can still produce output.
11. Verify `response.done` is still not used as an empty assistant transcript final substitute.
12. Verify implementation stays within Batch 04 and does not implement Batch 05 tools/search/tool errors or Batch 06 full structured errors/reconnect closure.

Evidence checks:

1. Verify event replay tests cover barge-in local flush.
2. Verify event replay tests cover cancel error after local interruption.
3. Verify event replay tests cover delayed stale delta blocking.
4. Verify tests do not contact the live Qwen service.
5. Verify the runtime import path test still passes or the report explains a real blocker.
6. Verify the builder report and PR body draft exist at the fork work-area paths and contain required evidence fields.

Code quality risks:

1. Flag duplicate or conflicting response id status sources.
2. Flag private logs used as the only stale-isolation or cancel-error evidence.
3. Flag broad core refactors, event-loop rewrites, or dependency churn.
4. Flag state names that do not map to the contract state responsibilities.
5. Flag comments that restate code instead of explaining the contract reason for stale delta defense.

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
