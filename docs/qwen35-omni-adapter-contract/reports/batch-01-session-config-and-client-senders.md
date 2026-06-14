# Batch 01 Report: Session Config And Client Senders

Branch: `feature/qwen35-session-config-contract`

Implementation commit SHA: `c64b067`.

## Files Changed

- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`
- `forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py`
- `forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- `docs/qwen35-omni-adapter-contract/reports/batch-01-session-config-and-client-senders.md`
- `docs/qwen35-omni-adapter-contract/pr-bodies/batch-01-session-config-and-client-senders.md`

## Contract IDs Covered

- `source-and-runtime-contract`
- `runtime-import-contract`
- `dependency-contract`
- `session-config-contract`
- `model-region-contract`
- `modalities-voice-instructions-contract`
- `audio-format-contract`
- `input-transcription-contract`
- `turn-detection-contract`
- `tools-search-config-contract`
- `client-event-contract`
- `client-event-set`
- `tool-result-events-contract`
- `static-config-tests`
- `fake-websocket-tests`
- `runtime-path-tests`

## Assertion Results

`runtime-imports-controlled-adapter`: PASS.

Evidence: `uv run pytest tests/test_vision_agents_runtime_path.py` passed and asserts `vision_agents.core`, `vision_agents.plugins.qwen`, `vision_agents.plugins.qwen.qwen_realtime`, and `vision_agents.plugins.getstream` load from `forks/vision-agents-qwen-native`.

`dependency-resolution-reproducible`: PASS for this batch baseline.

Evidence: the runtime path test passed using the root `uv` environment and existing editable sources in `pyproject.toml`. This batch did not change dependency resolution.

`session-update-uses-qwen35-contract-values`: PASS.

Evidence: `test_session_update_uses_qwen35_contract_defaults` captures the fake client `session.update` and asserts model/base URL pass-through, `modalities: ["text", "audio"]`, voice, instructions, `input_audio_format: "pcm"`, `output_audio_format: "pcm"`, `input_audio_transcription.model: "qwen3-asr-flash-realtime"`, and default `server_vad` parameters.

`semantic-vad-configurable`: PASS.

Evidence: `test_semantic_vad_is_visible_in_session_update` constructs `Realtime(turn_detection="semantic_vad")` and asserts the captured session config sends `turn_detection.type: "semantic_vad"`.

`manual-mode-configurable`: PASS for Batch 01 sender/config scope.

Evidence: `test_manual_mode_sends_null_turn_detection_and_response_create` constructs `Realtime(turn_detection=None)`, captures `turn_detection: None`, and verifies the adapter can send `input_audio_buffer.commit` followed by `response.create` through the fake client.

`tools-search-mutually-exclusive`: PASS.

Evidence: `test_tools_and_search_are_rejected_before_session_update` constructs a config with tools and `enable_search=True`, asserts `ValueError`, and asserts no fake client/session update was created. `test_tools_and_search_config_payloads_do_not_include_unsupported_fields` also covers legal tools/search payloads and asserts no `tool_choice` or `parallel_tool_calls` fields are sent.

## Test Commands And Output Summary

Red test run before implementation:

- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py -q`
- Result before implementation: `5 failed, 2 skipped`.
- Expected failures: legacy `pcm16`/`pcm24` and `gummy-realtime-v1` defaults, missing `turn_detection`, missing `tools`, missing `clear_audio`, missing Manual response helper.

Final verification:

- `uv run pytest tests/test_vision_agents_runtime_path.py`
- Result: `1 passed`.
- Note: pytest-cov emitted warnings that `tidesync` was not imported and no coverage data was collected. The command still passed; these warnings are caused by root coverage settings on a narrow import-path test.

- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`
- Result: `6 passed, 2 skipped`.
- Note: pytest-cov emitted the same no-data warning because the command targets plugin tests outside the `tidesync` coverage package. The two skipped tests are the pre-existing live integration tests.

- `uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- Result: `All checks passed!`

- `uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py`
- Result: `3 files already formatted`.

## Known Unknowns And Live Verification Blockers

- Live Qwen service compatibility for legacy `gummy-realtime-v1`, `pcm16`, and `pcm24` was not verified. This batch intentionally uses the Qwen3.5 contract values instead of treating legacy examples as defaults.
- Live Qwen acceptance of `qwen3-asr-flash-realtime`, `semantic_vad`, Manual `turn_detection: null`, tools payloads, and search options was not verified because no valid API key, cost authorization, or service availability was provided to this executor.
- The fake tests prove outbound adapter/client payloads. They do not prove full server event replay, interruption behavior, tool execution lifecycle, search usage parsing, or reconnect state reset.
- Before this batch branch was created, the TideSync worktree was clean but local `main` and `forks/vision-agents-qwen-native` both reported `main...origin/main [ahead 1]`. No unrelated files were dirty, and this batch preserved that existing local history.

## Explicit Non-Goals Left For Future Batches

- Full server event mapping for speech, transcript, audio done, response done, and usage.
- Input turn state, video send-permission state, and image timing enforcement beyond the existing pre-audio guard.
- Interruption state machine, local audio flush, stale response isolation, and cancel error behavior.
- Tool execution flow, search usage capture, structured tool errors, and structured Qwen error model.
- Reconnect state reset.
- Live API smoke evidence.
