# Handoff: Batch 06 Structured Errors Reconnect And Conformance Closure

Role: persistent builder subagent
Model requirement: `gpt-5.5`, reasoning `high`, `fork_context=false`
Branch: `feature/qwen35-error-reconnect-conformance`

You are not alone in the codebase. Do not revert edits made by others. If you encounter unrelated changes, preserve them, work around them, and report them. If you are unsure whether a change is unrelated, ask the coordinator before proceeding.

## Mission

Implement the final contract slice for the controlled Vision Agents Qwen adapter in TideSync:

1. Preserve structured Qwen `error` fields in deterministic adapter state or equivalent test-readable projection.
2. Classify Qwen/server/local errors into the remaining contract error states, with explicit impact scope.
3. Make session configuration errors fail or restrict the session so TideSync cannot keep sending media or responses as if realtime is ready.
4. Add recoverable reconnect state reset behavior and fake reconnect evidence for close codes 1011, 1012, 1013, and 1014.
5. Preserve the usage parse failure evidence already introduced earlier and include it in the final closure.
6. Write a final PR conformance statement for the 09 contract book, including implementation scope, upstream provenance, runtime path evidence, assertion results, verification commands, live blockers, deviations, unknowns, and rollback impact.
7. Produce a batch report and PR body draft that point to the final conformance statement.
8. Commit only the files for this batch.

Do not broaden into new product behavior outside the 09 contract book. Live Qwen verification remains blocked unless explicit API key, cost authorization, and service availability are present; blocked live verification must be recorded as a blocker/unknown, not as completed evidence.

## Required Reading

Read these files and line ranges before editing:

1. Object and conformance boundary:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc:32-120`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/010-artifact-identity.adoc:14-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/040-system-boundary.adoc:20-25`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:21-33`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:35-54`

2. Batch 06 target contract:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:65-70`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:8-14`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:75-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:1-37`

3. Batch 06 assertions and evidence:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/080-error-assertions.adoc:1-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:38-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/030-upstream-provenance.adoc:1-39`

4. Current accepted batch evidence:
   - `forks/vision-agents-qwen-native/UPSTREAM.adoc`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md`
   - all Batch 01 through Batch 05 reports and review reports under `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/`
   - all Batch 01 through Batch 05 PR body drafts and review trail comments under `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/`

5. Current code:
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/llm/events.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/llm/llm.py`
   - `tests/test_vision_agents_runtime_path.py`

## Current Baseline Facts

Batch 05 is merged to `main` at merge commit `b4f80ba`.

Important implementation facts at the Batch 06 starting point:

1. Current Qwen error handling sets only a small enum subset and emits `Exception(str(error))`; full structured Qwen fields are not yet test-readable except the Batch 04 cancel-error subset.
2. Current `ErrorState` does not yet include all contract states: `session_config_error`, `connection_error_recoverable`, `connection_error_terminal`, `audio_format_error`, `transcription_model_error`, `tool_schema_error`, `tool_execution_error`, `search_tools_conflict_error`, and `usage_parse_error`.
3. Usage parse failure is already test-visible through `_qwen_usage_snapshot()` and `usage_parse_failed`; Batch 06 should connect that evidence to final conformance rather than rewrite it unnecessarily.
4. Current `Qwen3RealtimeClient.read()` reconnects internally for recoverable websocket close codes, but adapter state reset/reconnect projection is not yet explicit.
5. Session config error currently flows through generic `error` handling and does not reliably fail or restrict the session.
6. `UPSTREAM.adoc` already records upstream repository, tag, commit, import date, import scope, omitted paths, local modification policy, and sync policy.

## Write Scope

You may edit:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py` only if fake reconnect evidence requires a minimal observable hook or state reset signal
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-06-structured-errors-reconnect-conformance.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-06-structured-errors-reconnect-conformance.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`

Do not edit:

- The 09 contract book.
- TideSync outer `src/tidesync/agent.py`.
- Root dependency resolution.
- Batch 01 through Batch 05 reports, review reports, or PR bodies.
- Core runtime files unless you first ask the coordinator and receive approval.

## Functional Requirements

Structured Qwen errors:

1. Preserve `event_id`, `error.type`, `error.code`, `error.message`, and `error.param` for every Qwen `error` event.
2. Expose those fields through deterministic adapter state, metadata, or an equivalent test-readable object.
3. Classify at least session config errors, input timing/image errors, cancel errors, tool errors, usage parse errors, and unknown Qwen errors into explicit error states.
4. Every error state must define an impact scope covering the affected session, input turn, video permission, response, local audio output, tool, or usage state.
5. Preserve existing Batch 04 cancel-error evidence and Batch 05 tool-error evidence.

Session config error:

1. Detect session configuration errors from Qwen `error` payload fields such as code/message/param referring to session, model, auth, audio format, transcription model, or invalid config.
2. Enter rejected/failed or restricted session state and preserve structured fields.
3. After a session config error, do not continue to send audio, images, commits, clears, or response.create as if the session is usable.
4. Emit or expose an error event/projection that tests can inspect.

Recoverable reconnect:

1. Cover recoverable close codes 1011, 1012, 1013, and 1014 with fake WebSocket/client tests.
2. Enter reconnecting or equivalent test-visible state.
3. Clear or isolate old response id, old input turn permission, old local audio output state, interrupted response ids, pending tool calls, and current item id.
4. After reconnect, session.update must be sent again.
5. Do not continue to use stale response ids or old video permission after reconnect.

Usage parse error:

1. Preserve existing `usage_parse_failed` behavior and raw usage retention.
2. Ensure final conformance statement lists this `should` assertion result accurately as passed if replay evidence exists, or as a deviation if not.

Final conformance statement:

1. Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md`.
2. Include all fields required by `pr-conformance-statement.adoc:13-34`.
3. Include upstream provenance from `UPSTREAM.adoc`.
4. Include runtime path evidence from `tests/test_vision_agents_runtime_path.py` and the accepted Batch 00/01 evidence.
5. Include assertion results for the 09 book's core assertions across batches. Use explicit statuses: `PASS`, `PASS_WITH_NOTES`, `BLOCKED`, `NOT_APPLICABLE`, or `DEVIATION`.
6. Do not claim live Qwen smoke, live interruption latency, or undocumented payload variants are verified unless they actually are.
7. Link or name the batch reports/review reports that prove each assertion.

Testing:

1. Add structured Qwen error replay tests.
2. Add session config error tests that prove the session becomes failed/restricted and future sends are blocked.
3. Add recoverable reconnect fake tests that prove state reset and a new session.update.
4. Preserve existing usage parse failure test.
5. Preserve Batch 01 through Batch 05 tests.
6. Keep existing live integration tests skipped.

Design constraints:

1. Keep error classification readable and local to the Qwen adapter.
2. Avoid a fragile keyword soup where a small ordered classifier with documented impact scopes would be clearer.
3. Prefer explicit state snapshots over private logs.
4. Reconnect reset should reuse existing state objects where possible rather than manually clearing scattered fields in many places.
5. Comments should explain contract reasons that code alone cannot show, especially why reconnect must isolate old response/input/video/audio state.

## Commands To Run

At minimum, run:

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

If `client.py` is unchanged, it may be omitted from focused ruff commands. If a command fails because of a pre-existing unrelated issue, record the exact command, failure summary, and why it is unrelated in the batch report.

## Report Requirements

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-06-structured-errors-reconnect-conformance.md` with:

- Branch name and commit SHA.
- Files changed.
- Contract IDs covered.
- Assertion results for:
  - `qwen-error-keeps-structured-fields`
  - `recoverable-connection-resets-state`
  - `session-config-error-fails-session`
  - `usage-parse-error-retains-raw`
- Error-state and impact-scope summary.
- Reconnect reset summary.
- Final conformance statement path and summary.
- Test commands and output summary.
- Known unknowns, live blockers, and deviations.
- Explicit non-goals left outside the current contract.

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-06-structured-errors-reconnect-conformance.md` with a PR-ready body containing:

- Summary.
- Scope.
- Repository rationale.
- Contract coverage.
- Verification.
- Final conformance statement link/path.
- Live verification / blockers.
- Rollback impact.

Long explanations belong in these files, not in chat.

## Commit Requirements

Create the topic branch first:

```bash
git switch -c feature/qwen35-error-reconnect-conformance
```

Commit only this batch's files. Because this is a shared workbench, use path-specific staging/commit. New files must be tracked before commit.

Use a detailed commit message. Recommended subject:

```text
feat: close Qwen error and reconnect conformance
```

The body should mention the 09 contract book, structured error fields, session config failure, reconnect reset, usage parse evidence, final conformance statement, tests, live blockers, and non-goals.

## Final Chat Response

Return only a short status:

- `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
- Branch name.
- Commit SHA if committed.
- Report file path.
- PR body draft path.
- Final conformance statement path.
- Test commands run.
- Any question for the coordinator.

If you are unsure about scope, ask the coordinator before implementing.
