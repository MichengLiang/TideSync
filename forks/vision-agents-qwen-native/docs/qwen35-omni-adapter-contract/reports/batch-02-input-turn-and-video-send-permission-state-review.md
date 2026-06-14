# Batch 02 Review: Input Turn And Video Send-Permission State

Review verdict: `APPROVED_WITH_NOTES`

Reviewed commit SHA: `8b5423c69f0c67f6414dabb18f0579f4c0951c4e`

Implementation commit SHA reviewed: `e6c9fb9`

Review branch: `feature/qwen35-input-turn-video-state`

## Contract Coverage Table

| Review item | Result | Evidence |
|---|---|---|
| Branch and reviewed HEAD | PASS | `git rev-parse HEAD` returned `8b5423c69f0c67f6414dabb18f0579f4c0951c4e`; branch is `feature/qwen35-input-turn-video-state`. |
| Batch 02 scope | PASS | Implementation commit `e6c9fb9` touches only `qwen_realtime.py`, Qwen tests, and Batch 02 report/PR body; final commit `8b5423c` updates the report commit field. No broad interruption, response lifecycle, usage, tools, search, reconnect, dependency, or root TideSync churn was observed. |
| Required builder report path | PASS | `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md` exists and contains branch, commit, files, contract IDs, assertion results, commands, blockers, and non-goals. |
| Required PR body draft path | PASS | `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-02-input-turn-and-video-send-permission-state.md` exists and contains summary, scope, rationale, coverage, verification, live blockers, and rollback impact. |
| `_audio_emitted_once` no longer sole video gate | PASS | No `_audio_emitted_once` references remain under the Qwen plugin; `qwen_realtime.py:53-92,141,287-297` uses `QwenInputTurnState.can_send_image()`. |
| Current-turn audio append opens image sending | PASS | `qwen_realtime.py:58-60,227-232`; covered by `test_video_frame_sent_after_current_turn_audio` at `test_qwen_realtime.py:252-272`. |
| No image before current-turn audio | PASS | `qwen_realtime.py:287-297`; covered by `test_video_frame_not_sent_before_current_turn_audio` at `test_qwen_realtime.py:234-249`. |
| `speech_stopped` closes image sending and projects state | PASS | `qwen_realtime.py:66-68,381-383`; covered by `test_speech_events_update_turn_and_close_image_window` at `test_qwen_realtime.py:275-307`, including `RealtimeUserSpeechStarted`/`RealtimeUserSpeechEnded` projection. |
| Manual commit closes current-turn image sending | PASS_WITH_NOTE | `qwen_realtime.py:70-72,218-221`; covered by `test_manual_commit_and_clear_close_image_window` at `test_qwen_realtime.py:310-348`. Note: the projection uses `committed`, not a distinct `waiting_response` state from the broader state model. |
| Manual clear closes current-turn image sending | PASS | `qwen_realtime.py:74-76,223-225`; covered by `test_manual_commit_and_clear_close_image_window` at `test_qwen_realtime.py:310-348`. |
| Server `input_audio_buffer.committed` closes image sending | PASS | `qwen_realtime.py:384-385`; covered by `test_input_audio_buffer_committed_event_closes_image_window` at `test_qwen_realtime.py:351-373`. |
| Track removal/reconnect forces next track to wait for current-turn audio | PASS | `qwen_realtime.py:78-83,316-324`; covered by `test_track_reconnect_waits_for_current_turn_audio` at `test_qwen_realtime.py:376-403`. |
| Image timing error suspends sending until new valid audio turn | PASS | `qwen_realtime.py:85-89,350-360,412-417`; covered by `test_image_timing_error_suspends_until_new_audio_turn` at `test_qwen_realtime.py:406-443`. |
| Fake tests do not contact live Qwen service | PASS | Tests use `FakeQwenClient`/`FakeWebSocket` at `test_qwen_realtime.py:26-94,76-81`; live integration tests remain skipped at `test_qwen_realtime.py:474-535`. |
| Runtime import path test | PASS | Fresh reviewer run: `uv run pytest tests/test_vision_agents_runtime_path.py` -> `1 passed` with known coverage no-data warnings. |
| Ruff on touched Python files | PASS | Fresh reviewer runs: `ruff check` passed and `ruff format --check` reported `3 files already formatted`. |

## Findings

No blocking findings.

### Note: Batch 02 commit projection does not distinguish `waiting_response`

The state model source includes `waiting_response` in the input audio state collection (`docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/300-target-contract/050-state-model.adoc:22-27`). Batch 02 implementation projects Manual/server commit as `committed` (`qwen_realtime.py:70-72,384-385`; tests at `test_qwen_realtime.py:341-343,370-372`).

I am not treating this as a blocker for this batch because the review package focuses on the Batch 02 image-permission effect: commit must close the current-turn image window, and the tests prove that behavior. The coordinator may still choose to require a distinct `waiting_response` projection in a later response-lifecycle batch.

### Note: Video permission tests call provider hooks directly

The report records that tests call provider internals directly and do not exercise the real `VideoForwarder` timing loop (`batch-02-input-turn-and-video-send-permission-state.md:80-84`). This is acceptable for Batch 02 fake/event evidence because the review package requires deterministic fake tests, and the gating function itself is covered. A future integration or replay test should cover the real forwarder loop if video timing regressions continue.

## Test Evidence Reviewed

Fresh reviewer commands run from `/home/t103o/workbench/micheng-ts/projects/TideSync`:

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Warnings: coverage reported `Module tidesync was never imported` and `No data was collected` for this narrow import-path test.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `13 passed, 2 skipped`.
  - Warnings: same coverage no-data warnings; skipped tests are the existing live integration tests.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `3 files already formatted`.

Additional review checks:

- `git show --name-status --oneline --no-renames e6c9fb9` confirmed the implementation commit touches only Batch 02 runtime, tests, report, and PR body files.
- `git diff --check ce6ceaf..8b5423c` produced no whitespace errors.
- `rg "_audio_emitted_once"` under `forks/vision-agents-qwen-native/plugins/qwen` found no remaining historical gate references.

## Missing Evidence

None for Batch 02 review promotion.

Live Qwen service behavior for image timing error payload variants, speech/commit event ordering, and track reconnect remains unverified and is recorded as blocked by missing API key, cost authorization, or service availability. The review package permits this because Batch 02 relies on fake/event replay evidence.

## Coordinator Promotion Recommendation

Promote Batch 02 from review.

The implementation replaces historical audio gating with a single test-visible input-turn/video-permission state object, closes or suspends image sending on the required Batch 02 events, preserves the future-batch boundaries, and passes the required verification commands on reviewed HEAD `8b5423c69f0c67f6414dabb18f0579f4c0951c4e`.
