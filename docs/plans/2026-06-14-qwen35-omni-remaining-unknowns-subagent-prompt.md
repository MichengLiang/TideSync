# Qwen3.5 Omni Realtime Remaining Unknowns Follow-up Subagent Prompt

## Task Identity

This is a follow-up research assignment for the same subagent that produced:

```text
/home/t103o/workbench/micheng-ts/projects/TideSync/docs/deep-research/03-Qwen35-Omni-Realtime-Vision-Agents-完整适配缺口调查报告.md
```

The task is to investigate the unknowns left by that report, using the newly provided Function Calling document and any authoritative online sources or local source files needed. The subagent must not implement code changes. The required output is a Chinese supplemental report saved under `docs/deep-research/`.

## Required Context

Read the previous report first:

```text
/home/t103o/workbench/micheng-ts/projects/TideSync/docs/deep-research/03-Qwen35-Omni-Realtime-Vision-Agents-完整适配缺口调查报告.md
```

Read the newly provided Function Calling document:

```text
/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen-Omni-Realtime 系列-全模态模型的工具调用.md
```

Use these existing local documents as the base API contract:

```text
/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime.md
/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md
```

Use these codebases only when needed to resolve a specific unknown:

```text
/home/t103o/workbench/external/Vision-Agents
/home/t103o/workbench/micheng-ts/projects/TideSync
/home/t103o/workbench/external/alibabacloud-bailian-speech-demo
```

Internet research is allowed. Prefer official Alibaba Cloud / Aliyun / DashScope / Model Studio / Qwen sources. Use public GitHub only for source code or repository metadata. Do not use random blog posts as authority for API behavior.

If live API verification is possible using already configured environment variables and can be performed without destructive side effects, it is allowed. Do not leak secrets. Do not run long or expensive tests. If a live test would require missing credentials, paid/white-listed endpoints, microphone/camera hardware, or unclear cost exposure, classify it as not verified and explain the blocker.

## Investigation Object

The object is:

```text
The unresolved API and runtime facts required to complete the Qwen3.5-Omni-Flash-Realtime adapter contract for Vision Agents.
```

The object is not:

```text
An implementation plan.
A code patch.
A product roadmap.
A speculative runtime architecture essay.
```

## Unknowns To Resolve

Investigate each item below and classify it as:

```text
resolved by local official doc
resolved by official online doc
resolved by local code
resolved by live API test
still unknown
not applicable
```

For every resolved item, provide evidence paths or URLs and line references where possible. For every still-unknown item, state the exact missing authority or live condition.

### U1. Audio Format Strings

Determine whether Qwen3.5 Omni Realtime accepts `pcm16` / `pcm24` in `session.update`, or whether official contract requires `pcm`.

Required distinctions:

- official documented value
- DashScope SDK enum behavior, if visible
- Vision Agents current value
- live API result, if safely testable

### U2. Input Audio Transcription Model

Determine whether `gummy-realtime-v1` remains valid for Qwen3.5 Omni Realtime, and whether `qwen3-asr-flash-realtime` is the documented target for Qwen3.5.

Required distinctions:

- official examples
- SDK examples
- Vision Agents default
- live API result, if safely testable

### U3. Function Calling Realtime Contract

Use the new local Function Calling document to extract the exact realtime tool calling contract.

Required extraction:

- session.update fields for tools
- tool schema shape
- tool choice fields, if any
- server event names for tool calls
- event payload fields
- client event names for tool results
- tool result payload shape
- incompatibility with search
- WebSocket/WebRTC protocol scope
- examples
- known limits

Then compare this contract to Vision Agents core and Qwen adapter surfaces.

### U4. Search Contract Details

Determine whether search config and `usage.plugins.search` are identical across WebSocket and WebRTC, or whether the official document only confirms WebSocket examples.

Extract exact fields and response usage shape.

### U5. Semantic VAD Event Ordering And Barge-in Behavior

Determine whether `semantic_vad` uses the same server event sequence as `server_vad`:

```text
input_audio_buffer.speech_started
input_audio_buffer.speech_stopped
input_audio_buffer.committed
response.created
...
```

Determine whether official docs describe semantic barge-in behavior beyond the `type` value.

Use live API only if safe.

### U6. Response Cancellation And Stale Delta Behavior

Determine whether official docs or examples describe events arriving after `response.cancel`.

Required answer:

- Does the server guarantee no more `response.audio.delta` after cancel?
- Is there a `response.cancelled` or equivalent event?
- Does `response.done` include status/details for cancelled responses?
- Does the adapter need response id / epoch filtering based on docs or only as runtime hardening?

### U7. Response Event Ordering

Determine documented ordering among:

```text
response.audio_transcript.done
response.audio.done
response.content_part.done
response.output_item.done
response.done
```

State whether the ordering is guaranteed, implied by examples, or unknown.

### U8. Qwen Native WebRTC Details

Determine from official docs:

- endpoint pattern
- SDP request/response contract
- DataChannel label(s)
- whether client sends `session.update` over DataChannel
- whether audio output is RTP only
- whether text events use `response.text.*` or `response.audio_transcript.*` in text+audio mode
- whether search/tool events are sent over the same DataChannel
- browser CORS or server-side SDP exchange constraints
- whitelist requirements

If endpoint is not available, do not attempt unsupported live WebRTC tests.

### U9. Voice Cloning And Voice Control Contract

Determine whether realtime voice cloning has concrete session fields in official docs. Determine whether voice control creates any server events or is only model behavior in natural language.

### U10. Error Contract

Determine whether official docs list Qwen realtime `error` event shape, error codes, or recoverability for:

- invalid audio format
- invalid transcription model
- append image before audio
- invalid tool schema
- tool result errors
- search/tool incompatibility
- session timeout
- WebRTC SDP failure

## Required Output

Write the supplemental report in Chinese at:

```text
/home/t103o/workbench/micheng-ts/projects/TideSync/docs/deep-research/04-Qwen35-Omni-Realtime-剩余未知项与工具调用补充调查报告.md
```

The report must be at least 3000 Chinese characters.

The report must include:

1. Executive conclusion.
2. Unknowns resolution table.
3. Function Calling contract extraction.
4. Search contract supplement.
5. VAD and cancellation supplement.
6. WebRTC supplement.
7. Voice cloning / voice control supplement.
8. Error contract supplement.
9. Impact on the Vision Agents adapter coverage matrix.
10. Still-unknown list with exact blockers.
11. Evidence list with file paths or official URLs.
12. A final section named `适配契约增量`, containing only object-level adapter requirements implied by resolved facts.

## Writing Constraints

Use object language. Separate fact, inference, and unknown.

Do not write a roadmap. Do not rank implementation order. Do not write code.

Avoid these phrases unless quoted from a source:

```text
最小闭环
短期
中期
长期
先修
后续再说
默认完整
不一定错
正确做法
建议路线
```

## Completion Criteria

The task is complete only when:

- The supplemental report file exists at the required path.
- Each U1-U10 item is classified.
- The Function Calling contract is extracted from the new local document or explicitly marked incomplete with evidence.
- Remaining unknowns identify exact blockers.
- The report separates facts from inferences.
- The report states how resolved facts change or refine the previous adapter coverage matrix.

## Final Message To Parent Agent

When finished, reply with:

- Report path.
- Character count estimate.
- U1-U10 classification summary.
- Newly resolved facts that change the prior coverage matrix.
- Still-unknown blockers.
- Files and online sources inspected.
