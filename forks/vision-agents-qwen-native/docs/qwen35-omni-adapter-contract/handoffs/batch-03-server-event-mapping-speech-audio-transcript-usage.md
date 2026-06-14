# Handoff: Batch 03 Server Event Mapping For Audio Transcript And Usage

Role: persistent builder subagent
Model requirement: `gpt-5.5`, reasoning `high`, `fork_context=false`
Branch: `feature/qwen35-server-event-mapping`

You are not alone in the codebase. Do not revert edits made by others. If you encounter unrelated changes, work around them and report them. If you are unsure, ask the coordinator before proceeding.

## Mission

Implement the third post-baseline contract slice for the controlled Vision Agents Qwen adapter in TideSync:

1. Complete the non-interruption server event mapping needed for response lifecycle, audio done, assistant transcript done, and response.done usage.
2. Preserve and expose response ids where the current Vision Agents event types allow it, or document the projection boundary where they do not.
3. Stop using `response.done` with an empty assistant transcript as a substitute for `response.audio_transcript.done`.
4. Parse and retain Qwen `response.done.usage`, including raw usage and `plugins.search`, in a test-visible projection.
5. Add repeatable event replay tests for this slice.
6. Produce a batch report and PR body draft.
7. Commit only the files for this batch.

Do not implement the interruption flush path, stale response isolation after cancel, cancel error handling, tool execution flow, structured Qwen error model, reconnect state reset, or full PR conformance closure in this batch unless a small supporting type is strictly required by the server event mapping work.

## Required Reading

Read these files and line ranges before editing:

1. Object and boundary:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/010-artifact-identity.adoc:14-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/040-system-boundary.adoc:20-25`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`

2. Current system facts:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/020-qwen-official-contract.adoc:27-39`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/030-vision-agents-qwen-adapter.adoc:38-45`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/040-vision-agents-core-carriers.adoc:6-20`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/050-gap-map.adoc:27-32`

3. Batch 03 target contract:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/040-server-event-contract.adoc:24-64`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:36-73`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/070-tools-search-usage-contract.adoc:29-41`

4. Batch 03 assertions and evidence:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/040-event-mapping-assertions.adoc:25-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/100-coverage-map.adoc:22-36`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

5. Current Batch 01 and Batch 02 artifacts:
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md:16-92`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders-review.md`
   - `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state-review.md`

6. Current code:
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
   - `tests/test_vision_agents_runtime_path.py`

## Write Scope

You may edit:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage.md`
- `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-03-server-event-mapping-speech-audio-transcript-usage.md`

Do not edit:

- The 09 contract book.
- TideSync outer `src/tidesync/agent.py`, unless you first ask and receive coordinator approval.
- Root dependency resolution.
- Batch 01 or Batch 02 reports, review reports, or PR bodies.
- `plugins/qwen/vision_agents/plugins/qwen/client.py` unless a server event mapping test proves a tiny local helper is required; ask before changing it.

## Functional Requirements

Response lifecycle:

1. Handle `response.created` and bind the current response id.
2. Handle `response.output_item.added`, `conversation.item.created`, `response.content_part.added`, `response.content_part.done`, `response.output_item.done`, and `response.done` enough to update a test-visible response state projection.
3. Do not implement stale response isolation after cancel in this batch. It belongs to Batch 04.
4. Do not use `response.done` to emit an empty assistant transcript final. `response.done` may close response state and parse usage, but transcript final must come from `response.audio_transcript.done` or text done if text-only support is explicitly implemented.

Audio output:

1. Continue decoding `response.audio.delta` as 24 kHz PCM and emitting `RealtimeAudioOutput`.
2. Handle `response.audio.done` and emit `RealtimeAudioOutputDone(interrupted=False)` or the available equivalent Vision Agents core event.
3. Record or expose the audio output state transition from streaming to done.

Assistant transcript:

1. Continue mapping `response.audio_transcript.delta` to assistant transcript delta.
2. Handle `response.audio_transcript.done` and emit assistant transcript final using the server-provided complete transcript, or local accumulated delta text if the done payload omits text.
3. Do not emit an empty final unless the service actually returns an empty final transcript.

User transcript:

1. Preserve existing final mapping for `conversation.item.input_audio_transcription.completed`.
2. If the code can add `conversation.item.input_audio_transcription.delta` without broad churn, map it to user transcript delta and cover it with a small test. If this would require uncertain core behavior, ask the coordinator before implementing.

Usage:

1. Parse `response.done.usage`.
2. Retain raw usage and parsed top-level token fields in a test-visible projection.
3. Preserve `usage.plugins.search` if present.
4. Do not implement the full metrics projection if Vision Agents core lacks a clear target surface; record the projection boundary in the batch report and keep the test-visible projection.
5. If usage parsing fails on a present usage payload, preserve raw payload and expose parse failure state; do not let the reader task crash.

Testing:

1. Add replay tests for audio delta followed by audio done.
2. Add replay tests for audio transcript delta followed by audio transcript done and verify final transcript text is not empty unless payload is empty.
3. Add replay tests for response.done usage with raw usage and `plugins.search`.
4. Add replay tests for response lifecycle events updating the test-visible response state projection.
5. Preserve Batch 01 and Batch 02 tests.
6. Keep existing live integration tests skipped.

Design constraints:

1. Keep a single source of truth for response, audio output, transcript, and usage projection state.
2. Prefer small typed state objects, enums, or focused helpers if they make state responsibilities explicit.
3. Provide a test-visible projection for response and usage state.
4. Comments should explain contract reasons that code alone cannot show, especially why `response.done` is not a transcript final substitute.
5. Do not broaden into Batch 04 interruption/stale-response behavior or Batch 05 tool execution.

## Commands To Run

At minimum, run:

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
```

If a command fails because of pre-existing unrelated issues, record the exact command, failure summary, and why it is unrelated in the batch report.

## Report Requirements

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage.md` with:

- Branch name and commit SHA.
- Files changed.
- Contract IDs covered.
- Assertion results for:
  - `audio-delta-and-done-map-to-output`
  - `transcript-delta-and-done-map-to-final`
  - `response-done-parses-usage`
- Response lifecycle coverage summary.
- Test commands and output summary.
- Known unknowns or live verification blockers.
- Explicit non-goals left for future batches.

Write `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-03-server-event-mapping-speech-audio-transcript-usage.md` with a PR-ready body containing:

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
git switch -c feature/qwen35-server-event-mapping
```

Commit only this batch's files. Because this is a shared workbench, use path-specific staging/commit. New files must be tracked before commit.

Use a detailed commit message. Recommended subject:

```text
feat: map Qwen audio transcript and usage events
```

The body should mention the 09 contract book, audio done, transcript done, response.done usage, event replay evidence, and non-goals.

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
