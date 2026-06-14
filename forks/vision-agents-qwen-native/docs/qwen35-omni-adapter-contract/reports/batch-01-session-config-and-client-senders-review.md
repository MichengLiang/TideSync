# Batch 01 Review: Session Config And Client Senders

Review verdict: `APPROVED_WITH_NOTES`

Reviewed commit SHA: `c183713df471e074f0adcf26a87eef0ed9535e73`

Review branch: `feature/qwen35-session-config-contract`

Prior review: `CHANGES_REQUIRED` at `a9c203eac39a40060bf2bf868dc698f4f384d46e`

## Contract Coverage Table

| Review item | Result | Evidence |
|---|---|---|
| Branch and reviewed HEAD | PASS | `git rev-parse HEAD` returned `c183713df471e074f0adcf26a87eef0ed9535e73`; branch is `feature/qwen35-session-config-contract`. |
| Prior finding: builder report path | PASS | Report now exists at `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`; root misplaced report copy was removed. |
| Prior finding: PR body draft path | PASS | PR body draft now exists at `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-01-session-config-and-client-senders.md`; root misplaced PR body copy was removed. |
| Prior finding: Manual-mode fake evidence | PASS | `test_manual_mode_sends_null_turn_detection_and_response_create` now sends fake audio before commit/response create and asserts `session.update`, `input_audio_buffer.append`, `input_audio_buffer.commit`, `response.create`. |
| Batch 01 scope | PASS | Fix commit moves evidence files and updates the Qwen test only; no broad state-machine, event mapping, dependency, or unrelated runtime churn was observed. |
| `session.update.session` required fields and `pcm` defaults | PASS | `qwen_realtime.py:107-128`; `test_qwen_realtime.py:72-103`. |
| Input transcription no longer silently defaults to `gummy-realtime-v1` | PASS | `qwen_realtime.py:23-25,45,117-119`; `test_qwen_realtime.py:93-95`. |
| `server_vad`, `semantic_vad`, Manual `turn_detection: null` representable and tested | PASS | `qwen_realtime.py:46-49,80-84,130-140`; `test_qwen_realtime.py:72-138`. |
| Tools/search mutual exclusion before illegal session update | PASS | `qwen_realtime.py:107-109`; `test_qwen_realtime.py:141-154`. |
| Unsupported `tool_choice` and `parallel_tool_calls` not sent | PASS | `qwen_realtime.py:111-128,142-154`; `test_qwen_realtime.py:157-206`. |
| Client senders for clear, function output, response create | PASS | `client.py:103-106,129-144`; `test_qwen_realtime.py:209-234`. |
| Fake/static tests avoid live Qwen service | PASS | Tests use fake client or fake websocket; live integration tests remain skipped. |
| Runtime import path test | PASS | Fresh reviewer run: `uv run pytest tests/test_vision_agents_runtime_path.py` -> `1 passed` with coverage no-data warnings. |
| Builder report and PR body evidence fields | PASS_WITH_NOTE | Fork-path report and PR body contain scope, coverage, verification, blockers, rollback/non-goals. Note: the builder report labels `c64b067` as the implementation commit while this re-review target and final HEAD are `c183713`. |

## Findings

No blocking findings remain.

### Note: Builder report commit label still names the implementation commit

The fork-path builder report records `Implementation commit SHA: c64b067` at `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md:3-6`. This re-review target is final HEAD `c183713df471e074f0adcf26a87eef0ed9535e73`, and the report also records the review-fix evidence at line 36.

I am not treating this as a blocker because the review report records the reviewed final HEAD, and the builder report distinguishes the original implementation commit from the later evidence-fix commit. The coordinator may still ask the builder to add a separate final HEAD field before promotion if stricter traceability is desired.

## Test Evidence Reviewed

Fresh reviewer commands run from `/home/t103o/workbench/micheng-ts/projects/TideSync`:

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Warnings: coverage reported `Module tidesync was never imported` and `No data was collected` for this narrow import-path test.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `6 passed, 2 skipped`.
  - Warnings: same coverage no-data warnings; skipped tests are the existing live integration tests.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `3 files already formatted`.

Additional review checks:

- `git show --name-status --oneline --no-renames c183713` confirmed the fix commit moved the report and PR body from root `docs/` into fork work-area paths and modified only `test_qwen_realtime.py` for Manual-mode evidence.
- Artifact existence checks confirmed the fork work-area report and PR body draft paths exist and the prior root `docs/` copies are absent from the worktree.
- `git diff --check a9c203e..c183713` produced no whitespace errors.

## Missing Evidence

None for Batch 01 review promotion.

Live Qwen service smoke remains unrun and recorded as blocked by missing API key, cost authorization, or service availability. The review package allows this blocker because fake/static evidence is the core Batch 01 requirement.

## Coordinator Promotion Recommendation

Promote Batch 01 from review, subject to coordinator acceptance of the non-blocking commit-label note above.

The two prior `CHANGES_REQUIRED` findings are fixed: evidence artifacts now live under the fork work-area paths, and Manual-mode fake evidence includes audio append before commit and response create. Quick regression against the original review package did not find a new blocker.
