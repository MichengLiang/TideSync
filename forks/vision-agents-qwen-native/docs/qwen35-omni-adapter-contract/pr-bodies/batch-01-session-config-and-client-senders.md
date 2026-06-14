## Summary

This PR implements Batch 01 of the Qwen3.5 Omni Realtime WebSocket adapter contract: session configuration and closed client event senders.

The Qwen adapter now builds a single explicit `session.update.session` payload for the Qwen3.5 contract defaults, exposes `semantic_vad` and WebSocket Manual mode, rejects tools/search mutual exclusion before any session update is sent, and adds the missing client senders for audio clear, function call output, and response creation.

Review fix: the report and PR body draft now live under the fork work-area evidence paths, the misplaced root evidence copies were removed, and Manual-mode fake evidence now includes audio append before commit and response create.

## Scope

- `plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
  - Sets Qwen3.5 contract defaults for model, DashScope base URL, voice, audio formats, and input transcription model.
  - Centralizes session config construction.
  - Supports `server_vad`, `semantic_vad`, and Manual `turn_detection: None`.
  - Adds tools/search config payload handling and mutual exclusion.
  - Adds a Manual-mode helper that sends commit plus response create.
- `plugins/qwen/vision_agents/plugins/qwen/client.py`
  - Keeps existing senders.
  - Adds `input_audio_buffer.clear`, `conversation.item.create` for `function_call_output`, and `response.create`.
- `plugins/qwen/tests/test_qwen_realtime.py`
  - Adds fake-client/static tests for session update payloads.
  - Covers Manual mode with audio append before commit and response create.
  - Adds fake WebSocket sender tests for the new client event methods.
  - Leaves existing live integration tests skipped.
- `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`
  - Records batch evidence, assertion results, known unknowns, and non-goals.
- `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders-review.md`
  - Records the independent review result for final reviewed HEAD `c183713`.
- `docs/qwen35-omni-adapter-contract/coordinator-state.md`
  - Records the coordinator promotion decision and next batch boundary.

## Repository Rationale

The changed files are inside the controlled `vision-agents-qwen-native` fork that TideSync runtime loads through local editable dependencies. This adapter owns the WebSocket session configuration and client event payloads; TideSync outer agent code can pass high-level settings, but cannot repair provider-level Qwen payloads or sender coverage.

This PR belongs in the controlled fork because the 09 contract requires Qwen adapter behavior to be reviewable in the TideSync PR diff and covered by repeatable fake/static evidence.

## Contract Coverage

- `runtime-imports-controlled-adapter`: covered by `tests/test_vision_agents_runtime_path.py`.
- `dependency-resolution-reproducible`: covered by existing editable dependency resolution plus runtime path test.
- `session-update-uses-qwen35-contract-values`: covered by fake-client session update capture.
- `semantic-vad-configurable`: covered by fake-client session update capture.
- `manual-mode-configurable`: covered by `turn_detection: None` plus fake audio append, commit, and response create sender evidence.
- `tools-search-mutually-exclusive`: covered by a negative fake-client test that asserts no illegal session update is sent.
- Client event set slice: covered for `input_audio_buffer.clear`, `conversation.item.create` with `function_call_output`, and `response.create`.

## Verification

- `uv run pytest tests/test_vision_agents_runtime_path.py`
  - Result: `1 passed`.
  - Note: root pytest coverage settings emitted no-data warnings because the narrow test did not import `tidesync`.
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
  - Result: `6 passed, 2 skipped`.
  - Note: the skipped tests are the existing live integration tests; coverage emitted the same no-data warning because plugin tests are outside the configured `tidesync` coverage package.
- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `All checks passed!`
- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
  - Result: `3 files already formatted`.
- Independent review:
  - Result: `APPROVED_WITH_NOTES`.
  - Report: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders-review.md`.

## Live Verification / Blockers

Live API smoke was not run. No valid API key, cost authorization, or live service availability was provided to this executor.

The following remain live compatibility unknowns:

- Whether Qwen still tolerates old `gummy-realtime-v1`, `pcm16`, or `pcm24` examples.
- Whether the live service accepts `qwen3-asr-flash-realtime`, `semantic_vad`, Manual `turn_detection: null`, tools payloads, and search options exactly as fake/static tests construct them.

## Rollback Impact

Rolling this PR back returns the controlled Qwen adapter to the prior upstream-like behavior: `pcm16`/`pcm24`, `gummy-realtime-v1`, fixed `server_vad`, no adapter-level tools/search mutual exclusion, and no client senders for audio clear, function call output, or response create.

That rollback would reopen Batch 01 contract gaps and leave Manual mode and tool-result response continuation without client event support.
