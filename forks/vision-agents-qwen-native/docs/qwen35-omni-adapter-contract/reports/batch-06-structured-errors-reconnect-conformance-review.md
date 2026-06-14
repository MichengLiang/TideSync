# Batch 06 Review: Structured Errors Reconnect And Conformance Closure

Review verdict: `APPROVED_WITH_NOTES`

Reviewed branch: `feature/qwen35-error-reconnect-conformance`

Reviewed commit SHA: `3e15f20bf04a39e32fe5c82e42d972b684629f67`

Implementation commit SHA: `3b26850e38bf46c3b6b2d3dbe9d24a7bee6217ea`

Review package: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/review-packages/batch-06-structured-errors-reconnect-conformance-spec-review.md`

## Scope Reviewed

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-06-structured-errors-reconnect-conformance.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-06-structured-errors-reconnect-conformance.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`

The worktree was on the expected branch and HEAD before review. I did not modify implementation code.

## Contract Coverage Table

| Required check | Review result | Evidence |
|---|---:|---|
| Preserve Qwen `error` fields: `event_id`, `error.type`, `error.code`, `error.message`, `error.param` | PASS | `QwenStructuredErrorSnapshot` preserves those fields plus `raw_error`, state, impact scope, and recoverability in `qwen_realtime.py:220`; `_structured_error_from_event()` copies the event fields in `qwen_realtime.py:1222`. `test_qwen_error_keeps_structured_fields_and_impact_scope` asserts the projection in `test_qwen_realtime.py:729`. |
| Classify session config, image/input timing, cancel, tool, usage, recoverable connection, and unknown error states | PASS_WITH_NOTES | The enum includes the required states in `qwen_realtime.py:107`. Qwen server error classification covers image timing, cancel, audio format, transcription, tool schema, session/model/auth config, and unknown in `qwen_realtime.py:1204`. Local paths cover search/tools conflict in `qwen_realtime.py:508`, tool execution failure in `qwen_realtime.py:963`, usage parse failure in `qwen_realtime.py:993`, and recoverable reconnect in `qwen_realtime.py:1144`. Terminal connection is represented but not live-replayed; the final statement records live reconnect/service behavior as unknown. |
| Define impact scope for each error state | PASS | Structured Qwen errors carry impact scope in `qwen_realtime.py:1091` and `qwen_realtime.py:1204`; local errors carry impact scope in `qwen_realtime.py:1114`; tests assert session, reconnect, and usage scopes in `test_qwen_realtime.py:752`, `test_qwen_realtime.py:862`, and `test_qwen_realtime.py:1055`. |
| Session config errors fail/restrict session and block later audio, image, commit, clear, response.create | PASS | `_record_qwen_error()` fails the session for session config, audio format, and transcription model errors in `qwen_realtime.py:1107`; `_can_send_realtime_event()` blocks failed sessions in `qwen_realtime.py:1136`; audio, commit/create, clear, video, and tool output paths call the guard in `qwen_realtime.py:568`, `qwen_realtime.py:577`, `qwen_realtime.py:583`, `qwen_realtime.py:670`, and `qwen_realtime.py:977`. The replay test asserts no sends after the original `session.update` in `test_qwen_realtime.py:772`. |
| Recoverable close codes 1011, 1012, 1013, 1014 enter reconnecting/equivalent, reset old state, and resend `session.update` | PASS | Client reconnect callbacks are wired in `client.py:22` and invoked in `client.py:88`; recoverable codes are listed in `client.py:163`. Adapter reconnect start records state and calls centralized reset in `qwen_realtime.py:1144`; reset clears response/current item/responding/input/video/response/interruption/tool state in `qwen_realtime.py:1168`. Parametrized replay covers all four close codes in `test_qwen_realtime.py:810`. |
| Reconnect reset prevents stale response ids, old image permission, old local audio output | PASS | Reset clears `response_id`, `item_id`, `audio_output`, and video permission in `qwen_realtime.py:1168`; test assertions cover response projection and `track_reconnected_waiting_audio` and block a post-reconnect video frame in `test_qwen_realtime.py:871` and `test_qwen_realtime.py:891`. |
| Usage parse failure keeps raw payload | PASS | `_parse_response_usage()` records parse failure and retains the snapshot in `qwen_realtime.py:993`; replay asserts `raw_usage`, parse error text, and `usage_parse_error` in `test_qwen_realtime.py:1028`. |
| Batch 01 through Batch 05 regressions still pass | PASS | Fresh command `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests` returned `37 passed, 2 skipped`. The skipped tests are existing live integration tests. |
| Final conformance statement contains required fields | PASS | `final-conformance-statement.md` contains implementation scope, upstream source, runtime path evidence, assertion results, test commands, live verification, deviations, unknowns, and rollback impact. |
| Final conformance statement avoids overclaiming live smoke, latency, undocumented payload variants | PASS | Live Qwen smoke is explicitly not run; interruption latency is `BLOCKED`; undocumented payload variants and live reconnect timing remain unknown in `final-conformance-statement.md`. |
| No unrelated product behavior, dependency churn, or broad core refactor | PASS | Diff scope is limited to Qwen adapter/client/tests plus Batch 06 report, PR body, and final statement. No root dependency or core runtime files were changed. |

## Findings

No blocking findings.

### Low: Classification evidence is not one replay per state

The implementation includes the required state vocabulary and local classification paths, but deterministic replay coverage is deepest for the four Batch 06 assertions: structured session config error, failed-session send blocking, recoverable reconnect reset, and usage parse failure. Other states rely on earlier batch tests or direct code-path inspection rather than a new Batch 06 table-driven classification replay.

References:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:107`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:1204`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py:729`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py:810`

This is not a promotion blocker because the review package requires explicit justification for not-applicable states and because the final conformance statement records live/undocumented variants as unknown rather than verified.

### Low: Terminal connection behavior remains represented, not live-proven

`connection_error_terminal` exists in the adapter error vocabulary, but Batch 06 does not add a live or fake terminal-close replay proving a terminal connection projection. The review package qualifies terminal connection coverage as "where applicable", and the final conformance statement records live reconnect/service-side behavior as unmeasured.

References:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:112`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`

This is a non-blocking evidence boundary, not a contract failure for this batch.

## Final Conformance Statement Audit

Result: PASS.

The final statement satisfies the required PR conformance fields from `parts/500-evidence-governance/020-pr-conformance-statement.adoc:13-34`:

- Implementation scope is listed.
- Upstream source includes repository, tag, commit, import date, imported paths, omitted paths, and local modification policy.
- Runtime path evidence points to the runtime import path test and accepted Batch 00/01 evidence.
- Assertion results are tabulated across Batches 00 through 06.
- Test commands and summaries are listed.
- Live verification states that live Qwen smoke was not run.
- Deviations mark live interruption latency as blocked.
- Unknowns include undocumented payload variants, live function-call variants, and live reconnect timing/service-side behavior.
- Rollback impact is stated.

I did not find overclaiming of live smoke, live interruption latency, or undocumented payload variant coverage.

## Test Evidence Reviewed

Fresh verification commands run during this review:

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
```

Result: `1 passed`. The command emitted the existing narrow-test coverage warnings: `Module tidesync was never imported`, `No data was collected`, and no coverage report.

```bash
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
```

Result: `37 passed, 2 skipped`. The skipped tests are the existing live integration tests. The same known coverage warnings appeared.

```bash
uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

Result: `All checks passed!`

```bash
uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

Result: `3 files already formatted`.

## Missing Evidence

- Live Qwen smoke was not run.
- Live interruption latency remains unmeasured.
- Live reconnect timing and service-side session behavior after transient close codes remain unmeasured.
- Undocumented Qwen error payload variants remain unknown.
- Terminal connection behavior is represented but not replay-proven in this batch.

These gaps are recorded as blockers/unknowns in the final conformance statement and are not blocking the deterministic Batch 06 promotion decision.

## Promotion Recommendation

Promote Batch 06 with notes.

The implementation satisfies the deterministic Batch 06 contract checks, preserves prior batch regression tests, keeps the change scope inside the Qwen adapter/client/test and evidence surfaces, and provides the required final conformance statement without overclaiming live evidence.
