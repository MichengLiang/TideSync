# Qwen3.5 Omni Adapter Contract Coordination State

Status timestamp: 2026-06-14
Coordinator role: principal coordinator

## Current Phase

Batches 01 through 03 have landed on `main`:

- Batch 01 merge commit: `2b73b11 Merge pull request #11 from MichengLiang/feature/qwen35-session-config-contract`
- Batch 02 merge commit: `052f669 Merge pull request #12 from MichengLiang/feature/qwen35-input-turn-video-state`
- Batch 03 merge commit: `01ed97c Merge pull request #13 from MichengLiang/feature/qwen35-server-event-mapping`
- Current branch before Batch 04 dispatch: `main`
- Worktree status before Batch 04 dispatch: clean before Batch 04 prep files were authored.

Batch 04 is the next implementation slice: interruption path, local audio flush, stale response isolation, and cancel-error behavior.

Batch 01 review status:

- Branch: `feature/qwen35-session-config-contract`
- Implementation commit: `c64b067 feat: implement Qwen session config contract slice`
- Evidence-fix commit: `c183713 fix: address Batch 01 review evidence gaps`
- Reviewed final HEAD: `c183713df471e074f0adcf26a87eef0ed9535e73`
- Review verdict: `APPROVED_WITH_NOTES`
- Review report: `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders-review.md`
- Builder report: `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`
- PR body draft: `docs/qwen35-omni-adapter-contract/pr-bodies/batch-01-session-config-and-client-senders.md`
- Promotion decision: Batch 01 may be promoted. The non-blocking review note is that the builder report names `c64b067` as the implementation commit while the reviewed final HEAD is `c183713`.

## Promotion Boundary

No implementation batch may be treated as complete until all of these are true:

1. The executor committed only the batch-relevant files on a topic branch.
2. The executor wrote a batch report under `docs/qwen35-omni-adapter-contract/reports/`.
3. The executor wrote a PR body draft under `docs/qwen35-omni-adapter-contract/pr-bodies/`.
4. A separate reviewer subagent reviewed the implementation against the batch review package.
5. Review findings either approve the batch or are sent back to the same executor for fixes.
6. Evidence paths and commands are recorded in the coordination state.

## Batch Plan

Batch 00, accepted baseline:

- Controlled source exists under `forks/vision-agents-qwen-native`.
- Root dependency resolution points to local editable packages.
- Runtime import path test exists at `tests/test_vision_agents_runtime_path.py`.
- Upstream provenance exists at `forks/vision-agents-qwen-native/UPSTREAM.adoc`.

Batch 01, review accepted:

- Name: `batch-01-session-config-and-client-senders`
- Handoff: `docs/qwen35-omni-adapter-contract/handoffs/batch-01-session-config-and-client-senders.md`
- Review package: `docs/qwen35-omni-adapter-contract/review-packages/batch-01-session-config-and-client-senders-spec-review.md`
- Owner role: persistent builder subagent
- Expected branch: `feature/qwen35-session-config-contract`
- Expected report: `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`
- Expected PR body draft: `docs/qwen35-omni-adapter-contract/pr-bodies/batch-01-session-config-and-client-senders.md`
- Final reviewed HEAD: `c183713df471e074f0adcf26a87eef0ed9535e73`
- Review report: `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders-review.md`
- Verification:
  - `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`

Batch 02, review accepted:

- Name: `batch-02-input-turn-and-video-send-permission-state`
- Handoff: `docs/qwen35-omni-adapter-contract/handoffs/batch-02-input-turn-and-video-send-permission-state.md`
- Review package: `docs/qwen35-omni-adapter-contract/review-packages/batch-02-input-turn-and-video-send-permission-state-spec-review.md`
- Owner role: persistent builder subagent.
- Expected branch: `feature/qwen35-input-turn-video-state`
- Expected report: `docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md`
- Expected PR body draft: `docs/qwen35-omni-adapter-contract/pr-bodies/batch-02-input-turn-and-video-send-permission-state.md`
- Dispatch prompt: `docs/qwen35-omni-adapter-contract/handoffs/batch-02-builder-dispatch-prompt.md`
- Review dispatch prompt: `docs/qwen35-omni-adapter-contract/review-packages/batch-02-reviewer-dispatch-prompt.md`
- Implementation commit: `e6c9fb9 feat: implement Qwen input turn video permission state`
- Reviewed final HEAD: `8b5423c69f0c67f6414dabb18f0579f4c0951c4e`
- Review verdict: `APPROVED_WITH_NOTES`
- Review report: `docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state-review.md`
- Promotion decision: Batch 02 may be promoted. Non-blocking notes are that committed state is projected as `committed` rather than distinct `waiting_response`, and deterministic tests call provider hooks rather than the real `VideoForwarder` timing loop.
- Verification:
  - `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`

Batch 03, review accepted:

- Name: `batch-03-server-event-mapping-speech-audio-transcript-usage`
- Handoff: `docs/qwen35-omni-adapter-contract/handoffs/batch-03-server-event-mapping-speech-audio-transcript-usage.md`
- Review package: `docs/qwen35-omni-adapter-contract/review-packages/batch-03-server-event-mapping-speech-audio-transcript-usage-spec-review.md`
- Owner role: persistent builder subagent.
- Expected branch: `feature/qwen35-server-event-mapping`
- Expected report: `docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage.md`
- Expected PR body draft: `docs/qwen35-omni-adapter-contract/pr-bodies/batch-03-server-event-mapping-speech-audio-transcript-usage.md`
- Dispatch prompt: `docs/qwen35-omni-adapter-contract/handoffs/batch-03-builder-dispatch-prompt.md`
- Review dispatch prompt: `docs/qwen35-omni-adapter-contract/review-packages/batch-03-reviewer-dispatch-prompt.md`
- Implementation commit: `2f5896d feat: map Qwen audio transcript and usage events`
- Reviewed final HEAD: `223cc1304ddb6201a46908d1886f7fbf24aefb92`
- Review verdict: `APPROVED_WITH_NOTES`
- Review report: `docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage-review.md`
- Promotion decision: Batch 03 may be promoted. Non-blocking notes are that usage/search projection remains adapter-private for this batch, and `response.done` without `response.audio.done` closes response state but does not emit agent speech ended.
- Verification:
  - `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`

Batch 04, review accepted:

- Name: `batch-04-interruption-local-flush-stale-response-cancel-error`
- Handoff: `docs/qwen35-omni-adapter-contract/handoffs/batch-04-interruption-local-flush-stale-response-cancel-error.md`
- Review package: `docs/qwen35-omni-adapter-contract/review-packages/batch-04-interruption-local-flush-stale-response-cancel-error-spec-review.md`
- Owner role: persistent builder subagent.
- Expected branch: `feature/qwen35-interruption-state`
- Expected report: `docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error.md`
- Expected PR body draft: `docs/qwen35-omni-adapter-contract/pr-bodies/batch-04-interruption-local-flush-stale-response-cancel-error.md`
- Dispatch prompt: `docs/qwen35-omni-adapter-contract/handoffs/batch-04-builder-dispatch-prompt.md`
- Review dispatch prompt: `docs/qwen35-omni-adapter-contract/review-packages/batch-04-reviewer-dispatch-prompt.md`
- Implementation commit: `830f914 feat: implement Qwen interruption state handling`
- Review-fix commit: `105ee3f fix: unblock Qwen post-response interruption path`
- Reviewed final HEAD: `4b01c38b49fe0ffa52ca88e674581b3582ef67ad`
- Review verdict: `APPROVED_WITH_NOTES`
- Review report: `docs/qwen35-omni-adapter-contract/reports/batch-04-interruption-local-flush-stale-response-cancel-error-review.md`
- Promotion decision: Batch 04 may be promoted. Non-blocking note is that live interruption latency remains unmeasured because live Qwen verification lacks explicit API key, cost authorization, and service availability.
- Verification:
  - `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`

Future batches, not yet dispatched after Batch 05:

- Batch 06: structured Qwen errors, reconnect state reset, evidence closure, and full PR conformance statement.

Batch 05, review accepted:

- Name: `batch-05-tools-search-tool-errors`
- Handoff: `docs/qwen35-omni-adapter-contract/handoffs/batch-05-tools-search-tool-errors.md`
- Review package: `docs/qwen35-omni-adapter-contract/review-packages/batch-05-tools-search-tool-errors-spec-review.md`
- Owner role: persistent builder subagent.
- Expected branch: `feature/qwen35-tools-search-tool-errors`
- Expected report: `docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors.md`
- Expected PR body draft: `docs/qwen35-omni-adapter-contract/pr-bodies/batch-05-tools-search-tool-errors.md`
- Dispatch prompt: `docs/qwen35-omni-adapter-contract/handoffs/batch-05-builder-dispatch-prompt.md`
- Review dispatch prompt: `docs/qwen35-omni-adapter-contract/review-packages/batch-05-reviewer-dispatch-prompt.md`
- Implementation commit: `9e97bcf feat: execute Qwen function calls through registry`
- Reviewed final HEAD: `c994f473bfc6021afad39f1d0b6cf26b56f1f851`
- Review verdict: `APPROVED_WITH_NOTES`
- Review report: `docs/qwen35-omni-adapter-contract/reports/batch-05-tools-search-tool-errors-review.md`
- Promotion decision: Batch 05 may be promoted. Non-blocking notes are that tool state projection is latest-call oriented rather than a full per-call history, and broader live Qwen function-call payload variants remain unverified without live service access.
- Verification:
  - `uv run pytest tests/test_vision_agents_runtime_path.py`
  - `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`

## Role Registry

Coordinator:

- Maintains plan, resource map, role registry, handoff packages, review packages, and promotion decisions.
- Does not implement adapter code.
- Answers executor questions with exact document paths and line ranges.

Persistent builder subagent:

- Uses model `gpt-5.5`, reasoning `high`, `fork_context=false`.
- Starts from the handoff file only.
- Implements the currently dispatched batch.
- Writes long reports to files, not chat.
- Commits its own batch changes with a focused commit.

Reviewer subagent:

- Will be dispatched only after the builder returns.
- Uses the review package as review basis.
- Does not fix code unless explicitly reassigned.

## Resource Map

Authoritative contract book:

- `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc`

Batch 01 authoritative sections:

- Source/runtime contract: `parts/300-target-contract/010-source-and-runtime-contract.adoc:1-32`
- Session config contract: `parts/300-target-contract/020-session-config-contract.adoc:1-52`
- Client event contract: `parts/300-target-contract/030-client-event-contract.adoc:1-55`
- Runtime source assertions: `parts/400-conformance-assertions/020-runtime-source-assertions.adoc:1-61`
- Session config assertions: `parts/400-conformance-assertions/030-session-config-assertions.adoc:1-80`
- Test evidence contract: `parts/500-evidence-governance/010-test-evidence-contract.adoc:1-55`
- PR conformance statement: `parts/500-evidence-governance/020-pr-conformance-statement.adoc:1-41`
- Upstream provenance contract: `parts/500-evidence-governance/030-upstream-provenance.adoc:1-39`

Build object:

- `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `plugins/qwen/vision_agents/plugins/qwen/client.py`
- `plugins/qwen/tests/`
- Root TideSync tests if needed: `tests/`

Batch 04 authoritative sections:

- Interruption contract: `parts/300-target-contract/060-interruption-contract.adoc:1-44`
- Interruption assertions: `parts/400-conformance-assertions/050-interruption-assertions.adoc:1-80`
- Server event interruption/error boundaries: `parts/300-target-contract/040-server-event-contract.adoc:13-22`, `33-47`, `65-70`
- Response, local audio, turn, transcript, and error state: `parts/300-target-contract/050-state-model.adoc:36-63`, `75-80`
- Structured error subset: `parts/300-target-contract/080-error-contract.adoc:6-18`
- Core carriers for local flush: `parts/200-current-system/040-vision-agents-core-carriers.adoc:6-27`
- Test evidence: `parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`

Batch 05 authoritative sections:

- Tools/search/usage contract: `parts/300-target-contract/070-tools-search-usage-contract.adoc:1-41`
- Function-call server events: `parts/300-target-contract/040-server-event-contract.adoc:49-64`
- Tool/search/usage state: `parts/300-target-contract/050-state-model.adoc:64-73`
- Tool error contract: `parts/300-target-contract/080-error-contract.adoc:27-32`
- Tools/search/usage assertions: `parts/400-conformance-assertions/070-tools-search-usage-assertions.adoc:1-80`
- Coverage map: `parts/400-conformance-assertions/100-coverage-map.adoc:34-40`
- Function registry carrier: `parts/200-current-system/040-vision-agents-core-carriers.adoc:29-36`
- Test evidence: `parts/500-evidence-governance/010-test-evidence-contract.adoc:13-34`

Current baseline facts:

- `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py` maps Qwen response lifecycle, audio done, transcript done, and usage state after Batch 03.
- `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py` implements Batch 04 interruption, local flush, stale response isolation, and cancel-error projection.
- `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py` still lacks Qwen `response.function_call_arguments.delta/done` execution through the Vision Agents registry.
- `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py` converts constructor-supplied tools to Qwen function schema, but registry tools are not yet included in session config at the Batch 05 starting point.
- `plugins/qwen/vision_agents/plugins/qwen/client.py` has the `response.cancel` sender needed by Batch 04.
- `plugins/qwen/vision_agents/plugins/qwen/client.py` has `conversation.item.create(function_call_output)` and `response.create` senders needed by Batch 05.
- `agents-core/vision_agents/core/llm/realtime.py` already exposes `RealtimeAudioOutputDone(interrupted=True)` and `RealtimeAgentSpeechEnded(interrupted=True)`.
- `agents-core/vision_agents/core/agents/inference/realtime_flow.py` already turns interrupted audio done into local `interrupt()` and downstream audio flush.
- `agents-core/vision_agents/core/llm/llm.py` owns `function_registry`, `get_available_functions()`, and `call_function(name, arguments)` for Batch 05 tool execution.

## Open Blockers

No blocker prevents Batch 04 dispatch.

Live API verification remains blocked unless an executor has valid API key, cost authorization, and service availability. This does not block fake WebSocket and static config tests.

## Coordinator Notes

Executor questions should be answered by pointing them to exact source lines in this state file, the handoff file, or the contract book. If the coordinator lacks an answer, a temporary reconnaissance subagent should be dispatched rather than letting the builder infer scope.
