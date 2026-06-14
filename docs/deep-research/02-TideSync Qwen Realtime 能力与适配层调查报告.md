# TideSync Qwen Realtime 能力与适配层调查报告

先给结论：你现在看到的两个核心问题，主要不是 Qwen3.5-Omni-Flash-Realtime 这个基座模型不支持，也不是 Stream / WSL 天然做不到，而是 **`vision-agents` 0.6.4 的 Qwen Realtime 适配层没有把 Qwen 服务端事件完整映射到 Vision Agents 的 realtime pipeline**。模型/API 本身支持流式音频、流式文本、服务端 VAD、语音打断、音视频输入；当前 TideSync 使用的 SDK/插件只接上了其中一部分能力。尤其是打断：官方示例会在 `input_audio_buffer.speech_started` 到来时立刻清本地播放器，而当前插件只尝试给 Qwen 发 `response.cancel`，没有同步清掉本地 WebRTC 音频输出缓冲，因此体验上不像 OpenAI Voice / Gemini Live 那种“我一说话，它马上停”。

下面分层说明。

## 1. 当前系统里有三层对象

这套东西不能只说“模型在干什么”。实际有三层：

第一层是 Qwen3.5-Omni-Flash-Realtime 模型和 DashScope Realtime WebSocket API。它承担语音识别、VAD、对话生成、视觉理解、语音合成、流式事件输出、打断响应等能力。

第二层是 `vision-agents` 的 Qwen 插件：

```text
.venv/lib/python3.13/site-packages/vision_agents/plugins/qwen/qwen_realtime.py
.venv/lib/python3.13/site-packages/vision_agents/plugins/qwen/client.py
```

它负责把 Stream call 收到的 PCM 音频和视频帧转换成 Qwen Realtime WebSocket 事件，也负责把 Qwen 返回的事件转换成 Vision Agents 内部的 `RealtimeAudioOutput`、`RealtimeAgentTranscript` 等事件。

第三层是 Vision Agents + GetStream 边缘层：

```text
.venv/lib/python3.13/site-packages/vision_agents/core/agents/inference/realtime_flow.py
.venv/lib/python3.13/site-packages/vision_agents/core/agents/agents.py
.venv/lib/python3.13/site-packages/vision_agents/plugins/getstream/stream_edge_transport.py
```

它负责 WebRTC call 的音频输入、音频输出、视频 track 监听、字幕/聊天消息同步、agent runner 生命周期、浏览器 demo URL 等。

你现在的体验问题发生在第二层和第三层的交界处：Qwen 服务端已经输出了足够多的事件，但插件没有把这些事件完整投射到 Vision Agents 的打断/播放/结束语义里。

## 2. Qwen 模型/API 本身支持什么

根据项目内已经保存的控制台文档 `docs/Qwen3.5-Omni-Flash-Realtime.md`，Qwen3.5-Omni-Flash-Realtime 是实时全模态模型，支持文本、图片、视频、音频输入，支持文本、图片、视频、音频输出。文档也写到 Qwen3.5-Omni 支持可控语音对话、语义打断、语音输出、多语言音频输入/输出等能力。

官方 Realtime 文档还说明了几个关键事件：

- `response.audio.delta`：模型增量生成新的音频数据时，服务端返回这个事件。
- `response.audio.done`：音频数据生成完成。
- `response.done`：响应生成完成。
- `response.audio_transcript.delta`：模型语音输出对应的文本 transcript 增量。
- `conversation.item.input_audio_transcription.completed`：用户输入音频转写完成。
- `input_audio_buffer.speech_started`：服务端 VAD 检测到用户开始说话。
- `input_audio_buffer.speech_stopped`：服务端 VAD 检测到用户停止说话。
- `response.cancel`：客户端取消正在进行的响应。
- `input_image_buffer.append`：客户端追加图像帧。

官方文档地址：

```text
https://help.aliyun.com/zh/model-studio/realtime
https://help.aliyun.com/zh/model-studio/client-events
https://help.aliyun.com/zh/model-studio/server-events
```

我还克隆了阿里官方示例仓库：

```text
/home/t103o/workbench/external/alibabacloud-bailian-speech-demo
https://github.com/aliyun/alibabacloud-bailian-speech-demo
```

官方示例 `samples/conversation/omni/README_EN.md` 明确写了 Qwen-Omni realtime API 支持低延迟多模态交互、流式输入音视频、流式输出文本和音频，并支持 voice interruption。

所以第一层结论是：**基座模型/API 不只是普通“语音转文字再生成再播报”的串行模型，它本身就是 realtime multimodal API，并支持流式输出和打断。**

## 3. 当前 TideSync 让模型承担了哪些职责

TideSync 当前 `src/tidesync/agent.py` 创建的是：

```python
llm = qwen.Realtime(
    model=settings.model,
    base_url=settings.base_url,
    voice=settings.voice,
    fps=settings.fps,
    include_video=True,
)
```

因为 `llm` 是 `Realtime` 类型，Vision Agents 会进入 realtime mode。`Agent._validate_configuration()` 里明确写了：如果是 realtime LLM，则 STT、TTS、Turn Detection 服务会被禁用，因为 realtime 模型内部处理 speech-to-text、text-to-speech 和 turn detection。

这意味着当前架构下：

- 用户语音识别：Qwen 负责。
- 用户说话开始/结束检测：Qwen server VAD 负责。
- 对话生成：Qwen 负责。
- 助手语音合成：Qwen 负责。
- 助手语音转写文本：Qwen 通过 `response.audio_transcript.*` 负责。
- 视觉理解：Qwen 负责，但前提是程序正确向它发送图像帧。
- 语义打断判断：Qwen 服务端能力负责一部分。
- 本地播放缓冲清理：程序必须负责。
- WebRTC 里的音频播放、字幕同步、消息显示：Vision Agents / GetStream 负责。

所以不要把“打断”理解成单点能力。打断至少有两个动作：

1. 远端停止继续生成：发 `response.cancel` 或让服务端依据 VAD/语义打断停止响应。
2. 本地已经排队的音频立刻停止播放：清掉本地播放器 / WebRTC audio track buffer。

OpenAI Voice / Gemini Live 的体感好，是因为这两个动作被做成一个用户可感知的整体。当前 TideSync 只部分做了第一个动作，第二个动作没有被可靠触发。

## 4. 当前 Qwen 插件实际接了哪些事件

当前插件文件：

```text
.venv/lib/python3.13/site-packages/vision_agents/plugins/qwen/qwen_realtime.py
```

它在 `connect()` 里发送 session 配置：

```python
session_config = {
    "modalities": ["text", "audio"],
    "voice": self.voice,
    "instructions": self._instructions,
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm24",
    "input_audio_transcription": {"model": self._audio_transcription_model},
    "turn_detection": {
        "type": "server_vad",
        "threshold": self._vad_threshold,
        "prefix_padding_ms": self._vad_prefix_padding_ms,
        "silence_duration_ms": self._vad_silence_duration_ms,
    },
}
```

这说明它确实启用了服务端 VAD，且请求文本+音频输出。

它处理服务端事件的代码核心是：

```python
elif event_type == "response.created":
    self._current_response_id = event.get("response", {}).get("id")
    self._is_responding = True
elif event_type == "response.done":
    self._emit_agent_speech_transcription(text="", mode="final")
    self._is_responding = False
    self._current_response_id = None
    self._current_item_id = None
elif event_type == "input_audio_buffer.speech_started":
    if self._is_responding:
        await self._on_interruption()
elif event_type == "response.audio.delta":
    audio_bytes = base64.b64decode(event["delta"])
    pcm = PcmData.from_bytes(audio_bytes, 24000)
    self._emit_audio_output_event(pcm=pcm)
elif event_type == "conversation.item.input_audio_transcription.completed":
    transcript = event.get("transcript", "")
    if transcript:
        self._emit_user_speech_transcription(text=transcript, mode="final")
elif event_type == "response.audio_transcript.delta":
    delta = event.get("delta", "")
    if delta:
        self._emit_agent_speech_transcription(text=delta, mode="delta")
```

这里接了：

- `response.created`
- `response.done`
- `input_audio_buffer.speech_started`
- `response.audio.delta`
- `conversation.item.input_audio_transcription.completed`
- `response.audio_transcript.delta`

但它没有接或没有投射：

- 没有把 `input_audio_buffer.speech_started` 转成 Vision Agents 的 `RealtimeUserSpeechStarted`。
- 没有把 `input_audio_buffer.speech_stopped` 转成 `RealtimeUserSpeechEnded`。
- 没有把 `response.created` 或首个 audio delta 转成 `RealtimeAgentSpeechStarted`。
- 没有处理 `response.audio.done`。
- 没有在 `response.done` 时发 `RealtimeAudioOutputDone`。
- 没有在 `response.done` 时发 `RealtimeAgentSpeechEnded`。
- 没有在打断时发 `RealtimeAudioOutputDone(interrupted=True)`。
- 没有在打断时清本地 audio output stream。

这些缺口直接解释你看到的体感问题。

## 5. Vision Agents 框架本身有打断管线

框架层 `RealtimeInferenceFlow.interrupt()` 是有清缓冲能力的：

```python
async def interrupt(self):
    await self._llm.interrupt()
    self._transcripts.flush_agent_transcript()
    self._transcripts.flush_users_transcripts()
    self._audio_output.clear()
    await self._audio_output.flush()
```

`AudioOutputStream.flush()` 会发送 `AudioOutputFlush()`。`Agent._produce_audio_output()` 收到 flush 后会调用：

```python
await self._audio_track.flush()
```

`getstream.video.rtc.AudioStreamTrack.flush()` 会清掉内部 byte buffer，注释里写的是 playback stops immediately。

所以第三层不是完全没有能力。Vision Agents + GetStream 本地播放链路是可以清的。问题是 Qwen 插件没有把“用户开始说话时需要清本地播放”这个事件传给 `RealtimeInferenceFlow.interrupt()`。

框架只在收到 `RealtimeAudioOutputDone(interrupted=True)` 时会打日志并调用 `await self.interrupt()`：

```python
elif isinstance(item, RealtimeAudioOutputDone):
    if item.interrupted:
        logger.info("👉 Participant barged-in, interrupting the agent")
        await self.interrupt()
```

你的日志里没有出现：

```text
👉 Participant barged-in, interrupting the agent
```

这说明框架层的这条打断清缓冲路径没有被触发。

## 6. 官方示例怎么做打断

阿里官方 Python 示例 `samples/conversation/omni/python/run_server_vad.py` 的做法很明确：

```python
if 'response.audio.delta' == type:
    recv_audio_b64 = response['delta']
    b64_player.add_data(recv_audio_b64)
if 'input_audio_buffer.speech_started' == type:
    print('======VAD Speech Start======')
    b64_player.cancel_playing()
```

官方 Java 示例同样在 `input_audio_buffer.speech_started` 时调用：

```java
audioPlayer.cancel();
```

也就是说，官方示例不是只发 `response.cancel`，而是在服务端 VAD 发现用户开始说话时，客户端立刻取消本地播放器。官方 README 还专门说明播放器按 chunk 播放，chunk 越大，打断延迟越高，推荐 100ms。这说明打断体验的关键之一就是本地播放缓冲控制。

当前 TideSync 通过 WebRTC 播放，等价的本地播放器就是 GetStream `AudioStreamTrack` 的 buffer。框架有 flush，但 Qwen 插件没触发这条 flush。

## 7. 你看到“不能打断”的直接原因

从源码和日志对齐看，原因不是单一的，而是三点叠加。

第一，Qwen 插件收到 `input_audio_buffer.speech_started` 后，只在 `_is_responding` 为真时调用 `_on_interruption()`。如果服务端事件顺序、状态更新、或 response 生命周期没有让 `_is_responding` 正确覆盖“本地仍在播放”的阶段，那么它不会处理打断。

第二，即使 `_on_interruption()` 触发，它做的事情也只是：

```python
if self._current_response_id:
    await self._client.cancel_response()
self._is_responding = False
self._current_response_id = None
self._current_item_id = None
```

这里没有清本地 audio output，也没有发 `RealtimeAudioOutputDone(interrupted=True)` 给框架。远端可能停止生成了，但已经进入 WebRTC audio track 的音频仍会继续播。

第三，插件没有 emit `RealtimeUserSpeechStarted` / `RealtimeAgentSpeechStarted` / `RealtimeAgentSpeechEnded`。这让框架和上层事件系统对“谁正在说话”的状态不可见，也让一些 turn lifecycle 事件缺失。

所以当前不是“没有任何打断代码”，而是“打断代码停在 Qwen 插件内部，没有完整连接到本地播放输出链路”。这就是你感知上不像 OpenAI / Gemini 的原因。

## 8. 你看到“好像不是流式传输”的原因

日志其实证明 Qwen 正在流式输出文本。比如：

```text
01:45:43.742 | Agent transcript: 你好
01:45:43.751 | Agent transcript: 呀
01:45:43.752 | Agent transcript: ，
...
01:45:43.848 | User transcript: 你好呀，你是谁呀？
...
```

这些 `Agent transcript` 是 `response.audio_transcript.delta` 逐片来的，不是一次性完整返回。`RealtimeInferenceFlow` 收到每个 delta 后都会更新 Stream conversation。

为什么你会觉得“文字全部打出来，然后语音才慢慢播”？因为文字和语音是两个不同投影：

- 文字投影来自 `response.audio_transcript.delta`，很小，走 Stream Chat 消息更新，视觉上可以很快累积完整。
- 语音投影来自 `response.audio.delta`，是 base64 音频数据，需要解码、转成 PCM、进入 `AudioOutputStream`、切成 20ms chunk、写入 WebRTC audio track、再经过浏览器播放缓冲。

这两个事件都来自 Qwen，但到用户端的路径不同。文字先完整出现，不等于模型没有流式音频；它更可能说明：文本 transcript 的传输和显示比音频播放链路快很多。

同时，当前 Qwen 插件没有处理 `response.audio.done`，也没有在 `response.done` 时发 `AudioOutputChunk(final=True)` 或 `RealtimeAudioOutputDone`，所以音频输出的结束边界没有被框架很好表达。这样会让“语音慢慢播完”的体感更明显，因为本地播放队列只是在自然 drain，而不是被明确标记为一个响应段落结束。

## 9. 日志里的视频错误说明什么

你的日志里多次出现：

```text
Error received from Qwen3Realtime API: {'type': 'invalid_request_error', 'message': 'Error append image before append audio.'}
```

这个错误不是“模型看不懂视频”。它说明程序在某些时刻向 Qwen 发送了 image frame，但服务端认为当前输入上下文里还没有先收到 audio append。Qwen Realtime 的图像输入有时序约束：要先发送音频，再发图片。`vision_agents.plugins.qwen.client.py` 的注释也写了：必须至少发送一次音频后才能发送图像数据。

插件里用 `_audio_emitted_once` 防止一开始先发图：

```python
if not self._audio_emitted_once:
    return
```

但你的日志显示，在视频 track 断开/重连、音频 track unpublished、或服务端进入新一轮缓冲状态后，这个布尔值不足以表达 Qwen 当前服务端 buffer 状态。它只记录“这个 Python 对象曾经发过音频”，不记录“当前服务端这一轮输入缓冲已经先收到音频”。

所以视频这块也有适配层状态问题：它需要按 Qwen 的轮次/缓冲语义管理音频和图像发送顺序，而不是只用一个 `_audio_emitted_once` 全局布尔值。

## 10. 当前 SDK 是否很好发挥了模型能力

我的判断：没有。

不是完全没接上；它已经接上了基础语音对话、文字 transcript、音频输出和视频帧发送，所以你能问“这里面有什么”，模型也能基于画面回答。但它没有很好发挥 Qwen Realtime 的完整交互能力。

缺口包括：

1. 打断没有完整接入本地播放清理。
2. 没有把 server VAD 的 speech started/stopped 投射成框架事件。
3. 没有把 agent speech started/ended 投射成框架事件。
4. 没有处理 `response.audio.done`。
5. `response.done` 只 final transcript，不 final audio。
6. 视频帧发送顺序用 `_audio_emitted_once` 这种弱状态，不能覆盖多轮输入和 track 重连。
7. `response.cancel` 之后没有本地状态和输出队列的统一收敛。
8. 没有记录 first text / first audio delay 等官方 SDK 示例里已有的时延指标。
9. 没有对 Qwen error 进行恢复策略，只记录错误继续跑。

因此当前更像“把 Qwen Realtime WebSocket 接进 Vision Agents 的基础 demo”，还不是一个达到 OpenAI Voice / Gemini Live 体感的 realtime adapter。

## 11. 模型处理掉的东西 vs 程序必须处理的东西

模型/API 已经处理：

- 音频识别。
- 服务端 VAD。
- 对话生成。
- 语音合成。
- 语音输出 transcript。
- 多模态理解。
- 流式事件产生。
- 接收 cancel 事件。
- 一部分语义打断判断。

程序必须处理：

- 从 WebRTC 收音频，转 16k mono PCM，发送 `input_audio_buffer.append`。
- 从视频 track 截帧，转 JPEG/base64，按 Qwen 时序发送 `input_image_buffer.append`。
- 把 Qwen 的 `response.audio.delta` 写入 WebRTC audio track。
- 把 Qwen 的 transcript delta 显示到 Stream chat。
- 在用户开始说话时清掉本地音频播放队列。
- 在必要时发送 `response.cancel`。
- 维护响应开始/结束、用户开始/结束、agent 开始/结束这些状态。
- 管理 track 断开/重连导致的输入轮次状态。
- 处理 Qwen error，并决定是否丢帧、重建 session、重置状态。

当前程序做了前四项的基础版本，没有做好后面几项。

## 12. 后续修复方向

如果下一步要改，我建议按这个顺序做，不要乱改。

第一步，加观测。先在 Qwen 插件里把服务端事件类型、response id、当前 `_is_responding`、audio buffer 状态、image send 状态打出来。现在日志没有显示 `input_audio_buffer.speech_started` 是否到达，也没有显示是否发送过 `response.cancel`。

第二步，修复打断投射。收到 `input_audio_buffer.speech_started` 时，应当无条件或在更准确条件下触发本地 audio flush；同时如果有当前 response，再发送 `response.cancel`。在 Vision Agents 语义里，更合适的是 emit `RealtimeAudioOutputDone(interrupted=True)` 或直接把中断事件送到 flow，让 `RealtimeInferenceFlow.interrupt()` 清 `AudioOutputStream` 和 WebRTC track。

第三步，补齐事件映射：

- `input_audio_buffer.speech_started` -> `_emit_user_speech_started()`
- `input_audio_buffer.speech_stopped` -> `_emit_user_speech_ended()`
- `response.created` 或首个 audio delta -> `_emit_agent_speech_started()`
- `response.audio.done` / `response.done` -> `_emit_audio_output_done_event()` 与 `_emit_agent_speech_ended()`

第四步，处理视频时序。`_audio_emitted_once` 应该替换成更接近“当前服务端输入轮次是否已有音频”的状态，或在收到相关错误后暂停图像发送直到下一段音频到达。否则摄像头 track 重连后仍会出现 `append image before append audio`。

第五步，再调 VAD 参数。当前配置是：

```python
vad_threshold=0.1
vad_prefix_padding_ms=500
vad_silence_duration_ms=900
```

这个静音结束时间偏长，会影响回合结束速度。但它不是“不能打断”的主因；主因是事件映射和本地播放清理。VAD 参数应该在事件链路打通后再调。

第六步，做真实交互验证。验证要看四个现象：

- 用户在 agent 讲话中途开口，agent 音频是否 100-300ms 内停止。
- 日志是否出现 speech_started、cancel、audio flush。
- Stream chat 是否不再继续追加被打断响应的后半段。
- 摄像头开关/track 重连后是否不再报 `append image before append audio`。

## 13. 最终判断

Qwen3.5-Omni-Flash-Realtime 本身承担的是实时全模态模型职责：听、看、理解、生成、说话、转写、VAD、流式输出和响应取消。Vision Agents/GetStream 承担的是媒体接入、WebRTC 播放、字幕/消息投影、会话生命周期和本地缓冲控制。

当前 TideSync 使用的 `vision-agents` Qwen 插件接上了基础输入输出，但没有把 Qwen 的实时事件完整映射到框架的 realtime control plane。你感受到的“不能打断”和“不像流式语音”都来自这个适配缺口，而不是模型完全不支持。

最关键的一句话：**Qwen 已经在发 realtime 事件；当前 SDK 适配层没有把这些事件变成正确的本地交互行为。**
