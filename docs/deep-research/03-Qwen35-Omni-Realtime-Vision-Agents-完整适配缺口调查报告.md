# Qwen3.5 Omni Realtime 与 Vision Agents Qwen Adapter 完整适配缺口调查报告

## 执行结论

本次调查对象是 Vision Agents Qwen realtime adapter 对官方 Qwen3.5-Omni-Flash-Realtime realtime API contract 的覆盖程度。官方能力边界来自 TideSync 本地保存的 Qwen3.5 文档，Vision Agents 覆盖边界来自 `external/Vision-Agents` 源码，TideSync 使用边界来自 `src/tidesync/agent.py` 与 `pyproject.toml`，旧 zipball 只作为历史客户端控制模式参考。

结论：Vision Agents 当前 Qwen adapter 只覆盖 WebSocket VAD 语音对话的基础路径：发送 16 kHz mono PCM 音频、发送 JPEG 图片帧、接收 `response.audio.delta`、接收助手 transcript delta、接收用户最终转写、在用户开始说话时向服务端发送 `response.cancel`。它没有覆盖 Qwen3.5 Omni Realtime 的完整官方 contract。缺口集中在七个对象层面：WebRTC 原生接入、semantic VAD、Manual 模式、完整响应生命周期事件、完整打断投射、本轮音频与图片时序状态、搜索与 Function Calling 能力面。Vision Agents core 已经有多个可承载这些能力的抽象，包括 `RealtimeAudioOutputDone`、用户/助手 speech started/ended 事件、audio output flush 和 GetStream audio track flush；Qwen adapter 没有充分使用这些核心抽象。

TideSync 当前依赖的是上游包行为，不是本地 fork 行为；它只在实例化时覆盖模型、base URL、音色、FPS，并固定启用视频。TideSync 没有向配置层暴露 Qwen3.5 的 VAD 类型、Manual、搜索、工具、usage、语音控制或 WebRTC 原生控制面。

## 官方 Qwen3.5 Omni Realtime 能力 contract

### 模型、地域、限额、价格

控制台摘要确认模型名称为 `Qwen3.5-Omni-Flash-Realtime`，模型 Code 为 `qwen3.5-omni-flash-realtime`，快照为 `qwen3.5-omni-flash-realtime-2026-03-15`，模型标签为实时全模态；同一摘要列出文本、图片、视频、音频输入和文本、图片、视频、音频输出，并标注 Function Calling 与联网搜索可用。证据：`docs/Qwen3.5-Omni-Flash-Realtime.md:15`、`:16`、`:17`、`:52`、`:53`、`:55`。同一摘要列出上下文 256K、最大输入 192K、最大输出 64K、RPM 60、TPM 100000。证据：`docs/Qwen3.5-Omni-Flash-Realtime.md:42`-`:49`。价格侧列出文本/图片/视频输入、音频输入、文本输出、文本+音频输出和联网搜索等工具调用价格。证据：`docs/Qwen3.5-Omni-Flash-Realtime.md:24`-`:30`。

API 文档确认 Qwen-Omni-Realtime 是实时音视频聊天模型，能理解流式音频与图像输入，并实时输出文本与音频。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:1`。API 文档列出支持北京和新加坡地域。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3`。

### WebSocket 与 WebRTC 连接 contract

官方 API 文档明确支持 WebSocket 和 WebRTC 两种协议。WebSocket 适合服务端集成和快速接入；WebRTC 适合浏览器端低延迟语音场景，音频通过 UDP 传输，并内置回声消除和降噪。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:11`。WebSocket 连接地址为北京 `wss://dashscope.aliyuncs.com/api-ws/v1/realtime`，新加坡为 workspace 域名，查询参数 `model` 必填，请求头为 Bearer Token。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:19`-`:23`。WebRTC 连接通过 HTTP POST SDP 到 `https://{endpoint}/api/v1/webrtc/realtime?model=...`，Content-Type 为 `application/sdp`，失败返回 HTTP 4xx JSON 错误；该功能当前白名单开放。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:134`-`:152`。

### session.update 配置 contract

`session.update` 的官方配置包括 `modalities`、`voice`、`input_audio_format`、`output_audio_format`、`instructions`、`turn_detection`。输出模态支持 `["text"]` 或 `["text","audio"]`；输入音频格式当前仅 `pcm`，输入音频是 16 kHz PCM；输出音频格式当前仅 `pcm`，输出音频是 24 kHz PCM；`turn_detection` 可为对象，也可为 `null`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:249`-`:281`。

`turn_detection.type` 官方取值为 `server_vad` 或 `semantic_vad`，且文档写明使用 qwen3.5 omni realtime 模型时推荐 `semantic_vad`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:274`-`:276`。VAD 参数包括 `threshold` 与 `silence_duration_ms`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:277`-`:280`。

### 输入与输出 transport contract

音频输入是必需的，图片输入是可选的。WebSocket 通过 `input_audio_buffer.append` 与 `input_image_buffer.append` 发送 Base64 音频和图片到服务端缓冲区；启用 VAD 时服务端在检测到语音结束时自动提交并触发响应；禁用 VAD 时客户端必须发送 `input_audio_buffer.commit`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:286`-`:296`。

WebRTC 通过 RTP 媒体通道传输输入：音频通过音频轨道发送，不需要 `input_audio_buffer.append`；图片通过视频轨道发送，不支持 `input_image_buffer.append`。WebRTC 仅支持 VAD 模式，不支持 Manual。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:298`-`:307`。

WebSocket 文本输出通过 `response.text.delta` 与 `response.text.done`。WebSocket 文本+音频输出中，文本通过 `response.audio_transcript.delta` 与 `response.audio_transcript.done`，音频通过 Base64 `response.audio.delta`，`response.audio.done` 标志音频生成完成。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:313`-`:323`。WebRTC 文本通过 DataChannel 接收；文本+音频模式中，文本文档写为 DataChannel `response.text.delta` 与 `response.text.done`，音频通过 RTP 轨道播放，不通过 `response.audio.delta`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:326`-`:336`。

### VAD、Manual、打断和响应 lifecycle

VAD 模式下，WebSocket 和 WebRTC 都支持 `server_vad` 或 `semantic_vad`，两者服务端事件一致，区别在媒体传输方式。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:2984`-`:2986`。VAD 交互流程包括客户端发送音频、服务端发送 `input_audio_buffer.speech_started`、`input_audio_buffer.speech_stopped`、`input_audio_buffer.committed`、`response.created`、`conversation.item.created`、`response.audio_transcript.delta`，最终 `response.done`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:2988`-`:3000`。生命周期表还列出 `session.created`、`session.updated`、`response.output_item.added`、`response.content_part.added`、`response.audio.done`、`response.content_part.done`、`response.output_item.done`、用户语音转写 delta 和 completed。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3003`-`:3007`。

Manual 模式通过把 `session.turn_detection` 设为 `null` 启用。客户端显式发送 `input_audio_buffer.commit` 和 `response.create` 请求模型响应。Manual 中 `input_image_buffer.append` 前必须至少发送一次 `input_audio_buffer.append`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3009`-`:3025`。Manual 生命周期表还列出 `input_audio_buffer.clear`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3028`-`:3032`。

### 图片、视频、搜索、工具、语音控制和计费 usage

图片输入 FAQ 写明 WebSocket 用 `input_image_buffer.append`；VAD 模式下应在服务端 `input_audio_buffer.speech_stopped` 前发送图片；Manual 模式参照 Manual 代码；WebRTC 通过视频轨道发送画面帧。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3477`-`:3494`。

联网搜索仅 Qwen3.5-Omni-Realtime 支持，默认关闭，需通过 `session.update` 启用；字段为 `enable_search` 与 `search_options.enable_source`；启用后 `response.done` 的 `usage.plugins.search` 记录搜索计量，包含 `count` 与 `strategy`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3034`-`:3078`。

Function Calling 是官方模型选型列出的 Qwen3.5 增强能力，文档说明模型可自主判断是否需要调用外部工具。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:351`-`:353`。当前本地 API 文档只给出能力入口链接，没有展开工具 schema、tool call 事件和 tool result 事件字段；这些字段需要 live API 或官方 Function Calling 页面进一步确认。

语音控制能力包括通过语音指令控制声音大小、语速和情绪。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:359`-`:361`。语言与音色能力包括 113 种语种和方言语音识别、36 种语种和方言语音生成、55 种音色，以及 Qwen3.5 plus/flash realtime 声音复刻。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:363`-`:373`。

使用限制包括联网搜索和工具调用不兼容、单次会话最长 120 分钟、模型维护历史上下文并按轮次或累计时长丢弃更早历史。对 `qwen3.5-omni-flash-realtime`，音频最大 80 轮，视频最大 50 轮，音频最大 480 秒，视频最大 120 秒。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:378`-`:394`。

计费 usage 示例中 `response.done` 的 usage 包含 `total_tokens`、`input_tokens`、`output_tokens`、`input_tokens_details.text_tokens`、`input_tokens_details.audio_tokens`、`output_tokens_details.text_tokens`、`output_tokens_details.audio_tokens`、`plugins.search`。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3055`-`:3078`。音频计费规则中 Qwen3.5 输入音频为秒数乘 7，输出音频为秒数乘 12.5；图片计费中 Qwen3.5 plus 每 `32x32` 像素对应 1 token，本地文档未在该表中单独列 flash 图片 token 规则。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3362`-`:3387`。

错误行为文档只在 WebRTC SDP 交换处说明失败返回 HTTP 4xx JSON 错误，并在错误码章节指向错误码文档。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:145`-`:152`、`:3496`-`:3498`。本地文档没有给出所有 WebSocket error event 的 recoverability 分类。

## Vision Agents Qwen adapter code map

上游 Qwen provider 类为 `Qwen3Realtime`，从 `vision_agents.core.llm.Realtime` 继承，对外在 `vision_agents.plugins.qwen.__init__` 中以 `Realtime` 导出。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:27`-`:28`，`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/__init__.py:1`。WebSocket client wrapper 为 `Qwen3RealtimeClient`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py:15`-`:18`。

`Qwen3Realtime` 代码默认模型为 `qwen3.5-omni-plus-realtime`，默认 base URL 为 `wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime`，默认音色为 `Cherry`，默认 ASR/transcription 模型为 `gummy-realtime-v1`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:21`、`:32`、`:35`、`:40`、`:50`。README 与代码不一致：README 表格写默认模型为 `qwen3-omni-flash-realtime`，用法示例也显式使用该旧模型；代码实际默认是 Qwen3.5 plus realtime。证据：`external/Vision-Agents/plugins/qwen/README.md:33`、`:45`，`qwen_realtime.py:32`。

adapter 生成的 session config 固定 `modalities=["text","audio"]`、`voice`、`instructions`、`input_audio_format="pcm16"`、`output_audio_format="pcm24"`、`input_audio_transcription={"model": self._audio_transcription_model}`、`turn_detection.type="server_vad"`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:80`-`:94`。这与官方本地 API 文档中的 `pcm` 字符串不一致，尽管 client 注释说明发送音频会重采样为 16-bit 16 kHz mono PCM。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py:91`-`:99`，官方证据为 `docs/Qwen3.5-Omni-Flash-Realtime-API.md:266`-`:269`。

client 只实现 WebSocket：构造 URL 时把 `model` 拼为 query 参数，使用 `websockets.connect` 与 Bearer Header，连接后发送 `session.update`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py:29`、`:38`-`:52`、`:87`-`:90`。client sender 包括 `input_audio_buffer.append`、`input_audio_buffer.commit`、`input_image_buffer.append`、`response.cancel`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py:91`-`:125`。provider 当前只调用 `send_audio`、`send_frame`、`cancel_response`，没有调用 `commit_audio` 或发送 `response.create`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:108`-`:115`、`:191`-`:195`、`:266`-`:276`。

视频 forwarding 使用 Vision Agents `VideoForwarder` 按 `fps` 抽帧，并通过 `frame_to_jpeg_bytes` 转 JPEG 后发送 `input_image_buffer.append`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:140`-`:166`、`:168`-`:195`。adapter 用 `_audio_emitted_once` 阻止首个音频发送前发图，但该布尔值只表达“本 Python 对象曾经发送过音频”，不表达官方所需的当前输入轮次和服务端 buffer 状态。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:69`-`:70`、`:175`-`:178`。

事件 reader loop 处理的服务端事件为：`error`、`session.created`、`response.created`、`response.output_item.added`、`response.done`、`input_audio_buffer.speech_started`、`response.audio.delta`、`conversation.item.input_audio_transcription.completed`、`response.audio_transcript.delta`。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:223`-`:265`。它没有处理 `session.updated`、`input_audio_buffer.speech_stopped`、`input_audio_buffer.committed`、`conversation.item.created`、`response.content_part.added`、`response.text.delta`、`response.text.done`、`response.audio_transcript.done`、`response.audio.done`、`response.content_part.done`、`response.output_item.done`，也没有读取 `response.done.response.usage`。证据为同一事件分支缺失范围：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:223`-`:265`。

interruption 当前只在 `input_audio_buffer.speech_started` 且 `_is_responding` 为真时调用 `_on_interruption`；`_on_interruption` 只发送 `response.cancel` 并清本地 response id/item id 状态，没有 emit `RealtimeAudioOutputDone(interrupted=True)`、没有 emit `RealtimeUserSpeechStarted`、没有 emit `RealtimeAgentSpeechEnded(interrupted=True)`、没有触发 audio output flush。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:250`-`:252`、`:266`-`:276`。

测试覆盖只有被整体 skip 的 integration tests，断言能收到 `RealtimeAudioOutput`；没有单元测试覆盖 session config、VAD 类型、Manual、search、tool calling、event mapping、interruption flush、usage 或 stale delta。证据：`external/Vision-Agents/plugins/qwen/tests/test_qwen_realtime.py:12`-`:14`、`:34`-`:48`、`:50`-`:73`。

## Vision Agents core realtime event/control map

Vision Agents core 已定义 `RealtimeAudioOutput`、`RealtimeAudioOutputDone`、`RealtimeUserTranscript`、`RealtimeAgentTranscript`、`RealtimeUserSpeechStarted`、`RealtimeUserSpeechEnded`、`RealtimeAgentSpeechStarted`、`RealtimeAgentSpeechEnded`。证据：`external/Vision-Agents/agents-core/vision_agents/core/llm/realtime.py:23`-`:76`。`Realtime` base class 提供 `_emit_audio_output_event`、`_emit_audio_output_done_event`、`_emit_user_speech_started`、`_emit_user_speech_ended`、`_emit_agent_speech_started`、`_emit_agent_speech_ended`、用户 transcript 和助手 transcript emit helper。证据：`external/Vision-Agents/agents-core/vision_agents/core/llm/realtime.py:212`-`:285`。

`RealtimeInferenceFlow` 消费这些事件：`RealtimeAudioOutput` 写入 `AudioOutputStream`，`RealtimeAudioOutputDone(interrupted=True)` 调用 `interrupt()`，非中断 done 发送 final audio chunk；用户 speech started/ended 转为 `UserTurnStartedEvent`/`UserTurnEndedEvent`；助手 speech started/ended 转为 `AgentTurnStartedEvent`/`AgentTurnEndedEvent`；用户和助手 transcript 写入 conversation。证据：`external/Vision-Agents/agents-core/vision_agents/core/agents/inference/realtime_flow.py:127`-`:233`。

`RealtimeInferenceFlow.interrupt()` 会调用 LLM interrupt、flush agent/user transcript、清空 `AudioOutputStream` 并发送 flush。证据：`external/Vision-Agents/agents-core/vision_agents/core/agents/inference/realtime_flow.py:110`-`:119`。`AudioOutputStream.flush()` 发送 `AudioOutputFlush`，用于通知下游清空 buffer。证据：`external/Vision-Agents/agents-core/vision_agents/core/agents/inference/audio.py:118`-`:124`。Agent 的 audio producer 收到 `AudioOutputFlush` 时调用 GetStream `AudioStreamTrack.flush()`。证据：`external/Vision-Agents/agents-core/vision_agents/core/agents/agents.py:923`-`:940`。

core 也有 epoch/stale event 基础对象：`Realtime.interrupt()` 增加 `_epoch` 并清 output。证据：`external/Vision-Agents/agents-core/vision_agents/core/llm/realtime.py:109`-`:156`。但是 Qwen adapter 发出的 `RealtimeAudioOutput` 没有携带 response id，也没有按 epoch 丢弃被打断后的迟到 `response.audio.delta`。证据：Qwen adapter `response.audio.delta` 分支仅解码并 emit audio，`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:253`-`:256`。

Agent 层负责监听视频 track 并将 video-capable LLM 连接到 track。证据：`external/Vision-Agents/agents-core/vision_agents/core/agents/agents.py:1039`-`:1048`。Qwen adapter 实现 `watch_video_track`，所以 core 能把 call 中的视频 track 交给 Qwen adapter；缺口在 adapter 内部的 Qwen buffer/turn 时序表达。证据：`external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:140`-`:166`。

## TideSync current usage map

TideSync 默认模型为 `qwen3.5-omni-flash-realtime`，默认 base URL 为中国内地 DashScope WebSocket `wss://dashscope.aliyuncs.com/api-ws/v1/realtime`，默认音色为 `Tina`，默认 FPS 为 1。证据：`micheng-ts/projects/TideSync/src/tidesync/agent.py:12`-`:15`。`RealtimeSettings` 只读取 `QWEN_REALTIME_MODEL`、`QWEN_REALTIME_BASE_URL`、`QWEN_REALTIME_VOICE`、`QWEN_REALTIME_FPS`。证据：`micheng-ts/projects/TideSync/src/tidesync/agent.py:23`-`:37`。`create_agent` 实例化 `qwen.Realtime` 时传入 `model`、`base_url`、`voice`、`fps`，并固定 `include_video=True`。证据：`micheng-ts/projects/TideSync/src/tidesync/agent.py:60`-`:68`。

TideSync 没有暴露 Qwen3.5 的 `turn_detection.type`、semantic VAD、Manual、`enable_search`、`search_options`、工具 schema、tool choice、usage、音频格式、transcription model 或语音控制配置。证据：`micheng-ts/projects/TideSync/src/tidesync/agent.py:23`-`:68`。TideSync 依赖 `vision-agents[qwen,getstream]>=0.6.4,<0.7`，没有本地 fork 依赖路径。证据：`micheng-ts/projects/TideSync/pyproject.toml:6`-`:10`。测试确认默认模型、base URL、音色、FPS 和 env override 行为。证据：`micheng-ts/projects/TideSync/tests/test_hello.py:6`-`:31`。

本地 `.venv/lib/python3.13/site-packages/vision_agents` 路径在本次文件枚举中未返回文件；因此报告中的 Vision Agents 代码结论以 `/home/t103o/workbench/external/Vision-Agents` 上游 clone 为直接源码依据，以 TideSync `pyproject.toml` 作为依赖版本范围依据。

## 旧 zipball reference assessment

旧 `omni-realtime_zipball_0.0.3` 使用 FastAPI WebSocket bridge 接浏览器，再由服务端连接 DashScope WebSocket。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/server.py:7`-`:9`、`:138`-`:140`、`:212`-`:243`。它不是 Qwen 原生 WebRTC transport；浏览器与后端之间是应用 WebSocket，DashScope 侧也是 WebSocket，不包含 SDP 交换、RTP 音频轨道或 DataChannel。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/server.py:83`-`:97`，`tmp/omni-realtime_zipball_0.0.3/src/code/omni_realtime_client.py:86`-`:99`。

旧实现使用旧模型默认：server 创建 client 时写死 `qwen-omni-turbo-realtime`，client 默认 model 为空，session transcription 使用 `gummy-realtime-v1`。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/server.py:83`-`:94`，`tmp/omni-realtime_zipball_0.0.3/src/code/omni_realtime_client.py:45`-`:52`、`:101`-`:130`。

旧实现包含客户端音频队列和 `interrupt` 控制消息。服务端在 `on_interrupt` 中向浏览器发送文本 `"interrupt"`；浏览器收到后调用 `handleInterrupt()`，清空 audio queue、设置 interrupted 标记并切回 listening UI。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/server.py:172`-`:180`，`tmp/omni-realtime_zipball_0.0.3/src/code/static/index.html:994`-`:1016`、`:1123`-`:1128`。旧 client 在 `input_audio_buffer.speech_started` 时会执行 on_interrupt，并在 responding 时发送 `response.cancel`。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/omni_realtime_client.py:243`-`:251`。

旧 zipball 也有 Manual/server VAD 枚举、`input_audio_buffer.commit`、`response.create`、`input_image_buffer.append`。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/omni_realtime_client.py:11`-`:14`、`:159`-`:195`。它没有定义 Qwen3.5 完整 contract：没有 semantic VAD、没有 WebRTC 原生 transport、没有搜索、没有 Function Calling、没有 usage 字段处理、没有 Qwen3.5 flash/plus 限额建模。

## Coverage matrix

| Official capability | Official API surface | Protocol scope | Model-side responsibility | Adapter/runtime responsibility | Vision Agents current coverage | Coverage status | Evidence path and line reference | Required adaptation | Verification surface |
|---|---|---|---|---|---|---|---|---|---|
| 模型族与模型 code | `qwen3.5-omni-flash-realtime`、plus/flash realtime；snapshot 由控制台给出 | Both | 提供 Qwen3.5 Omni realtime 模型能力 | 允许目标模型 code 显式配置，避免旧模型默认误导 | TideSync 覆盖 flash；adapter 代码默认 plus；README 表格仍写旧 `qwen3-omni-flash-realtime` | partial | 官方：`docs/Qwen3.5-Omni-Flash-Realtime.md:15`-`:17`；VA：`plugins/qwen/qwen_realtime.py:32`，`plugins/qwen/README.md:33`、`:45`；TideSync：`src/tidesync/agent.py:12` | adapter 文档和配置默认需要与 Qwen3.5 flash/plus 目标集合一致；TideSync 需要保留 flash override 的可见性 | 静态配置测试；实际连接 flash/plus smoke |
| WebSocket 连接 | `wss://.../api-ws/v1/realtime?model=...` + Bearer | WebSocket | 接收 WS 事件流 | 建立 WS、发送 Bearer、发送 session.update | 覆盖 | covered | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:19`-`:23`；VA：`client.py:29`、`:38`-`:52` | 无对象缺口；需补错误恢复语义 | Mock WS connect；live WS connect |
| WebRTC 原生连接 | SDP POST 到 `/api/v1/webrtc/realtime?model=...`，RTP + DataChannel | WebRTC | 通过 RTP/DataChannel 收发实时媒体与事件 | 建立 SDP、管理音频/视频 track、DataChannel session.update/events | 没有 Qwen 原生 WebRTC；当前是 Stream/GetStream WebRTC 到 Vision Agents，再由 adapter 转 DashScope WebSocket | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:134`-`:152`；VA：`client.py:15`-`:18`、`:38`-`:52` only WebSocket | 新增或分离 Qwen WebRTC transport；不要把当前桥接 WS 等同官方 WebRTC | Live API WebRTC 白名单；SDP/DataChannel integration |
| session.update 基本字段 | `modalities`、`voice`、`input_audio_format`、`output_audio_format`、`instructions`、`turn_detection` | Both | 按 session config 调整输出、语音、VAD | 暴露并发送官方字段 | 部分发送；格式字符串为 `pcm16`/`pcm24`，官方文档为 `pcm` | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:249`-`:281`；VA：`qwen_realtime.py:80`-`:94` | 对齐官方字段名和值域；保留兼容性判断需 live API 验证 | Session config unit test；live session.updated |
| 输入音频格式 | 16 kHz PCM，WebSocket Base64 append；WebRTC RTP | Both | 接收音频并做 ASR/VAD | 重采样到 16 kHz mono PCM；按协议发送 | WebSocket 发送覆盖；WebRTC 原生缺失 | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:266`-`:268`、`:290`-`:304`；VA：`client.py:91`-`:99` | WebSocket 保留 PCM 重采样；WebRTC 需 RTP 发送路径 | PCM fixture；live ASR |
| 图片/视频输入规则 | WebSocket `input_image_buffer.append`；WebRTC 视频轨道；VAD 图像须在 speech_stopped 前；Manual 图像前须已 append audio | Both | 图像/帧理解 | 按协议与 turn 时序发送图像 | WebSocket 图片发送覆盖；只用 `_audio_emitted_once` 弱状态；WebRTC 原生缺失 | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3477`-`:3494`；VA：`qwen_realtime.py:69`-`:70`、`:168`-`:195`；client：`client.py:106`-`:120` | 建模每轮 input buffer 的 audio-before-image 状态；VAD 下约束 speech_stopped 前发图；WebRTC 需视频轨道 | Error replay：append image before append audio；track reconnect |
| 文本输入 | 本地 realtime 文档未给 text input client event；模型响应输出支持文本 | WebSocket/WebRTC unknown | 处理用户文本输入未在本地文档确认 | adapter 不应伪造未确认输入面 | adapter 明确不支持 text simple_response | not applicable | 官方：无本地 text input contract；VA：`qwen_realtime.py:117`-`:125` | live API 确认是否存在文本输入事件后再定义 | 官方 client-events/live |
| 文本-only 输出 | WebSocket `response.text.delta/done`；WebRTC DataChannel `response.text.delta/done` | Both | 生成纯文本响应 | 处理 text delta/done 并投射 transcript | 未处理 `response.text.*` | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:313`-`:317`、`:326`-`:330`；VA event loop：`qwen_realtime.py:223`-`:265` | 处理 `response.text.delta` 与 `response.text.done`，映射到 agent transcript/response lifecycle | Mock event unit test；text-only live session |
| 文本+音频助手 transcript | `response.audio_transcript.delta/done` | WebSocket; WebRTC 文档表述不完全一致 | 输出音频对应文本 | delta/done 映射到 assistant transcript final | 只处理 delta；`response.done` 时发空 final；不处理 done transcript | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:321`、`:3007`；VA：`qwen_realtime.py:245`-`:264` | 处理 `response.audio_transcript.done` 并用完整 transcript final；避免空 final 替代真实 done | Mock transcript done；conversation message assertion |
| WebSocket 助手音频输出 | `response.audio.delta` Base64 PCM，`response.audio.done` 标志完成 | WebSocket | 生成音频流 | 解码为 PCM、输出 chunk、输出 done boundary | 处理 delta；未处理 audio.done；未发送 audio output done | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:321`-`:323`；VA：`qwen_realtime.py:253`-`:256` | 处理 `response.audio.done` 与/或 `response.done`，emit `RealtimeAudioOutputDone` | Mock audio.done；audio final chunk |
| WebRTC 助手音频输出 | RTP 音频轨道，不返回 `response.audio.delta` | WebRTC | 通过 RTP 输出音频 | 接收/播放远端 RTP track | Qwen 原生 WebRTC 未实现 | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:332`-`:336`；VA client only WS：`client.py:38`-`:52` | 实现 Qwen WebRTC media receiver 或明确不承诺该协议 | Live WebRTC RTP playback |
| server_vad | `turn_detection.type="server_vad"` | Both | 检测语音起止、自动提交 | 发送配置，处理 speech events | session 配置覆盖 server_vad；事件只处理 speech_started 的 cancel 路径 | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:2984`-`:3007`；VA：`qwen_realtime.py:88`-`:93`、`:250`-`:252` | 映射 speech_started/ended/committed 到 core turn events 和 input state | Mock VAD event sequence |
| semantic_vad | `turn_detection.type="semantic_vad"`，Qwen3.5 推荐 | Both | 语义打断和无意义背景音过滤 | 暴露并发送 semantic_vad 配置 | 不支持配置，只写死 server_vad | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:274`-`:276`、`:2984`-`:2986`；VA：`qwen_realtime.py:88`-`:93` | 增加 VAD type 配置和值域，保留 threshold/silence 参数 | Static session_config test；live semantic VAD behavior |
| Manual 模式 | `turn_detection=null`、`input_audio_buffer.commit`、`response.create` | WebSocket only | 等待显式提交后生成响应 | 暴露 Manual mode，按轮次 commit/create | client 有 commit sender；provider 不暴露 Manual，也不发送 response.create | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3009`-`:3032`；VA：`client.py:101`-`:104`，provider event sender absent `qwen_realtime.py:108`-`:115`、`:223`-`:276` | session config 允许 `turn_detection=None`；实现 commit/create 控制面和输入轮次状态 | Manual live flow；unit event sender |
| 用户转写 delta | `conversation.item.input_audio_transcription.delta` | Both events; transcription enabled | 流式 ASR 文本 | 映射为 user transcript delta | 未处理 delta | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3007`；VA：`qwen_realtime.py:257`-`:260` only completed | 处理用户转写 delta 并保持 participant 归属 | Mock ASR delta；conversation update |
| 用户转写 completed | `conversation.item.input_audio_transcription.completed` | Both events; transcription enabled | 完成 ASR 文本 | 映射为 user transcript final | 覆盖 final | covered | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3007`；VA：`qwen_realtime.py:257`-`:260`；core：`realtime_flow.py:164`-`:200` | 无对象缺口；需确认 ASR 模型默认 | Mock completed event |
| 用户 speech started/ended | `input_audio_buffer.speech_started/stopped` | Both | VAD 起止 | emit `RealtimeUserSpeechStarted/Ended` | 未 emit；speech_started 只触发 cancel；speech_stopped 未处理 | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:2992`-`:2994`；VA：`qwen_realtime.py:250`-`:252`; core helper：`realtime.py:236`-`:250` | 调用 core emit helpers，并保持 participant 状态 | Core event assertion |
| 助手 speech started/ended | response/audio lifecycle | Both | 开始/结束输出 | emit `RealtimeAgentSpeechStarted/Ended` | 未 emit | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:2998`-`:3007`；VA loop lacks helper calls `qwen_realtime.py:240`-`:265`; core helper：`realtime.py:252`-`:262` | 在 `response.created` 或首个 audio delta emit started；在 audio.done/response.done/interruption emit ended | AgentTurn events tests |
| 响应 lifecycle 完整事件 | `response.created/output_item.added/content_part.added/audio_transcript.delta/audio.delta/audio_transcript.done/audio.done/content_part.done/output_item.done/response.done` | Both event stream, with audio transport differences | 响应生成状态 | 建模 response/item/content/audio/text 边界 | 只记录 response id、item id、empty final transcript；缺失多数 lifecycle | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3007`；VA：`qwen_realtime.py:240`-`:265` | 建模 response/item/content/audio/text 状态和 finalization | Ordered event replay tests |
| interruption/cancellation | `input_audio_buffer.speech_started` + `response.cancel`，本地播放清理为 runtime 责任 | Both events; response.cancel over control channel | 停止或取消远端生成 | 停服务端生成、清本地播放、丢弃旧响应 delta | 只发 `response.cancel`；不清本地 audio output，不丢弃 stale delta | partial | 官方 speech_started：`Qwen3.5-Omni-Flash-Realtime-API.md:2992`; VA：`qwen_realtime.py:250`-`:276`; core flush：`realtime_flow.py:110`-`:119`，`agents.py:935`-`:940` | emit interrupted audio done 或调用 flow interrupt 等价信号；按 response id/epoch 丢弃迟到 delta | Barge-in integration; delayed delta replay |
| `input_audio_buffer.clear` | Manual 表列出的客户端事件 | WebSocket Manual | 清除服务端输入缓冲 | 提供 clear sender | 未实现 sender | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3032`; VA client sender list：`client.py:87`-`:125` | 增加 input buffer clear 控制面 | Manual error recovery test |
| 搜索 enable/config | `enable_search=true`、`search_options.enable_source=true`；搜索与工具互斥 | Both session? 本地文档未区分协议 | 自主搜索并返回来源/计量 | 暴露配置，发送 session.update 字段，读取 usage.plugins.search | 不支持 | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3034`-`:3055`; VA session_config：`qwen_realtime.py:80`-`:94` | 增加 search config、互斥校验和 usage extraction | Session config test；live search usage |
| Function Calling | Qwen3.5 Omni Realtime 支持工具调用；本地文档只给能力入口 | Both unknown | 判断是否调用外部工具 | 注册工具 schema、处理 tool-call events、执行工具、返回结果 | Qwen adapter 没有 tools surface；core base 有 background tool task，但 adapter 未使用 | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:351`-`:353`; VA adapter no tool branches `qwen_realtime.py:223`-`:265`; core tool task helpers `realtime.py:158`-`:174` | 以官方 Function Calling 事件 contract 为准实现 tool schema、tool call、tool result | 官方 doc/live tool event capture |
| 语音控制 | 语音指令控制音量、语速、情绪 | Both model behavior | 理解并调整生成语音属性 | 暴露可观测状态或至少不破坏模型行为；记录 voice-control effects | 无配置、无状态、无事件观察 | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:359`-`:361`; VA config only voice `qwen_realtime.py:80`-`:94` | 定义语音控制的 runtime 可观测对象；确认是否有服务端事件或只表现为模型行为 | Live prompts for volume/speed/emotion |
| 音色与声音复刻 | 55 音色；Qwen3.5 plus/flash 支持自定义音色 | Both | 语音合成 | 传 voice 并校验/暴露 voice choices/custom voice id | 只传 voice 字符串；无 voice list 或 clone config | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:367`-`:373`；VA：`qwen_realtime.py:35`、`:82`-`:87` | 暴露官方音色/自定义音色标识；错误面处理 | Voice list/live voice tests |
| Usage/billing fields | `response.done.response.usage`，含 token details 与 plugins.search | Both events | 返回计费统计 | 提取、记录、暴露 metrics | 未读取 usage | missing | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:3055`-`:3078`; VA `response.done` branch：`qwen_realtime.py:245`-`:249` | 解析 usage 并进入 metrics/session event | Mock response.done usage |
| 会话限制 | 120 分钟；flash 音频 80 轮/480 秒，视频 50 轮/120 秒 | Both | 自动丢弃历史或关闭 session | 观测 session age/turn/media duration，向产品暴露风险 | 无限制建模；WebSocket 1011/1012/1013/1014 可重连 | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:378`-`:394`; VA reconnect：`client.py:61`-`:72`、`:134`-`:151` | 记录 session duration/turn/media counters；明确 reconnect 后上下文丢失边界 | Long session/live close test |
| 错误行为与 recoverability | WebRTC HTTP 4xx JSON；错误码文档引用；WS error event | Both | 返回错误 | 分类错误、恢复或降级、重置 runtime state | 记录 error 并 emit LLMErrorEvent；连接 close code 有有限重连；Qwen error 不重置 video/audio turn state | partial | 官方：`Qwen3.5-Omni-Flash-Realtime-API.md:145`-`:152`、`:3496`-`:3498`; VA：`qwen_realtime.py:226`-`:235`; client：`client.py:67`-`:85`、`:134`-`:151` | 建立 Qwen error taxonomy 和 state recovery；处理 append image before audio 等可恢复错误 | Error injection tests |
| 控制台图片/视频输出 | 控制台矩阵列出文本、图片、视频、音频输出 | Protocol undefined in realtime API doc | 可能属于模型广义能力 | realtime adapter 只能实现有事件面的输出 | 本地 realtime API 响应 contract 只定义文本/音频输出事件，未定义图片/视频输出 transport | not applicable | 官方摘要：`Qwen3.5-Omni-Flash-Realtime.md:53`; API response：`Qwen3.5-Omni-Flash-Realtime-API.md:309`-`:336`; VA no image/video output branches `qwen_realtime.py:223`-`:265` | 若官方补充 realtime 图片/视频输出事件，再纳入 adapter contract | 官方文档/live API confirmation |

## Missing capability list

- Qwen 原生 WebRTC transport：当前 adapter 只通过 WebSocket 连接 DashScope，不实现官方 SDP、RTP 音频/视频轨道和 DataChannel。
- semantic VAD：官方 Qwen3.5 推荐 `semantic_vad`，adapter 固定 `server_vad`。
- Manual 模式：官方 WebSocket 支持 `turn_detection=null`、`input_audio_buffer.commit`、`response.create`，adapter 没有 provider-level mode。
- 文本-only 输出：官方有 `response.text.delta/done`，adapter 未处理。
- 用户转写 delta：官方有 `conversation.item.input_audio_transcription.delta`，adapter 未处理。
- 用户 speech started/ended：core 有事件类和 helper，adapter 未 emit。
- 助手 speech started/ended：core 有事件类和 helper，adapter 未 emit。
- `response.audio.done` 与 audio output done：adapter 不发 `RealtimeAudioOutputDone`。
- 完整 response lifecycle：`conversation.item.created`、`response.content_part.*`、`response.output_item.done` 等未处理。
- 本地打断清理：adapter 只发 `response.cancel`，未触发 Vision Agents audio flush，也未丢弃迟到 delta。
- `input_audio_buffer.clear`：官方 Manual 表中列出，client 未实现。
- search enable/config 与 search usage：adapter 不发送 `enable_search`/`search_options`，不读取 `usage.plugins.search`。
- Function Calling：adapter 无工具 schema 注册、tool-call event、工具执行、tool result return。
- 语音控制可观测面：adapter 无状态或事件表征音量、语速、情绪控制。
- usage/billing fields：adapter 未解析 `response.done.response.usage`。

## Partial capability list

- 模型默认与文档：代码默认 Qwen3.5 plus，TideSync 默认 Qwen3.5 flash，但 plugin README 仍写旧模型。
- session.update：覆盖部分字段，但格式值与本地官方文档不一致，且未暴露 Qwen3.5 扩展字段。
- WebSocket 音频输入：重采样和 append 覆盖，但 Manual commit/create 未接入 provider flow。
- WebSocket 图片输入：能发图，但 `_audio_emitted_once` 不足以表达每轮 input buffer 的 audio-before-image 约束。
- server_vad：能发送配置并响应 speech_started cancel，但未完整映射 speech events 和 committed。
- 助手 audio transcript：只处理 delta，未处理 done。
- 错误与 reconnect：连接 close code 有有限重连；Qwen API error 只记录，不做状态恢复。
- 会话限制：无 turn/media/session limit 观测，仅依赖服务端关闭。
- 音色：只传字符串，不管理官方音色列表或声音复刻参数。

## Not-applicable capability list with reason

- 文本输入：本地 Qwen3.5 realtime API 文档没有定义用户文本输入 client event；Vision Agents adapter 不支持 `simple_response(text)` 在当前证据下不是 Qwen3.5 realtime contract 缺口。
- 图片/视频输出：控制台摘要列出图片、视频输出，但本地 realtime API 响应章节只定义文本和音频输出 transport；在没有官方 realtime 图片/视频输出事件前，Qwen realtime adapter 无可实现事件面。
- WebRTC Manual 模式：官方明确 WebRTC 仅支持 VAD，不支持 Manual；WebRTC Manual 不属于适配目标。

## Confirmed facts from official docs

- Qwen3.5-Omni-Flash-Realtime 的模型 code 是 `qwen3.5-omni-flash-realtime`，快照是 `qwen3.5-omni-flash-realtime-2026-03-15`。证据：`docs/Qwen3.5-Omni-Flash-Realtime.md:15`-`:17`。
- Qwen-Omni-Realtime 支持 WebSocket 与 WebRTC，且两者媒体传输语义不同。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:11`、`:290`-`:307`。
- `session.update` 官方字段包括 modalities、voice、audio format、instructions、turn_detection；Qwen3.5 推荐 semantic VAD。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:249`-`:281`。
- WebSocket 与 WebRTC 在输出音频 transport 上不同：WebSocket 使用 `response.audio.delta`，WebRTC 使用 RTP 音频轨道。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:313`-`:336`。
- Manual 模式只属于 WebSocket contract，要求 commit 和 create response。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3009`-`:3032`。
- 搜索默认关闭，通过 session.update 启用，并在 usage.plugins.search 记录计量。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:3034`-`:3078`。
- Qwen3.5 Omni Realtime 支持 Function Calling，但本地 API 文档未展开其 realtime event contract。证据：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:351`-`:353`。

## Confirmed facts from Vision Agents code

- Qwen adapter 是 `Qwen3Realtime`，client wrapper 是 `Qwen3RealtimeClient`。证据：`plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:27`，`plugins/qwen/vision_agents/plugins/qwen/client.py:15`。
- adapter 默认 ASR model 是 `gummy-realtime-v1`，不是本地官方示例中的 `qwen3-asr-flash-realtime`。证据：VA `qwen_realtime.py:40`；官方示例：`docs/Qwen3.5-Omni-Flash-Realtime-API.md:702`-`:707`。
- adapter 固定 `turn_detection.type="server_vad"`。证据：`plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:88`-`:93`。
- adapter 事件 loop 没有处理 `response.audio.done`、`response.audio_transcript.done`、`input_audio_buffer.speech_stopped`、用户 transcription delta、usage 或 search/tool 事件。证据：`plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:223`-`:265`。
- Vision Agents core 已有 audio done、speech start/end 和 flush 抽象。证据：`agents-core/vision_agents/core/llm/realtime.py:23`-`:76`、`:225`-`:262`；`agents-core/vision_agents/core/agents/inference/realtime_flow.py:110`-`:163`。

## Confirmed facts from TideSync code

- TideSync 默认使用 `qwen3.5-omni-flash-realtime`、中国内地 DashScope WebSocket、`Tina`、FPS 1。证据：`src/tidesync/agent.py:12`-`:15`。
- TideSync 固定 `include_video=True`。证据：`src/tidesync/agent.py:62`-`:68`。
- TideSync 的配置只暴露 model/base_url/voice/fps。证据：`src/tidesync/agent.py:23`-`:37`。
- TideSync 依赖 PyPI/package 行为 `vision-agents[qwen,getstream]>=0.6.4,<0.7`。证据：`pyproject.toml:6`-`:10`。

## Confirmed facts from the old zipball

- zipball 是 browser WebSocket 到 FastAPI，再由 FastAPI 接 DashScope WebSocket。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/server.py:138`-`:243`。
- zipball 使用旧模型 `qwen-omni-turbo-realtime`。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/server.py:83`-`:94`。
- zipball 的 browser audio queue 能响应 `"interrupt"` 并清队列。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/static/index.html:994`-`:1016`、`:1123`-`:1128`。
- zipball 不是 Qwen 原生 WebRTC；它没有 SDP、RTP 或 DataChannel 实现。证据：`tmp/omni-realtime_zipball_0.0.3/src/code/server.py:83`-`:97`，`src/code/static/index.html:1110`-`:1128`。

## Inferences from comparing docs and code

- Vision Agents core 可以表达 Qwen 服务端 VAD 的用户 turn 起止和助手 speech 起止；Qwen adapter 没有把对应 Qwen 事件投射到这些 core 对象。
- `input_audio_buffer.speech_started` 对产品打断只完成了远端 cancel 的一部分；本地 GetStream audio track flush 需要通过 core 的 `RealtimeAudioOutputDone(interrupted=True)` 或等价控制信号触发。
- `_audio_emitted_once` 不能满足 Qwen 官方“本轮图片前必须有音频”的约束，因为它没有跟随 `input_audio_buffer.committed`、`speech_stopped`、track reconnect 或 server error 重置。
- adapter 当前更接近 WebSocket 基础 demo，而不是 Qwen3.5 Omni Realtime 完整 adapter。
- README 默认模型、代码默认模型和 TideSync 默认模型三者不一致，后续维护容易产生错误认知。

## Unknowns requiring live API verification

- 官方 `input_audio_format`/`output_audio_format` 在裸 WebSocket 中是否接受 `pcm16`/`pcm24`，还是必须使用文档中的 `pcm`。
- `gummy-realtime-v1` 在 Qwen3.5 Omni Realtime 上是否仍被接受；官方示例使用 `qwen3-asr-flash-realtime`。
- Function Calling 的 realtime 事件形状：工具 schema 字段、tool call delta/done 事件、tool result return 事件、与 Vision Agents tool abstraction 的可映射字段。
- 搜索功能在 WebRTC DataChannel 与 WebSocket 上是否完全同形，`usage.plugins.search` 是否总在 `response.done.response.usage`。
- `semantic_vad` 的 live 行为：无意义背景音、附和声、barge-in 的事件序列是否与 `server_vad` 完全一致。
- 服务端在 `response.cancel` 后是否仍可能发送旧 response 的 `response.audio.delta`；若会发送，adapter 需要以 response id 或 epoch 丢弃。
- `response.audio_transcript.done`、`response.audio.done`、`response.done` 的相对顺序在中断、错误和正常完成三种路径下是否稳定。
- WebRTC 白名单 endpoint、SDP answer、DataChannel 名称、视频轨道格式和浏览器端兼容性需要服务访问验证。
- 声音复刻在 realtime session.update 中的字段名、鉴权和错误面需要官方文档或 live API 确认。

## Evidence list

- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime.md:15`-`:17`：模型名称、code、snapshot。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime.md:24`-`:30`：价格。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime.md:42`-`:55`：限流、模态、Function Calling、搜索。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:1`-`:11`：实时音视频模型和协议入口。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:19`-`:23`：WebSocket 连接。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:134`-`:152`：WebRTC SDP 交换。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:249`-`:281`：session.update 字段。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:286`-`:336`：输入输出 transport。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:341`-`:373`：Qwen3.5 能力增强、搜索、工具、语义打断、语音控制、语言、音色。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:378`-`:394`：使用限制。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:2984`-`:3032`：VAD 与 Manual lifecycle。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:3034`-`:3078`：联网搜索与 usage.plugins.search。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:3362`-`:3387`：音频、图片 token 规则。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md:3477`-`:3498`：图片输入 FAQ 与错误码引用。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:21`-`:43`：adapter 默认 base URL、model、voice、ASR、VAD 参数。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:80`-`:106`：session_config 和 client connect。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:108`-`:115`：audio sender。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:140`-`:195`：video forwarding。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py:223`-`:276`：server event loop 和 interruption。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py:15`-`:18`：client identity。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py:38`-`:52`：WebSocket connect 与 session.update。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py:91`-`:125`：audio/image/commit/cancel senders。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/tests/test_qwen_realtime.py:12`-`:73`：skip integration tests。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/llm/realtime.py:23`-`:76`：core realtime event classes。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/llm/realtime.py:212`-`:285`：core emit helpers。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/agents/inference/realtime_flow.py:110`-`:119`：interrupt flush。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/agents/inference/realtime_flow.py:127`-`:233`：realtime output consumption。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/agents/inference/audio.py:36`-`:124`：audio output stream and flush。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/agents/agents.py:923`-`:940`：GetStream audio track write/flush。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/src/tidesync/agent.py:12`-`:15`：TideSync defaults。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/src/tidesync/agent.py:23`-`:37`：TideSync config surface。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/src/tidesync/agent.py:60`-`:68`：Qwen adapter instantiation。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/pyproject.toml:6`-`:10`：Vision Agents dependency range。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/tests/test_hello.py:6`-`:31`：TideSync settings tests。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/tmp/omni-realtime_zipball_0.0.3/src/code/server.py:83`-`:97`：old client construction.
- `/home/t103o/workbench/micheng-ts/projects/TideSync/tmp/omni-realtime_zipball_0.0.3/src/code/server.py:138`-`:243`：FastAPI WebSocket bridge.
- `/home/t103o/workbench/micheng-ts/projects/TideSync/tmp/omni-realtime_zipball_0.0.3/src/code/omni_realtime_client.py:101`-`:130`：old session config.
- `/home/t103o/workbench/micheng-ts/projects/TideSync/tmp/omni-realtime_zipball_0.0.3/src/code/omni_realtime_client.py:159`-`:202`：commit/image/create/cancel senders.
- `/home/t103o/workbench/micheng-ts/projects/TideSync/tmp/omni-realtime_zipball_0.0.3/src/code/omni_realtime_client.py:243`-`:251`：old interruption callback.
- `/home/t103o/workbench/micheng-ts/projects/TideSync/tmp/omni-realtime_zipball_0.0.3/src/code/static/index.html:994`-`:1016`：browser audio queue interrupt.

## 后续实现输入

- Qwen adapter 的目标能力对象是官方 Qwen3.5 Omni Realtime contract，不是 Vision Agents 当前抽象的最窄子集。
- WebSocket adapter 需要以 `session.update` 官方字段为配置对象，包含 `modalities`、`voice`、`instructions`、`input_audio_format`、`output_audio_format`、`input_audio_transcription`、`turn_detection`、`enable_search`、`search_options` 和工具配置对象。
- VAD 配置对象需要表达 `server_vad`、`semantic_vad` 和 WebSocket Manual 的 `turn_detection=null`；WebRTC 配置对象不得包含 Manual。
- 输入 buffer 状态需要表达当前轮次是否已经 append audio、是否允许 append image、是否已 committed、是否已被 clear、是否进入 response generation。
- WebSocket 音频输入发送需要保持 16 kHz mono PCM transport；图片输入发送需要绑定到当前输入轮次，不得用全局 once 布尔值替代轮次状态。
- Qwen event state machine 需要覆盖 session、input_audio_buffer、conversation.item、response、response.audio、response.audio_transcript、response.text、error、search usage、tool call 和 cancellation 对象。
- `input_audio_buffer.speech_started` 需要投射为用户 speech started、远端 response cancel、本地 audio output flush、助手 speech interrupted、旧 response delta 丢弃。
- `input_audio_buffer.speech_stopped` 需要投射为用户 speech ended，并驱动图像发送截止状态。
- `response.created` 或首个输出事件需要投射为助手 speech started；`response.audio.done`、`response.done` 或 interrupted path 需要投射为 audio output done 和助手 speech ended。
- `response.audio_transcript.delta/done` 和 `response.text.delta/done` 需要投射到 assistant transcript 的 delta/final 边界；用户 transcription delta/completed 需要投射到 user transcript 的 delta/final 边界。
- `response.done.response.usage` 需要进入 metrics 和 session event，包含 token details 与 `plugins.search`。
- 搜索配置需要与工具调用配置互斥，互斥依据来自官方“联网搜索和工具调用不兼容”限制。
- Function Calling 适配需要以官方 realtime Function Calling 事件面为准，包含工具 schema registration、tool-call event、工具执行、tool-result return 和错误回传。
- Qwen 原生 WebRTC adapter 需要单独表达 SDP 交换、RTP 音频输入、RTP 视频输入、RTP 音频输出、DataChannel 控制事件；它不能复用 WebSocket `input_audio_buffer.append` 和 `input_image_buffer.append` 作为媒体 transport。
- 错误恢复对象需要区分连接关闭、HTTP SDP 错误、Qwen `error` event、输入时序错误、音色错误、格式错误、session timeout，并定义每类错误对 input state、response state、local playback state 的影响。
