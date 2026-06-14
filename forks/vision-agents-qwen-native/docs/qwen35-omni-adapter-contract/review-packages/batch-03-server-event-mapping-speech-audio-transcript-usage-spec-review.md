# Review Package: Batch 03 Server Event Mapping For Audio Transcript And Usage

Review role: independent spec reviewer

Do not fix code during this review. Produce findings only. Long findings must be written to:

`forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage-review.md`

## Review Object

Review the implementation produced by the builder for:

- Handoff: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/handoffs/batch-03-server-event-mapping-speech-audio-transcript-usage.md`
- Expected branch: `feature/qwen35-server-event-mapping`
- Expected builder report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage.md`
- Expected PR body draft: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-03-server-event-mapping-speech-audio-transcript-usage.md`

## Review Basis

Required contract sources:

- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/020-qwen-official-contract.adoc:27-39`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/030-vision-agents-qwen-adapter.adoc:38-45`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/040-vision-agents-core-carriers.adoc:6-20`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/050-gap-map.adoc:27-32`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:24-64`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:36-73`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/070-tools-search-usage-contract.adoc:29-41`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/040-event-mapping-assertions.adoc:25-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:22-36`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

Implementation files likely in scope:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- Batch report and PR body draft files

## Required Checks

Spec compliance:

1. Verify the implementation stays within Batch 03 and does not implement Batch 04 interruption/stale-response behavior, Batch 05 tool execution, or broad structured error/reconnect work.
2. Verify `response.audio.delta` still emits audio output and `response.audio.done` emits `RealtimeAudioOutputDone(interrupted=False)` or the correct available equivalent.
3. Verify `response.audio_transcript.delta` emits assistant transcript delta and `response.audio_transcript.done` emits assistant transcript final with server-provided or accumulated text.
4. Verify `response.done` no longer emits an empty assistant transcript final as a substitute for transcript done.
5. Verify `response.done.usage` is parsed into a test-visible projection that retains raw usage and `plugins.search`.
6. Verify response lifecycle events update test-visible response state without pretending to solve stale cancel isolation.
7. Verify fake/event replay tests do not contact the live Qwen service.
8. Verify the runtime import path test still passes or the report explains a real blocker.
9. Verify the builder report and PR body draft exist at the fork work-area paths and contain required evidence fields.

Code quality risks:

1. Flag duplicate or conflicting response, audio, transcript, or usage state sources.
2. Flag hidden state with no test-visible projection.
3. Flag broad event-loop refactors that belong to later batches.
4. Flag overbroad edits, unrelated refactors, client churn, or root dependency churn.
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
