# Handoff: Batch 02 Input Turn And Video Send-Permission State

Role: persistent builder subagent
Model requirement: `gpt-5.5`, reasoning `high`, `fork_context=false`
Branch: `feature/qwen35-input-turn-video-state`

You are not alone in the codebase. Do not revert edits made by others. If you encounter unrelated changes, work around them and report them. If you are unsure, ask the coordinator before proceeding.

## Mission

Implement the second post-baseline contract slice for the controlled Vision Agents Qwen adapter in TideSync:

1. Replace the global `_audio_emitted_once` video gate with per-input-turn audio and video send-permission state.
2. Close the current image send window when Qwen reports `input_audio_buffer.speech_stopped`.
3. Close or reset the current image send window when Manual mode commits or clears the input audio buffer.
4. Reset video permission on track removal and track reconnect so a new track waits for current-turn audio.
5. Suspend video sending after a Qwen image timing error until a new valid input turn reopens permission.
6. Add repeatable fake-client/event tests for this slice.
7. Produce a batch report and PR body draft.
8. Commit only the files for this batch.

Do not implement the full audio output done mapping, transcript done mapping, response.done usage parsing, interruption flush path, stale response isolation, tool execution flow, search usage parsing, structured Qwen error model, or reconnect state reset in this batch unless a tiny supporting hook is strictly required for input-turn/video permission behavior.

## Required Reading

Read these files and line ranges before editing:

1. Object and boundary:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/010-artifact-identity.adoc:14-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/040-system-boundary.adoc:20-25`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`

2. Current system facts:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/020-qwen-official-contract.adoc:20-25`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/030-vision-agents-qwen-adapter.adoc:31-36`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/050-gap-map.adoc:20-25`

3. Batch 02 target contract:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/030-client-event-contract.adoc:29-41`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:13-23`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:22-35`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/080-error-contract.adoc:20-25`

4. Batch 02 assertions and evidence:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/040-event-mapping-assertions.adoc:6-23`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/060-video-turn-assertions.adoc:1-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

5. Current Batch 01 artifacts:
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md:16-70`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders-review.md`

6. Current code:
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
   - `tests/test_vision_agents_runtime_path.py`

## Write Scope

You may edit:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py` only if the provider needs a tiny client hook for clear/commit state consistency.
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-02-input-turn-and-video-send-permission-state.md`

Do not edit:

- The 09 contract book.
- TideSync outer `src/tidesync/agent.py`, unless you first ask and receive coordinator approval.
- Root dependency resolution.
- Batch 01 reports, review report, or PR body except to reference them from the Batch 02 report.

## Functional Requirements

Input turn state:

1. Maintain current input-turn state for `turn_empty`, `audio_appended`, `speech_started`, `speech_stopped`, `committed`, and `cleared`, or use equivalent internal names with a test-visible projection.
2. Every `input_audio_buffer.append` sent by the provider must update current-turn state and establish current-turn audio presence.
3. `input_audio_buffer.speech_started` must update current-turn state and emit the existing or appropriate user speech started core event if the current adapter already has such a helper. Do not implement the full interruption path in this batch.
4. `input_audio_buffer.speech_stopped` must update current-turn state, close current-turn image sending, and emit user speech ended if the current adapter can do so without broad event-mapping work.
5. Manual `input_audio_buffer.commit` must close current-turn image sending and move the current turn to committed/waiting-response state.
6. Manual `input_audio_buffer.clear` must close current-turn image sending and move the current turn to cleared/empty state.

Video send-permission state:

1. Replace `_audio_emitted_once` as the sole video gate. A historical audio append must not allow later tracks or later turns to send images before current-turn audio.
2. New or reconnected video tracks must start in a waiting-for-current-audio state.
3. A frame must not send before current-turn audio append.
4. After current-turn audio append, frames may send until the current turn is closed by speech stopped, commit, clear, track removal, track reconnect, or image timing error.
5. After `speech_stopped`, no more image frames may be sent for the closed turn.
6. After Manual commit or clear, no more image frames may be sent for the closed/cleared turn.
7. After track removal and later track reconnect, the new track must wait for current-turn audio before sending images.
8. A Qwen image timing error must suspend video sending until a new valid input turn establishes audio permission again.

Error and event boundary:

1. Detect Qwen image timing errors from structured `error` events conservatively by using available `error.code`, `error.message`, and `error.param` fields.
2. Do not replace the future structured Qwen error model. This batch only needs enough error recognition to stop blind image sending after an image timing error.
3. Preserve existing error emission behavior while adding the video-permission state effect.

Testing:

1. Add tests proving no image is sent before current-turn audio.
2. Add tests proving an image can be sent after current-turn audio.
3. Add tests proving `input_audio_buffer.speech_stopped` closes the image window.
4. Add tests proving Manual commit and clear close the image window.
5. Add tests proving track reconnect waits for new current-turn audio.
6. Add tests proving image timing error suspends sending and a new valid audio turn can reopen permission.
7. Keep existing live integration tests skipped.

Design constraints:

1. Keep a single source of truth for input-turn and video permission state. Do not spread unrelated booleans across runtime and tests.
2. Prefer small typed state objects, enums, or focused helpers if they make the state responsibilities explicit.
3. Provide a test-visible projection for the state responsibilities. It may be a private helper/property if tests are in the provider test module.
4. Comments should explain contract reasons that code alone cannot show, especially why historical audio cannot authorize later image sends.
5. Do not implement broad server event mapping beyond the speech and image-permission events needed by this batch.

## Commands To Run

At minimum, run:

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

If a command fails because of pre-existing unrelated issues, record the exact command, failure summary, and why it is unrelated in the batch report.

## Report Requirements

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md` with:

- Branch name and commit SHA.
- Files changed.
- Contract IDs covered.
- Assertion results for:
  - `speech-events-map-to-user-turn`
  - `image-not-sent-before-turn-audio`
  - `image-window-closes-after-speech-stopped`
  - `image-timing-error-suspends-sending`
  - `track-reconnect-waits-for-current-audio`
- Test commands and output summary.
- Known unknowns or live verification blockers.
- Explicit non-goals left for future batches.

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-02-input-turn-and-video-send-permission-state.md` with a PR-ready body containing:

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
git switch -c feature/qwen35-input-turn-video-state
```

Commit only this batch's files. Because this is a shared workbench, use path-specific staging/commit. New files must be tracked before commit.

Use a detailed commit message. Recommended subject:

```text
feat: implement Qwen input turn video permission state
```

The body should mention the 09 contract book, input-turn state, video permission state, event/error evidence, and test commands.

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
