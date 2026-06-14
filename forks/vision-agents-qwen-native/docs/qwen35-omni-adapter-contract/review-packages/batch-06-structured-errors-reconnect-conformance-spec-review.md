# Review Package: Batch 06 Structured Errors Reconnect And Conformance Closure

Review role: independent spec reviewer

Do not fix code during this review. Produce findings only. Long findings must be written to:

`forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-06-structured-errors-reconnect-conformance-review.md`

## Review Object

Review the implementation produced by the builder for:

- Handoff: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/handoffs/batch-06-structured-errors-reconnect-conformance.md`
- Expected branch: `feature/qwen35-error-reconnect-conformance`
- Expected builder report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-06-structured-errors-reconnect-conformance.md`
- Expected PR body draft: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-06-structured-errors-reconnect-conformance.md`
- Expected final conformance statement: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`

## Review Basis

Required contract sources:

- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc:32-120`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:21-33`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:35-54`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:65-70`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:8-14`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:75-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:1-37`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/080-error-assertions.adoc:1-80`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:38-40`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`
- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/030-upstream-provenance.adoc:1-39`

Implementation files likely in scope:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py` only if the builder changed it
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- Batch report, PR body draft, and final conformance statement files

## Required Checks

Spec compliance:

1. Verify every Qwen `error` event preserves `event_id`, `error.type`, `error.code`, `error.message`, and `error.param` in a deterministic test-readable object or equivalent metadata.
2. Verify error classification covers session config, recoverable connection, terminal connection where applicable, image/input timing, audio format, transcription model, cancel, tool schema/execution, search/tools conflict, usage parse, and unknown Qwen error states, or explicitly justifies not-applicable states in final conformance.
3. Verify each error state defines impact scope.
4. Verify session config errors fail or restrict the session and block later audio, image, commit, clear, and response.create sends.
5. Verify recoverable close codes 1011, 1012, 1013, and 1014 enter reconnecting or equivalent state, reset old response/input/video/audio/tool state, and resend `session.update`.
6. Verify reconnect reset prevents stale response ids, old image permission, and old local audio output from carrying across reconnect.
7. Verify usage parse failure raw payload evidence still passes.
8. Verify Batch 01 through Batch 05 regression tests still pass.
9. Verify final conformance statement contains all fields required by the PR conformance statement contract.
10. Verify final conformance statement does not claim live Qwen smoke, interruption latency, or undocumented payload variants are verified when they remain blocked.
11. Verify implementation stays within Batch 06 and does not introduce unrelated product behavior, dependency churn, or broad core refactors.

Evidence checks:

1. Verify error replay tests cover structured fields and classification.
2. Verify session config error replay tests cover failed/restricted session behavior.
3. Verify reconnect fake tests cover state reset and new session.update.
4. Verify usage parse failure replay remains present.
5. Verify tests do not contact the live Qwen service.
6. Verify the runtime import path test still passes or the report explains a real blocker.
7. Verify the builder report, PR body draft, and final conformance statement exist at the fork work-area paths and contain required evidence fields.

Code quality risks:

1. Flag keyword-only classification that is unmaintainable or contradicts more specific errors.
2. Flag stale state clearing spread across many methods instead of centralized reset.
3. Flag private logs used as the only structured error or reconnect evidence.
4. Flag failed-session state that is visible but does not actually block later sends.
5. Flag final conformance statements that blur `PASS`, `BLOCKED`, `DEVIATION`, and `UNKNOWN`.

## Output Format

The review report must contain:

- Review verdict: `APPROVED`, `APPROVED_WITH_NOTES`, or `CHANGES_REQUIRED`.
- Reviewed commit SHA.
- Contract coverage table.
- Findings ordered by severity with file and line references.
- Final conformance statement audit.
- Test evidence reviewed.
- Missing evidence, if any.
- Recommendation for coordinator promotion decision.

The chat response should be short and point to the review report path.
