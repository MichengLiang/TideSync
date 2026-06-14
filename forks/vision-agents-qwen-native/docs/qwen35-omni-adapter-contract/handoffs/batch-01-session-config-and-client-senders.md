# Handoff: Batch 01 Session Config And Client Senders

Role: persistent builder subagent
Model requirement: `gpt-5.5`, reasoning `high`, `fork_context=false`
Branch: `feature/qwen35-session-config-contract`

You are not alone in the codebase. Do not revert edits made by others. If you encounter unrelated changes, work around them and report them. If you are unsure, ask the coordinator before proceeding.

## Mission

Implement the first post-baseline contract slice for the controlled Vision Agents Qwen adapter in TideSync:

1. Make Qwen3.5 session configuration explicit, testable, and contract-aligned.
2. Add the missing Qwen WebSocket client event senders needed by the closed client event set.
3. Add repeatable fake-client/static tests for this slice.
4. Produce a batch report and PR body draft.
5. Commit only the files for this batch.

Do not implement the full server event mapping, interruption state machine, video turn state, tools execution flow, usage parsing, reconnect handling, or structured Qwen error model in this batch unless a small supporting type is strictly required by the config/sender work.

## Required Reading

Read these files and line ranges before editing:

1. Contract object and nonconformance boundary:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/010-artifact-identity.adoc:14-40`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/050-conformance-model.adoc:6-19`

2. Current system facts:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/010-tidesync-runtime-path.adoc:6-34`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/030-vision-agents-qwen-adapter.adoc:15-30`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/200-current-system/050-gap-map.adoc:6-18`

3. Batch 01 target contract:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/010-source-and-runtime-contract.adoc:1-32`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/020-session-config-contract.adoc:1-52`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/030-client-event-contract.adoc:1-55`

4. Batch 01 assertions and evidence:
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/020-runtime-source-assertions.adoc:1-61`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/400-conformance-assertions/030-session-config-assertions.adoc:1-80`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/010-test-evidence-contract.adoc:1-55`
   - `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`

5. Current code:
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
   - `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
   - `src/tidesync/agent.py`
   - `tests/test_vision_agents_runtime_path.py`

## Write Scope

You may edit:

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/`
- `tests/` only if needed for TideSync-level import/config tests.
- `src/tidesync/agent.py` only if TideSync settings must expose batch 01 config values.
- `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`
- `docs/qwen35-omni-adapter-contract/pr-bodies/batch-01-session-config-and-client-senders.md`

Do not edit:

- The 09 contract book.
- Other plugin packages except if a tiny test helper import requires it and you first explain why in the report.
- Root dependency resolution unless your tests prove it is necessary.

## Functional Requirements

Session configuration:

1. The adapter must explicitly support `qwen3.5-omni-flash-realtime` as a TideSync target model and preserve configurable model/base URL/voice/FPS behavior.
2. `session.update.session` must include `modalities`, `voice`, `instructions`, `input_audio_format`, `output_audio_format`, `input_audio_transcription`, and `turn_detection`.
3. The contract default audio formats must be `pcm` for both input and output. Do not silently keep `pcm16` or `pcm24` as contract defaults.
4. Input transcription must not silently default to `gummy-realtime-v1` as the Qwen3.5 contract value. Use a Qwen3.5-aligned default from the book context, and document any compatibility unknown in the batch report.
5. Turn detection must support `server_vad`, `semantic_vad`, and WebSocket Manual mode represented as `turn_detection: null`.
6. `semantic_vad` must be selectable and visible in the captured `session.update`.
7. Manual mode must be selectable and visible in the captured `session.update`.
8. Tools/search mutual exclusion must be enforced before sending an illegal `session.update`.
9. The adapter must not send unsupported `tool_choice` or `parallel_tool_calls` fields.

Client event senders:

1. Keep existing senders for `session.update`, `input_audio_buffer.append`, `input_audio_buffer.commit`, `input_image_buffer.append`, and `response.cancel`.
2. Add senders for `input_audio_buffer.clear`, `conversation.item.create` for `function_call_output`, and `response.create`.
3. Sender methods must be directly testable with a fake WebSocket/client send log.

Testing:

1. Add static config tests that capture the `session.update` payload without contacting Qwen.
2. Cover default Qwen3.5 contract values: model URL query behavior if practical, modalities, voice, instructions, `pcm` formats, input transcription model, and turn detection.
3. Cover `semantic_vad`.
4. Cover Manual mode, including `turn_detection: None` and sender availability for commit and response.create.
5. Cover tools/search mutual exclusion as a negative test and assert no illegal `session.update` is sent.
6. Cover the new client senders and payload shapes.
7. Keep existing skipped live integration tests skipped unless you intentionally add separate fake tests.

Design constraints:

1. Keep a single source of truth for session config construction. Avoid spreading raw dictionaries across tests and runtime.
2. Prefer typed configuration objects or small focused helpers if they remove real duplication.
3. Do not hide contract-relevant state in private variables without a test-visible projection.
4. Comments should explain contract reasons that code alone cannot show, especially Qwen contract conflicts or unknown compatibility behavior.
5. Do not implement broad state-machine work in this batch.

## Commands To Run

At minimum, run:

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
```

If you edit `src/tidesync/agent.py`, also run:

```bash
uv run pytest tests
uv run ruff check src tests forks/vision-agents-qwen-native/plugins/qwen
```

If a command fails because of pre-existing unrelated issues, record the exact command, failure summary, and why it is unrelated in the batch report.

## Report Requirements

Write `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md` with:

- Branch name and commit SHA.
- Files changed.
- Contract IDs covered.
- Assertion results for:
  - `runtime-imports-controlled-adapter`
  - `dependency-resolution-reproducible`
  - `session-update-uses-qwen35-contract-values`
  - `semantic-vad-configurable`
  - `manual-mode-configurable`
  - `tools-search-mutually-exclusive`
- Test commands and output summary.
- Known unknowns or live verification blockers.
- Explicit non-goals left for future batches.

Write `docs/qwen35-omni-adapter-contract/pr-bodies/batch-01-session-config-and-client-senders.md` with a PR-ready body containing:

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
git switch -c feature/qwen35-session-config-contract
```

Commit only this batch's files. Because this is a shared workbench, use path-specific staging/commit. New files must be tracked before commit.

Use a detailed commit message. Recommended subject:

```text
feat: implement Qwen session config contract slice
```

The body should mention the 09 contract book, session config values, client sender coverage, and test evidence.

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
