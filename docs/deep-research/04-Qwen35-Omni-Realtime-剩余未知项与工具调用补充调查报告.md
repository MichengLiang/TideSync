# Qwen3.5 Omni Realtime 剩余未知项与工具调用补充调查报告

## 执行结论

本次调查对象是 Vision Agents 适配 Qwen3.5-Omni-Flash-Realtime 时仍缺少的 API 与运行时事实。调查范围包括本地新增的工具调用文档、本地 Qwen3.5 Omni Realtime API 文档、Vision Agents 当前 Qwen 插件与通用 LLM 抽象、阿里云官方在线客户端事件、服务端事件、声音复刻与错误码文档，以及阿里百炼 speech demo 中的旧模型示例。未执行 live API 调用：当前环境没有 `DASHSCOPE_API_KEY`，TideSync 环境也未安装 `dashscope` 包；计划只允许已有凭据且无明确费用风险的轻量验证，因此 live 验证被阻塞。

结论分为三层。第一层是官方合同已经明确的事实：原生 Realtime JSON 合同的音频格式值是 `pcm`，输入要求为 16 kHz PCM，输出为 24 kHz PCM；Qwen3.5 的输入音频转录模型固定为 `qwen3-asr-flash-realtime`；工具调用通过 `session.update.session.tools` 注入工具定义，服务端以 `response.function_call_arguments.delta` 和 `response.function_call_arguments.done` 输出函数调用参数，客户端用 `conversation.item.create` 回传 `function_call_output`，再用 `response.create` 触发最终响应；`tool_choice` 与 `parallel_tool_calls` 在 Qwen-Omni-Realtime 中不受支持；联网搜索与工具调用不兼容。第二层是本地代码事实：Vision Agents 的 Qwen Realtime 插件仍发送 `pcm16` 与 `pcm24`，默认 ASR 为 `gummy-realtime-v1`，没有向 Qwen 会话注入通用 FunctionRegistry 的工具 schema，没有处理 Qwen 工具调用事件，也没有把搜索用量、函数调用输出项、取消后的状态细节纳入 Qwen 插件事件流。第三层是仍无法由文档封闭的运行时事实：`pcm16`/`pcm24` 是否被服务端宽容接受、`gummy-realtime-v1` 是否仍可用于 Qwen3.5、取消后是否保证不再出现旧响应音频增量、WebRTC 白名单端点上的搜索与工具事件是否与 WebSocket 完全一致，均需要有凭据、有白名单或可控费用条件下的 live API 验证。

对上一份覆盖矩阵的影响是：Function Calling 不再是“事件形状未知”的能力缺口，而是“合同已知、适配器未接线”的能力缺口；音频格式与 ASR 模型不再是同一类模糊兼容问题，而应拆成“官方合同值”和“当前插件值的 live 兼容性”两项；WebRTC 不再缺少基础协议面事实，端点、SDP、DataChannel、RTP 音频与 VAD 范围均已由本地官方文档覆盖；声音复刻有独立创建音色接口和 `voice` 会话字段，不是 Realtime 会话内的内联克隆字段。

## Unknowns Resolution Table

| 编号 | 主分类 | 已解析事实 | 仍未知或阻塞条件 |
| --- | --- | --- | --- |
| U1 Audio Format Strings | resolved by local official doc | 官方原生 JSON 合同只支持 `pcm`；输入音频为 16 kHz PCM，输出音频为 24 kHz PCM。Vision Agents 当前发送 `pcm16`/`pcm24`。新增工具调用文档的 SDK 示例使用 `AudioFormat.PCM_16000HZ_MONO_16BIT` 与 `AudioFormat.PCM_24000HZ_MONO_16BIT`。 | live API 未验证 `pcm16`/`pcm24` 是否被服务端宽容接受；缺少 `DASHSCOPE_API_KEY`。SDK enum 最终序列化字符串未在本地包中可见。 |
| U2 Input Audio Transcription Model | resolved by local official doc | 官方 Qwen3.5 文档固定 `input_audio_transcription.model` 为 `qwen3-asr-flash-realtime`，并写明不支持修改。Vision Agents 默认仍为 `gummy-realtime-v1`。阿里 speech demo 的 `gummy-realtime-v1` 示例绑定旧模型 `qwen-omni-turbo-realtime-latest`。 | `gummy-realtime-v1` 在 Qwen3.5 服务端是否仍被宽容接受未验证；缺少 live API 条件。 |
| U3 Function Calling Realtime Contract | resolved by local official doc | 新增本地工具调用文档与官方在线事件页共同给出工具定义、事件名、载荷字段、结果回传与限制。 | WebRTC 下工具调用的完整样例未在本地文档中出现；本地交互流程声明事件类型与 WebSocket 一致，因此属于文档推断，不是样例证明。 |
| U4 Search Contract Details | resolved by local official doc | `enable_search` 与 `search_options.enable_source` 是 `session.update` 字段；搜索用量出现在 `response.done.usage.plugins.search`，包含 `count` 与 `strategy`。本地文档声明 WebSocket 与 WebRTC 的控制指令和服务端事件类型一致。 | WebRTC 搜索的官方独立样例未发现；是否返回来源列表的完整载荷形状未在已读片段中展开。 |
| U5 Semantic VAD Event Ordering And Barge-in Behavior | resolved by local official doc | `turn_detection.type` 可设为 `server_vad` 或 `semantic_vad`；WebSocket 与 WebRTC VAD 模式服务端事件一致；流程包含 `speech_started`、`speech_stopped`、`committed`、`response.created` 等。`semantic_vad` 的语义说明是过滤回应语、背景音等无意义声音。 | 更细粒度的语义打断判定、边界时序和误触发恢复未由文档定义。 |
| U6 Response Cancellation And Stale Delta Behavior | still unknown | 官方在线客户端事件页定义 `response.cancel`，无可取消响应时返回 `error`。Vision Agents Qwen 插件在 `speech_started` 且正在响应时发送 `response.cancel`。 | 官方文档未发现“取消后不再发送旧 `response.audio.delta`”保证，也未发现 `response.cancelled` 事件；`response.done` 对 cancelled 状态的完整状态字段未在可用证据中闭合。 |
| U7 Response Event Ordering | resolved by local official doc | 本地交互流程表给出 `response.audio_transcript.done`、`response.audio.done`、`response.content_part.done`、`response.output_item.done`、`response.done` 的顺序。 | 该顺序是文档生命周期顺序；在异常、取消、网络重连或工具调用分支中的严格全序保证未由文档说明。 |
| U8 Qwen Native WebRTC Details | resolved by local official doc | 文档给出 `POST https://{endpoint}/api/v1/webrtc/realtime?model=...` SDP 交换，`Content-Type: application/sdp`，鉴权头，成功返回 Answer SDP，失败 HTTP 4xx JSON；WebRTC 白名单开放；客户端可创建自定义 DataChannel，服务端固定通过 `txt` 通道推送事件；音频输出走 RTP，控制指令和服务端事件走 DataChannel。 | 白名单端点不可用，未执行 WebRTC live 测试；工具与搜索在 WebRTC 的样例仍缺失。文档内部对 text+audio 模式文本事件存在 `response.text.*` 与 `response.audio_transcript.*` 两处表述差异。 |
| U9 Voice Cloning And Voice Control Contract | resolved by official online doc | 声音复刻是独立 HTTP 接口：创建音色时使用 `qwen-voice-enrollment`，指定 `target_model`，返回可用于 Realtime `voice` 参数的音色名；`target_model` 必须与后续 Omni 调用模型一致。语音控制在本地 Realtime 文档中表现为自然语言能力，可控制音量、语速、情绪。 | 未发现 Realtime 会话内创建复刻音色的字段；语音控制未发现专用 server event 或结构化状态字段。声音复刻接口有费用，且缺少 API key，未 live 验证。 |
| U10 Error Contract | still unknown | 官方在线服务端事件页定义 `error` 事件形状：`type: "error"`，`error` 对象含 `type`、`code`、`message`、`param`。客户端事件页说明 `session.update` 参数不合法返回 `error`，`response.cancel` 无可取消响应也返回 `error`。WebRTC SDP 失败为 HTTP 4xx JSON。本地 API 文档只把详细错误码委托给错误码页。 | 针对无效音频格式、无效转录模型、音频前图片、无效工具 schema、工具结果错误、搜索/工具同时开启、session timeout 的 Realtime 专属 code 与 recoverability 未由已读官方文档逐项列出。 |

## Function Calling Contract Extraction

事实：新增本地工具调用文档明确 Qwen3.5-Omni-Plus-Realtime 与 Qwen3.5-Omni-Flash-Realtime 支持工具调用，适用于语音对话场景，调用方式包括 DashScope SDK 与 WebSocket 原生协议。连接建立后，客户端通过 `session.update` 传入工具定义。工具定义数组使用 OpenAI 风格：每项 `type` 为 `function`，`function` 内含 `name`、`description`、`parameters`；`parameters` 是 JSON Schema 风格对象，根 `type` 为 `object`，可含 `properties` 与 `required`。

事实：服务端工具调用参数输出有两个事件层级。新增本地文档强调 `response.function_call_arguments.done`，载荷包含 `response_id`、`item_id`、`output_index`、`name`、`call_id` 和 `arguments`。官方在线服务端事件页补充了 `response.function_call_arguments.delta`，载荷包含 `response_id`、`item_id`、`output_index`、`call_id` 与 `delta`，并说明客户端应按接收顺序拼接增量，但完整内容以随后的 `done` 事件为准。官方在线服务端事件页还显示 `conversation.item.created`、`response.output_item.added`、`response.output_item.done` 与 `response.done.output` 可出现 `type: "function_call"` 的项，项内包含 `call_id`、`name`、`arguments`，其中 added 阶段的 `arguments` 可为空字符串，done 阶段为完整 JSON 字符串。

事实：客户端回传工具执行结果使用 `conversation.item.create`。其 `item.type` 是 `function_call_output`，`call_id` 必须对应 `response.function_call_arguments.done` 的 `call_id`，`output` 是工具执行结果字符串；`item.id` 可选，未提供时由服务端生成。工具结果回传后，客户端发送 `response.create`，触发模型基于工具结果生成最终响应。最终语音与文本分别通过 `response.audio.delta` 与 `response.audio_transcript.delta` 返回。

事实：Qwen-Omni-Realtime 不支持 `tool_choice` 与 `parallel_tool_calls`。事实：联网搜索与工具调用不兼容，不可同时开启。该限制同时出现在本地 Qwen3.5 API 文档和官方在线客户端事件页。

对 Vision Agents 的对比事实：通用 core 已有 `FunctionRegistry`，可以注册 async 函数，生成 `ToolSchema`，并执行 `call_function`。`ToolSchema` 当前形状是 `name`、`description`、`parameters_schema`，需要映射为 Qwen `{"type":"function","function":{...}}`。通用 `Realtime` 基类已有 `_run_tool_in_background`、`_await_pending_tools` 与 epoch 字段，用于后台工具任务与中断后的旧事件识别。Qwen 插件当前 `session_config` 不含 `tools`，事件处理未分支处理 `response.function_call_arguments.delta`、`response.function_call_arguments.done`、`function_call` 输出项，也没有创建 `function_call_output` 或发送工具后的 `response.create`。因此 U3 对覆盖矩阵的增量是：缺口对象从未知协议升级为已知协议未适配。

推断：Qwen 工具调用适配可以复用 core 的 registry 与工具执行抽象，但必须补一个 Qwen Realtime 专用协议映射层；该映射层不是新的工具执行模型，而是 `ToolSchema` 到 Qwen session tools、Qwen function_call 事件到 registry 调用、registry 结果到 `conversation.item.create` 的连接。

## Search Contract Supplement

事实：联网搜索仅 Qwen3.5-Omni-Realtime 模型支持，默认关闭。启用字段是 `session.update.session.enable_search: true`。若需要搜索结果来源列表，字段是 `session.update.session.search_options.enable_source: true`。官方在线客户端事件页声明 `search_options` 需先启用 `enable_search` 才生效，并声明 `tools` 与 `enable_search` 不兼容。

事实：搜索计量出现在 `response.done.usage.plugins.search`。本地 Qwen3.5 API 文档示例中，`usage` 包含 `total_tokens`、`input_tokens`、`output_tokens`、`input_tokens_details`、`output_tokens_details`，并新增 `plugins.search.count` 与 `plugins.search.strategy`，示例策略值为 `agent`。本地文档没有在已读片段中给出搜索来源列表的完整字段结构。

事实：本地交互流程说明 WebSocket 与 WebRTC 的服务端事件一致，区别在音频和图片传输方式；控制指令和服务端事件通过 DataChannel 传输，事件类型与 WebSocket 一致。因此，搜索开关作为 `session.update` 控制字段、搜索计量作为 `response.done` 字段，在文档层面适用于 WebRTC。推断范围：该结论基于“事件类型一致”的总则，不是基于 WebRTC 搜索专门样例。

对 Vision Agents 的对比事实：Qwen 插件当前没有 `enable_search`、`search_options` 或 `usage.plugins.search` 处理。上一份矩阵中的搜索能力应拆成两个合同项：会话配置项已经确定；搜索来源列表与 WebRTC 专门样例仍缺少独立证据。

## VAD And Cancellation Supplement

事实：`turn_detection.type` 可取 `server_vad` 或 `semantic_vad`。官方在线客户端事件页对 `server_vad` 的说明是基于声学特征检测语音结束，对 `semantic_vad` 的说明是基于语义有效性检测语音结束，可过滤回应语、背景音等无意义声音，且仅 Qwen3.5 Omni Realtime 支持。其余 VAD 参数包括 `threshold` 与 `silence_duration_ms`；在线服务端事件页的会话示例还出现 `create_response` 与 `interrupt_response` 字段。

事实：本地交互流程说明 WebSocket 与 WebRTC 均支持 VAD 模式，且服务端事件一致。事件流程包含：`input_audio_buffer.speech_started`、`input_audio_buffer.speech_stopped`、`input_audio_buffer.committed`、`response.created`、`conversation.item.created`、`response.audio_transcript.delta`、`response.audio.delta`、`response.audio_transcript.done`、`response.audio.done`、`response.content_part.done`、`response.output_item.done`、`response.done`。WebRTC 下音频通过 RTP 传输，`response.audio.delta` 不作为音频输出载体。

事实：`response.cancel` 是客户端事件。官方在线客户端事件页说明它取消正在进行的响应，当前无响应可取消时服务端返回 `error`。Vision Agents Qwen 插件在收到 `input_audio_buffer.speech_started` 且 `_is_responding` 为真时调用 `cancel_response()`，随后清空本地 `_is_responding`、`_current_response_id` 与 `_current_item_id`。

未知：官方文档未发现 `response.cancelled` 事件。官方文档未发现取消后不会再到达旧 `response.audio.delta` 的保证。官方文档未发现取消场景中 `response.done` 是否一定返回、以及是否包含 cancelled 状态或 details 的完整合同。因此，response id 或 epoch 过滤在文档层面不是强制合同，但作为运行时防护仍有对象依据：Vision Agents 基类已经维护 epoch，且网络流式事件可能与客户端中断动作存在竞态。

## WebRTC Supplement

事实：Qwen Native WebRTC 通过 SDP over HTTP 建连。请求地址是 `POST https://{endpoint}/api/v1/webrtc/realtime?model={MODEL}`，`Content-Type` 为 `application/sdp`，鉴权头为 `Authorization: Bearer DASHSCOPE_API_KEY`，请求体是客户端 Offer SDP。成功响应为 HTTP 200，返回服务端 Answer SDP 字符串；失败响应为 HTTP 4xx，返回 JSON 错误信息。WebRTC 功能为白名单开放，需要获取 Endpoint。

事实：客户端示例创建 `RTCPeerConnection`，添加音频轨道以保证 Offer SDP 包含 `m=audio`，创建名为 `oai-events` 的 DataChannel 触发 SDP 协商；文档说明客户端 DataChannel 名称可自定义，服务端会通过固定名为 `txt` 的通道推送事件。Python 示例在收到服务端 `txt` 通道首条消息后，通过该通道发送 `session.update`。浏览器示例也通过 DataChannel 发送 `session.update`，会话配置使用 `input_audio_format: "pcm"`、`output_audio_format: "pcm"` 与 `input_audio_transcription.model: "qwen3-asr-flash-realtime"`。

事实：WebRTC 音频输入通过音频轨道 RTP 直接传输，图片通过视频轨道 RTP 传输；WebRTC 不支持手动模式，仅支持 `server_vad` 或 `semantic_vad`。模型音频输出通过 RTP 音频轨道接收与播放，不需要 `response.audio.delta`。控制指令与服务端事件通过 DataChannel 传输。

文档差异：接收模型响应章节写明 WebRTC text+audio 模式的文本通过 DataChannel 接收 `response.text.delta` 和 `response.text.done`；交互流程章节又写明响应过程中服务端通过 `response.audio_transcript.delta` 增量返回文字转录，且生命周期表也列出 `response.audio_transcript.done`。此处不能合并为单一事实。对于适配器合同，应保留两类文本事件处理，直到 live API 或更新文档给出唯一事件族。

## Voice Cloning / Voice Control Supplement

事实：声音复刻文档说明声音复刻与模型调用是两个独立但关联的步骤。创建音色通过 HTTP `POST https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization` 或国际地域对应 endpoint，`model` 固定为 `qwen-voice-enrollment`，`input.action` 为 `create`，`input.target_model` 指定驱动音色的全模态模型，`input.preferred_name` 指定名称关键字，`input.audio.data` 提供音频 data URI。支持的驱动模型包括 `qwen3.5-omni-plus-realtime` 与 `qwen3.5-omni-flash-realtime`。返回的 `output.voice` 可直接用于实时多模态接口的 `voice` 参数。文档明确 `target_model` 必须与后续调用 Omni 接口时的模型一致，否则合成失败。

事实：音频要求包括 WAV 16bit、MP3、M4A，推荐 10 到 20 秒，最长不超过 60 秒，文件小于 10 MB，采样率不低于 24 kHz，单声道，需包含至少 3 秒连续清晰朗读。声音复刻创建按音色计费，创建失败不计费；当前环境没有 API key，因此本次没有执行创建、查询或删除音色的 live API。

事实：本地 Qwen3.5 Realtime 文档把语音控制描述为自然语言能力：通过语音指令控制声音大小、语速和情绪，例如“语速快一些”“声音大一些”“用开心的语气”。未发现该能力对应的 session 字段、server event 或结构化状态回报。

推断：Vision Agents 适配层的 `voice` 字段应允许普通音色名和声音复刻返回的专属音色名；适配层不应把声音复刻创建过程内联到 Realtime 会话合同中。语音控制不产生当前已知的结构化事件面，不能作为事件处理覆盖项计入。

## Error Contract Supplement

事实：官方在线服务端事件页定义了 Realtime `error` 事件。事件顶层包含 `event_id`、`type: "error"` 与 `error` 对象；`error` 对象包含 `type`、`code`、`message`、`param`。示例错误为 `invalid_request_error`、`invalid_value`，`param` 指向 `session.modalities`。服务端事件页还说明 `session.update` 成功返回 `session.updated`，出错返回 `error`。客户端事件页说明 `input_audio_buffer.commit` 在音频缓冲区为空时返回错误事件，`response.cancel` 在无可取消响应时返回错误事件。WebRTC SDP 失败是 HTTP 4xx JSON。

事实：官方错误码页给出大量通用错误，包括不支持 `enable_search`、工具名不能为 `search`、模型不支持工具调用、WebSocket JSON 格式错误、`unsupported audio format:xxx`、鉴权、限流、内部错误、超时等。但已读错误码页不是 Qwen Realtime 专属枚举，不能逐项绑定到 U10 列出的所有 Realtime 错误场景。

未知：未发现无效 `input_audio_format` 或 `output_audio_format` 在 Qwen3.5 Realtime 中的精确 `error.code`；未发现无效 `input_audio_transcription.model` 的精确 code；未发现先发送图片再发送音频时的精确 code；未发现无效工具 schema、工具结果错误、`enable_search` 与 `tools` 同时开启、120 分钟会话关闭的专属 code 与可恢复性说明。Vision Agents 当前 Qwen 插件只把 `error` 转为通用异常事件，未保留 `error.code`、`error.param` 与 `event_id` 的结构化字段。

## Impact On The Vision Agents Adapter Coverage Matrix

1. Function Calling 覆盖项从“协议未知”改为“官方合同已知，Qwen 插件未实现”。新增缺口包括 tools 注入、Qwen 工具事件解析、工具参数 JSON 解析、FunctionRegistry 调用、工具结果回传、工具后 `response.create`、工具调用输出项归一化、搜索互斥校验。

2. Audio Format 覆盖项从“格式字符串不确定”拆为两项。官方原生合同项已解析为 `pcm`；当前 Vision Agents 插件值 `pcm16`/`pcm24` 是本地代码事实，与官方合同不一致。服务端是否宽容接受属于 live API 未知项，不应再覆盖官方合同判断。

3. ASR 模型覆盖项从“`gummy-realtime-v1` 是否有效”拆为两项。Qwen3.5 官方目标是 `qwen3-asr-flash-realtime` 且不支持修改；Vision Agents 默认与官方目标不一致。旧 speech demo 只证明旧模型示例使用 `gummy-realtime-v1`，不证明 Qwen3.5 兼容。

4. Search 覆盖项新增互斥约束。适配器不能把 `enable_search` 与 `tools` 同时发送到 Qwen Realtime 会话。`usage.plugins.search` 应作为 Qwen 专属 usage 扩展保留，否则搜索用量会丢失。

5. WebRTC 覆盖项从“基础协议未知”改为“基础协议已知，专门样例不足”。已知面包括白名单 endpoint、SDP HTTP 交换、`txt` DataChannel、DataChannel 传输控制事件、RTP 音频输出、WebRTC 仅 VAD 模式。剩余差异是 text+audio 文本事件族与工具/搜索 WebRTC 样例。

6. Cancellation 覆盖项保留为运行时健壮性缺口。官方确认 `response.cancel` 与错误返回，但没有确认 stale delta 绝不出现。Vision Agents core 已有 epoch 字段，Qwen 插件还没有使用 response id/epoch 过滤音频和转录增量。

7. Voice cloning 覆盖项从“会话字段未知”改为“外部创建音色 + Realtime voice 使用”。适配器合同只需要接受 `voice` 字符串；创建、查询、删除音色属于另一个 HTTP API 面。

## Still-Unknown List With Exact Blockers

U1 的 live 兼容性仍未知：需要有效 `DASHSCOPE_API_KEY`，并向 Qwen3.5 Realtime `session.update` 分别发送 `pcm16`/`pcm24` 与 `pcm`，观察 `session.updated` 或 `error`。当前环境没有 key。

U2 的旧 ASR 模型兼容性仍未知：需要有效 `DASHSCOPE_API_KEY`，并在 Qwen3.5 Realtime 中发送 `input_audio_transcription.model: "gummy-realtime-v1"`，观察服务端是否拒绝。当前环境没有 key，且官方合同已经写明 Qwen3.5 固定为 `qwen3-asr-flash-realtime`。

U3 的 WebRTC 工具调用样例仍缺失：需要官方 WebRTC Function Calling 示例或白名单端点 live 测试，确认 `response.function_call_arguments.*` 是否经 `txt` DataChannel 传输，以及工具结果 `conversation.item.create` 是否同样通过该 DataChannel 回传。

U4 的 WebRTC 搜索完整载荷仍缺失：需要官方 WebRTC search 示例或 live 测试，确认搜索来源列表和 `usage.plugins.search` 在 WebRTC `response.done` 中的完整结构。

U5 的语义 VAD 细粒度行为仍未知：需要官方说明或可重复 live 测试，覆盖回应语、背景音、用户打断、模型正在输出时的语义判定边界。

U6 的 stale delta 保证仍未知：需要官方声明或 live 测试，确认 `response.cancel` 后是否可能继续收到旧 `response.audio.delta`、`response.audio_transcript.delta` 或 `response.done`。

U8 的 text+audio 文本事件族仍存在文档差异：需要官方更正文档或 live WebRTC 测试，确认 text+audio 模式下 DataChannel 文本事件使用 `response.text.*`、`response.audio_transcript.*`，或两者按场景共存。

U9 的声音复刻 live 行为未验证：需要 API key、可计费授权和合规音频样本。计划限制下未执行创建音色。语音控制没有结构化事件证据。

U10 的 Realtime 专属错误枚举仍未知：需要官方错误码细表或逐项 live 负向测试。当前只确认通用 `error` 事件形状与部分通用错误码。

## Evidence List

本地官方文档：

- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen-Omni-Realtime 系列-全模态模型的工具调用.md`：Qwen3.5 工具调用支持、`session.update` 注入工具、`response.function_call_arguments.done`、`conversation.item.create`、`response.create`、不支持 `tool_choice` 与 `parallel_tool_calls`、SDK enum 示例。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime-API.md`：`pcm` 音频格式、`qwen3-asr-flash-realtime`、WebSocket/WebRTC 输入输出、VAD 流程、搜索配置、搜索 usage、WebRTC SDP 与 DataChannel、错误码委托。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/Qwen3.5-Omni-Flash-Realtime.md`：模型能力背景与 Realtime 使用说明。
- `/home/t103o/workbench/micheng-ts/projects/TideSync/docs/deep-research/03-Qwen35-Omni-Realtime-Vision-Agents-完整适配缺口调查报告.md`：上一轮覆盖矩阵与未知项基线。

本地代码：

- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py`：当前 Qwen session 配置、`pcm16`/`pcm24`、`gummy-realtime-v1`、事件处理和取消逻辑。
- `/home/t103o/workbench/external/Vision-Agents/plugins/qwen/vision_agents/plugins/qwen/client.py`：WebSocket client、`session.update`、audio append、image append、`response.cancel`、重连 close code。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/llm/realtime.py`：Realtime 基类的后台工具任务、epoch、中断和输出事件抽象。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/llm/function_registry.py`：FunctionRegistry、ToolSchema 生成、注册函数执行。
- `/home/t103o/workbench/external/Vision-Agents/agents-core/vision_agents/core/llm/llm_types.py`：NormalizedToolCallItem、NormalizedToolResultItem、ToolSchema 与 NormalizedResponse 类型。
- `/home/t103o/workbench/external/alibabacloud-bailian-speech-demo/samples/conversation/omni/python/run_server_vad.py`：旧模型 `qwen-omni-turbo-realtime-latest` 的 SDK enum 与 `gummy-realtime-v1` 示例。
- `/home/t103o/workbench/external/alibabacloud-bailian-speech-demo/samples/conversation/omni/python/run_with_camera.py`：旧模型视频示例中的相同 ASR 配置。

官方在线来源：

- `https://help.aliyun.com/zh/model-studio/client-events`：`session.update` 字段、`tools` schema、`enable_search`、`search_options`、`response.create`、`response.cancel`、`conversation.item.create`。
- `https://help.aliyun.com/zh/model-studio/server-events`：`error` 事件形状、`response.function_call_arguments.delta`、`response.function_call_arguments.done`、`response.output_item.*`、`response.done` 中的 `function_call` 输出项。
- `https://help.aliyun.com/zh/model-studio/qwen-omni-voice-cloning`：声音复刻 HTTP API、`qwen-voice-enrollment`、`target_model`、`voice` 结果、Qwen3.5 Realtime 驱动模型、计费与音频要求。
- `https://help.aliyun.com/zh/model-studio/error-code`：通用错误码、工具与搜索相关通用错误、WebSocket 通用错误。

环境证据：

- `DASHSCOPE_API_KEY_SET False`。
- TideSync 环境中 `dashscope_import_error ModuleNotFoundError No module named 'dashscope'`。

## 适配契约增量

Qwen Realtime 会话配置使用官方原生 JSON 音频格式值 `pcm`；采样率约束由数据流承担：输入音频为 16 kHz 单声道 16-bit PCM，输出音频为 24 kHz 单声道 16-bit PCM。

Qwen3.5 Realtime 输入音频转录配置使用 `input_audio_transcription.model: "qwen3-asr-flash-realtime"`；适配器不得把旧模型示例中的 `gummy-realtime-v1` 作为 Qwen3.5 的合同默认值。

Qwen 工具定义由 Vision Agents `ToolSchema` 映射为 `{"type":"function","function":{"name":...,"description":...,"parameters":...}}`，并放入 `session.update.session.tools`。

Qwen 工具调用事件处理以 `response.function_call_arguments.done.arguments` 为完整参数源；`response.function_call_arguments.delta` 只作为增量观察或调试状态，不作为最终参数依据。

Qwen 工具调用结果通过 `conversation.item.create` 回传，`item.type` 为 `function_call_output`，`item.call_id` 等于服务端工具调用事件的 `call_id`，`item.output` 为工具执行结果字符串；回传后用 `response.create` 触发最终回答。

Qwen Realtime 适配器不发送 `tool_choice` 与 `parallel_tool_calls`。

Qwen Realtime 适配器对 `tools` 与 `enable_search` 执行互斥约束；同一会话配置不得同时启用二者。

Qwen 搜索配置由 `enable_search` 与 `search_options.enable_source` 表达；搜索计量保留 `response.done.usage.plugins.search` 的原始结构。

Qwen VAD 事件处理同时接受 `server_vad` 与 `semantic_vad` 配置；两者共享 `speech_started`、`speech_stopped`、`committed` 与响应生命周期事件处理。

Qwen 取消处理以 `response.cancel` 作为客户端事件；流式输出处理保留 response id 或 epoch 过滤能力，以屏蔽取消或打断后到达的旧响应增量。

Qwen WebRTC 适配的控制事件经服务端 `txt` DataChannel 传输，音频输入和输出经 RTP 轨道传输；WebRTC 模式不依赖 `response.audio.delta` 播放输出音频。

Qwen WebRTC 文本事件处理同时接受 `response.text.*` 与 `response.audio_transcript.*`，直到官方合同消除 text+audio 模式事件族差异。

Qwen `voice` 配置接受官方音色名和声音复刻接口返回的专属音色名；声音复刻创建、查询、删除属于独立 HTTP API，不属于 Realtime 会话内联字段。

Qwen `error` 事件以结构化对象保留 `error.type`、`error.code`、`error.message`、`error.param`；适配器事件层不得只保留格式化字符串。
