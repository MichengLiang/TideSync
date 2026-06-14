# Handoff: Batch 04 Interruption Local Flush Stale Response And Cancel Error

Role: persistent builder subagent
Model requirement: `gpt-5.5`, reasoning `high`, `fork_context=false`
Branch: `feature/qwen35-interruption-state`

You are not alone in the codebase. Do not revert edits made by others. If you encounter unrelated changes, preserve them, work around them, and report them. If you are unsure whether a change is unrelated, ask the coordinator before proceeding.

## Mission

Implement the fourth post-baseline contract slice for the controlled Vision Agents Qwen adapter in TideSync:

1. Turn Qwen `input_audio_buffer.speech_started` into a real barge-in path when agent output is active or locally still playable.
2. Emit the Vision Agents core public flush carriers needed for local audio interruption.
3. Mark the interrupted response id so late audio, transcript, text, and completion events for that response cannot re-enter current output.
4. Send `response.cancel` when a cancellable response exists, without making remote cancel success a prerequisite for local flush.
5. Preserve enough structured cancel-error information for deterministic tests.
6. Add event replay tests for barge-in, cancel error, and stale delayed deltas.
7. Produce a batch report and PR body draft.
8. Commit only the files for this batch.

Do not implement Batch 05 tool execution, search flow, tool errors, full structured Qwen error model, reconnect state reset, or final full conformance closure in this batch. Batch 04 may add the minimum cancel-error projection needed to prove that cancel errors do not undo local interruption.

## Required Reading

Read these files and line ranges before editing:

1. Object and boundary:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/010-artifact-identity.adoc:14-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/040-system-boundary.adoc:20-25`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`

2. Current system facts:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/040-vision-agents-core-carriers.adoc:6-27`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/050-gap-map.adoc:33-38`

3. Batch 04 target contract:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:13-22`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:33-47`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:65-70`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:36-63`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:75-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/060-interruption-contract.adoc:1-44`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:6-18`

4. Batch 04 assertions and evidence:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/050-interruption-assertions.adoc:1-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:37-45`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

5. Current accepted batch evidence:
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage-review.md`

6. Current code:
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/llm/realtime.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/agents/inference/realtime_flow.py`
   - `forks/vision-agents-qwen-native/agents-core/vision_agents/core/agents/inference/audio.py`
   - `tests/test_vision_agents_runtime_path.py`

## Current Baseline Facts

Batch 03 is already merged to `main` at merge commit `01ed97c`.

Important implementation facts at the Batch 04 starting point:

1. `qwen_realtime.py` already maps `response.audio.done` to `RealtimeAudioOutputDone(interrupted=False)` and `RealtimeAgentSpeechEnded(interrupted=False)`.
2. `qwen_realtime.py` currently enters `_on_interruption()` only when `_is_responding` is true.
3. `_on_interruption()` currently sends `response.cancel` only when `_current_response_id` is set, then clears `_is_responding`, `_current_response_id`, and `_current_item_id`.
4. Current state projections do not yet distinguish `cancel_requested`, `interrupted`, `audio_interrupted`, `audio_flush_emitted`, `stale_audio_blocked`, or `transcript_interrupted_boundary`.
5. Core already has `RealtimeAudioOutputDone(interrupted=True)` and `RealtimeAgentSpeechEnded(interrupted=True)`.
6. `RealtimeInferenceFlow` calls `interrupt()` when it receives `RealtimeAudioOutputDone(interrupted=True)`, and `interrupt()` clears transcripts, clears `AudioOutputStream`, and emits downstream audio flush.

These facts are the reason Batch 04 is an adapter-state and adapter-event projection task, not a core refactor task.

## Write Scope

You may edit:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-04-interruption-local-flush-stale-response-cancel-error.md`

You may edit `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py` only if a deterministic test proves the existing `cancel_response()` surface is insufficient for the Batch 04 requirements.

Do not edit:

- The 09 contract book.
- TideSync outer `src/tidesync/agent.py`.
- Root dependency resolution.
- Batch 01, Batch 02, or Batch 03 reports, review reports, or PR bodies.
- Core runtime files unless you first ask the coordinator and receive approval. The current core event carriers are sufficient for Batch 04.

## Functional Requirements

Interruption trigger:

1. `input_audio_buffer.speech_started` must always emit `RealtimeUserSpeechStarted`.
2. The decision to enter interruption must not depend only on `_is_responding`.
3. The decision must consider current response state, local audio output state, unfinished transcript state, and the risk that old response deltas may arrive after cancel.
4. If no agent output or local playable output exists, `speech_started` should remain a normal user turn start and should not emit an interrupted agent/audio boundary.

Local flush:

1. The interruption path must emit `RealtimeAudioOutputDone(interrupted=True)` or the available equivalent core event.
2. The same path must emit `RealtimeAgentSpeechEnded(interrupted=True)` or the available equivalent agent turn-ended event.
3. The local flush event must be emitted even if `response.cancel` later fails or the server reports no cancellable response.
4. The adapter's test-visible projection must record the local audio state as interrupted/flushed or equivalent.

Remote cancel:

1. If a current response id is cancellable, send `response.cancel`.
2. Mark the response state as cancel requested or interrupted before relying on server acknowledgement.
3. A Qwen cancel error must not restore the response to normal streaming/completed state.
4. Preserve structured cancel-error fields that deterministic tests can inspect: `event_id`, `error.type`, `error.code`, `error.message`, and `error.param` when present.

Stale response isolation:

1. The interrupted response id must be recorded as cancelled or interrupted.
2. Late `response.audio.delta` for the interrupted response id must not emit `RealtimeAudioOutput`.
3. Late `response.audio_transcript.delta` and `response.text.delta` for the interrupted response id must not emit current agent transcript deltas.
4. Late completion events for the interrupted response id must not convert the interrupted response into a normal completed current response.
5. Stale audio/transcript blocking must be visible in the adapter projection or another deterministic test surface.
6. Do not block events for a later valid response id.

Transcript boundary:

1. Interrupted assistant transcript fragments must not be finalized as a complete delivered assistant message.
2. The adapter must expose or record a transcript interruption boundary when the interrupted response had unfinished transcript text.
3. Do not use `response.done` as a substitute for assistant transcript finality.

Error scope:

1. Implement only the cancel-error subset needed by Batch 04.
2. Preserve existing image timing error behavior.
3. Do not implement full recoverability, reconnect cleanup, session config error classification, tool errors, or usage error closure in this batch.

Testing:

1. Add a barge-in replay test with response `resp_1` actively outputting audio, followed by `input_audio_buffer.speech_started`.
2. Assert that the output stream contains `RealtimeUserSpeechStarted`, `RealtimeAudioOutputDone(interrupted=True)`, and `RealtimeAgentSpeechEnded(interrupted=True)`.
3. Assert that fake client send log includes `response.cancel` when `resp_1` is cancellable.
4. Add a cancel-error replay test where the adapter has already interrupted locally and then receives a Qwen `error` event for a no-cancellable-response/cancel error. Assert local flush state remains interrupted/flushed and stale isolation remains active.
5. Add a delayed stale delta replay test where `resp_1` is interrupted, then late `response.audio.delta` and `response.audio_transcript.delta` arrive for `resp_1`; assert no new playable audio or current transcript is emitted for that stale response.
6. Add a non-stale follow-up test if needed to prove a later valid response id can still emit audio/transcript after interruption.
7. Preserve all Batch 01 through Batch 03 tests.
8. Keep existing live integration tests skipped.

Design constraints:

1. Keep a single source of truth for response id status, response projection, local audio projection, and transcript interruption boundary.
2. Prefer small typed state objects, enums, or focused helpers when they make the contract state responsibilities explicit.
3. Avoid broad event-loop refactors. The change should be readable as a state-machine improvement around interruption.
4. Add comments only where code alone does not expose the contract reason, especially stale delta defense after `response.cancel`.
5. Do not add private logs as the only evidence of contract behavior. Tests need a deterministic object, emitted event, or snapshot.

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

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error.md` with:

- Branch name and commit SHA.
- Files changed.
- Contract IDs covered.
- Assertion results for:
  - `speech-started-interrupts-current-response`
  - `cancel-error-does-not-block-local-flush`
  - `stale-delta-after-interrupt-blocked`
- Local flush and stale isolation state summary.
- Cancel-error projection summary.
- Test commands and output summary.
- Known unknowns or live verification blockers.
- Explicit non-goals left for future batches.

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-04-interruption-local-flush-stale-response-cancel-error.md` with a PR-ready body containing:

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
git switch -c feature/qwen35-interruption-state
```

Commit only this batch's files. Because this is a shared workbench, use path-specific staging/commit. New files must be tracked before commit.

Use a detailed commit message. Recommended subject:

```text
feat: implement Qwen interruption state handling
```

The body should mention the 09 contract book, barge-in local flush, response.cancel, stale response id isolation, cancel error evidence, event replay tests, and non-goals.

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
