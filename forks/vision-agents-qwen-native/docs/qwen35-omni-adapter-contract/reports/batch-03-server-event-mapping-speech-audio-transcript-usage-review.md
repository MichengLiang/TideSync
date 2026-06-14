# Batch 03 Review: Server Event Mapping For Audio Transcript And Usage

Review verdict: `APPROVED_WITH_NOTES`

Reviewed commit SHA: `223cc1304ddb6201a46908d1886f7fbf24aefb92`

Implementation commit SHA reviewed: `2f5896d`

Review branch: `feature/qwen35-server-event-mapping`

## Contract Coverage Table

| Review item | Result | Evidence |
|---|---|---|
| Branch and reviewed HEAD | PASS | `git rev-parse HEAD` returned `223cc1304ddb6201a46908d1886f7fbf24aefb92`; branch is `feature/qwen35-server-event-mapping`. |
| Batch 03 scope | PASS | Implementation commit `2f5896d` touches only `qwen_realtime.py`, Qwen tests, and Batch 03 report/PR body; final commit `223cc13` updates the report commit field. No Batch 04 stale/cancel isolation, Batch 05 tool execution, structured error/reconnect work, client churn, root dependency churn, or TideSync outer runtime changes were observed. |
| Required builder report path | PASS | `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage.md` exists and contains branch, commit, files, contract IDs, assertion results, lifecycle summary, commands, blockers, and non-goals. |
| Required PR body draft path | PASS | `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/pr-bodies/batch-03-server-event-mapping-speech-audio-transcript-usage.md` exists and contains summary, scope, rationale, coverage, verification, live blockers, and rollback impact. |
| `response.audio.delta` emits audio output | PASS | `qwen_realtime.py:570-577`; covered by `test_response_audio_delta_and_done_emit_output_boundary` at `test_qwen_realtime.py:456-489`, including 24 kHz PCM and `response_id="resp_1"`. |
| `response.audio.done` emits done boundary | PASS | `qwen_realtime.py:578-583`; covered by `test_response_audio_delta_and_done_emit_output_boundary` at `test_qwen_realtime.py:456-489`, including `RealtimeAudioOutputDone(interrupted=False, response_id="resp_1")`. |
| `response.audio_transcript.delta` emits assistant delta | PASS | `qwen_realtime.py:585-591`; covered by `test_audio_transcript_delta_and_done_emit_non_empty_final` at `test_qwen_realtime.py:492-519`. |
| `response.audio_transcript.done` emits assistant final | PASS | `qwen_realtime.py:593-602`; covered by server transcript and accumulated-delta fallback tests at `test_qwen_realtime.py:492-543`. |
| `response.done` no longer emits empty assistant final | PASS | `qwen_realtime.py:555-568`; covered by `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final` at `test_qwen_realtime.py:546-585`. |
| `response.done.usage` raw and token fields retained | PASS | `qwen_realtime.py:610-628`; covered by `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final` at `test_qwen_realtime.py:546-585`. |
| `usage.plugins.search` retained | PASS | `qwen_realtime.py:620-628`; covered by `test_response_done_parses_usage_and_does_not_emit_empty_transcript_final` at `test_qwen_realtime.py:552-585`. |
| Usage parse failure preserves raw payload | PASS | `qwen_realtime.py:610-628,661-676`; covered by `test_response_done_usage_parse_failure_retains_raw_payload` at `test_qwen_realtime.py:588-613`. |
| Response lifecycle projection | PASS_WITH_NOTE | `qwen_realtime.py:523-568`; covered by `test_response_lifecycle_events_update_state_projection` at `test_qwen_realtime.py:616-672`. See note below about response.done without audio.done. |
| User transcript delta/completed mapping | PASS | `qwen_realtime.py:508-517`; covered by `test_user_input_audio_transcription_delta_and_completed_emit_transcripts` at `test_qwen_realtime.py:675-700`. |
| Fake/event replay tests avoid live Qwen service | PASS | Tests use `FakeQwenClient` and server event lists; existing live integration tests remain skipped at `test_qwen_realtime.py:731-792`. |
| Runtime import path test | PASS | Fresh reviewer run: `uv run pytest tests/test_vision_agents_runtime_path.py` -> `1 passed` with known coverage no-data warnings. |
| Ruff on touched Python files | PASS | Fresh reviewer runs: `ruff check` passed and `ruff format --check` reported `2 files already formatted`. |

## Findings

No blocking findings.

### Note: Usage/search projection is adapter-private for this batch

The implementation retains raw usage, parsed token fields, parse failure, and `plugins.search` in `_qwen_usage_snapshot()` (`qwen_realtime.py:347-349,610-628`) and documents that current Vision Agents core has no obvious public carrier for the full raw provider usage structure (`batch-03-server-event-mapping-speech-audio-transcript-usage.md:50-52,85-89`). This satisfies the Batch 03 review package because it requires a test-visible projection, but later metrics/cost-governance work should decide whether this projection needs a public core event or metrics surface.

### Note: `response.done` closes response state but does not emit agent speech ended unless `response.audio.done` arrived

`response.created` emits `RealtimeAgentSpeechStarted` through `_ensure_agent_speech_started()` (`qwen_realtime.py:523-528,604-608`). `response.audio.done` emits `RealtimeAgentSpeechEnded` (`qwen_realtime.py:578-583`), but `response.done` itself only marks the response completed and clears response ids (`qwen_realtime.py:555-568`). The Batch 03 lifecycle test covers the state projection, not an agent-turn-ended core event for a response that reaches `response.done` without `response.audio.done` (`test_qwen_realtime.py:616-672`).

I am not treating this as a blocker because the review package specifically requires audio done to emit the audio/agent boundary and response.done to update lifecycle/usage state without pretending to solve stale/cancel isolation. A future response lifecycle or interruption batch may still want to define the exact agent-turn closure behavior for no-audio-done responses.

## Test Evidence Reviewed

Fresh reviewer commands run from `/home/t103o/workbench/micheng-ts/projects/TideSync`:

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Warnings: coverage reported `Module tidesync was never imported` and `No data was collected` for this narrow import-path test.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `20 passed, 2 skipped`.
  - Warnings: same coverage no-data warnings; skipped tests are the existing live integration tests.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `2 files already formatted`.

Additional review checks:

- `git show --name-status --oneline --no-renames 2f5896d` confirmed the implementation commit touches only Batch 03 runtime, tests, report, and PR body files.
- `git diff --check 80efbe4..223cc13` produced no whitespace errors.
- Targeted search found no Batch 04 stale/cancel isolation implementation or Batch 05 function-call execution implementation introduced by this batch.

## Missing Evidence

None for Batch 03 review promotion.

Live Qwen service behavior for exact `response.audio_transcript.done` payload variants and usage plugin field variants remains unverified and is recorded as blocked by missing API key, cost authorization, or service availability. The review package permits this because replay/fake evidence is the required Batch 03 evidence surface.

## Coordinator Promotion Recommendation

Promote Batch 03 from review.

The implementation maps the required Batch 03 server events, removes the empty-final `response.done` substitute, retains usage/search usage in test-visible projections, preserves future-batch boundaries, and passes the required verification commands on reviewed HEAD `223cc1304ddb6201a46908d1886f7fbf24aefb92`.
