# TideSync Qwen Omni Harness 调试前端完整蓝图汇报

## 一、当前证据面

本次汇报合并了四类已经形成证据的材料。第一类是黑盒测试聊天记录，它回答“测试者在 live 环境中到底要触发什么”：基础语音链路、中文多轮语义、视频理解、音频加视频联合理解、barge-in 打断、静音不误触发、长回答完成边界、退出流程。第二类是 `qwen-smoke-20260614-151000.log`，它回答“真实运行中已经观察到什么”：agent 启动、warmup、加入 GetStream call、用户进入 call、中文用户转写、Qwen 回复、视频 track 加入、1 FPS 视频转发、视觉问答、视频 track 移除和重连、用户离开。第三类是 Hegel 的《TideSync Qwen Omni 调试前端依赖与 SDK 事实交叉验证报告》，它回答“浏览器端和前端依赖到底是什么”：GetStream Video React SDK、GetStream low-level video client、Stream Chat 包名、Vision Agents 当前暴露给浏览器的边界、Qwen 文档能力分类、官方 zipball 可借鉴元素与不可照搬原因。第四类是最新的《TideSync 自研 Qwen Omni 调试前端调查与设计汇报》，它回答“这个前端作为人工制品是什么”：它不是实验、不是 getstream.io demo 换皮、不是去年 Qwen zipball 的直连 WebSocket 页面，而是 TideSync Qwen Omni Harness 的开发者调试控制台。

这里的核心判断是：模型本身的知识质量、ASR 误听率、语音自然度、视觉识别上限属于基座模型能力；TideSync 要负责的是 Harness 与 Agent 环境。Harness 的职责不是保证模型一定答对“紫微斗数”，而是保证用户音频和视频以正确方式进入模型，Qwen session 配置按开发者声明生效，模型输出被可观察地投射出来，barge-in、转写、响应、工具、搜索、usage、错误和退出状态能被开发者检查。换句话说，TideSync 前端不评价模型聪明不聪明；它评价“模型潜力有没有被正确激发，链路有没有挡住模型，失败发生在哪一层”。

15:10 live smoke 已经证明主链路成立。日志显示：agent 能启动并加入 `default/tidesync-qwen-smoke`；用户进入 GetStream call 后，音频轨道被订阅；用户说“你好呀，你是谁呢？”、“权威这个词是什么意思呢？”、“它和玄妙有什么区别呢？”等语句后，日志中出现对应中文 user transcript 和 agent transcript；15:11:44 出现 `Track added: VIDEO from user-demo-agent` 与 `Started video forwarding with 1 FPS`；随后用户问“画面里有什么呀？”，agent 回答“银灰色的 CUKTECH 充电宝、白色充电线、蓝边鼠标垫、手、电脑显示器”；用户问“现在手指指向了什么呀？”，agent 回答“黑色的联想鼠标”；视频轨道移除与重新加入也被日志记录。这些事实说明：GetStream 浏览器媒体、Vision Agents Python edge、Qwen Realtime adapter、DashScope WebSocket、音频输出回流这条主链路已经能真实工作。

这次 smoke 也暴露了设计必须处理的观察缺口。`Browser opened successfully` 后紧接着出现 `gio: Operation not supported`，说明 WSL 自动打开浏览器的投影不干净；“No participants joined after 10.0s timeout” 后又出现 audio track subscription，说明 participant join 与 track subscription 的日志语义需要分层；INFO 日志中 agent transcript delta 逐字逐词刷屏，导致人工读日志成本极高；“紫微斗数”被回答成“豆数”是模型语义或 prompt 控制问题，不是链路失败，但它需要进入测试记录以区分模型能力与 Harness 责任；视频重连后回答“画面全黑”需要同时观察浏览器本地预览和 agent forwarding 状态，不能只看模型回答。

由这些证据推出的对象定义是：TideSync Qwen Omni 调试前端是一个开发者控制台，用于创建、配置、运行、观察和结束一次基于 GetStream call、Vision Agents Python agent、Qwen Realtime WebSocket adapter 的全模态会话。它的公共消费者是调试者，不是普通聊天用户。调试者的行动是：选择 Qwen 能力配置，启动受控会话，浏览器加入 call，发布麦克风与摄像头，触发黑盒测试话术，观察实时状态和事件，定位失败层，导出证据，结束会话。

## 二、架构蓝图

TideSync 当前架构的主链路是四层对象。

第一层是浏览器。浏览器只承担人类参与者身份、设备权限、麦克风/摄像头发布、agent 音频接收、调试 UI 展示、控制命令发起和证据查看。浏览器不持有 DashScope API key，不直接连接 Qwen WebSocket，不执行后端工具，不创建 Stream secret token。

第二层是 GetStream。GetStream 承担实时 call 的 WebRTC 媒体传输。浏览器作为 human participant 加入 call，Python agent 作为 agent participant 加入同一个 call。浏览器通过 GetStream browser token 和 apiKey 连接；Stream API secret 只在后端签 token 时使用。GetStream call events 或 custom events 可承载轻量 agent 状态，但大 payload 与审计日志不应依赖 5KB custom event 限制。

第三层是 TideSync/Vision Agents 后端。该层负责签发 human token、创建或复用 call、启动 agent session、把 Qwen 配置注入 agent、关闭 session、暴露 metrics、推送结构化调试事件。Vision Agents 当前已经提供 Runner HTTP API：`POST /calls/{call_id}/sessions`、`DELETE /calls/{call_id}/sessions/{session_id}`、`POST /close`、`GET session`、`GET metrics`、`/health`、`/ready`。但该 API 的 `StartSessionRequest` 当前只包含 `call_type`，不能承载 Qwen 的 model、voice、instructions、VAD、fps、includeVideo、tools、search。由此推出：TideSync 前端不能只接原生 Runner API，它需要 TideSync 专属控制 API 包装 Runner 与 AgentLauncher。

第四层是 Qwen Realtime adapter。该层运行在 Python agent 内部，负责连接 DashScope Qwen WebSocket，发送 `session.update`，转发音频 PCM 与视频帧，处理 Qwen response lifecycle，投射用户转写、助手转写、音频输出、工具调用、搜索 usage、错误、打断和重连状态。浏览器看到的是该层状态的投影，不是直接操作该层。

因此，完整控制 API 的核心契约应当是：

`POST /api/qwen-omni/sessions` 创建一次调试会话。请求体包含 call 与 human 参数、Qwen session 参数、媒体参数、工具/搜索参数、观测参数。响应体返回 `call_id`、`session_id`、`call_type`、Stream `apiKey`、human `userId`、human `token`、token 过期时间、后端配置快照、事件订阅端点、metrics 端点。

`DELETE /api/qwen-omni/sessions/{session_id}` 结束会话。结束不是单纯离开网页，而是要求 agent 停止音频 consumer/producer、停止视频 forwarding、关闭 Qwen realtime 连接、离开 GetStream call、flush pending conversation sync，并给前端返回最终关闭状态。

`GET /api/qwen-omni/sessions/{session_id}` 返回当前 session snapshot，包括 created/running/closing/ended/error、call participant 状态、agent 状态、Qwen realtime 状态、最近事件时间、配置快照。

`GET /api/qwen-omni/sessions/{session_id}/metrics` 返回数值指标：turn 数、barge-in 次数、track add/remove 次数、最后视频帧时间、agent first token/audio 延迟、response 完成耗时、错误数、usage/search usage。

`GET /api/qwen-omni/sessions/{session_id}/events` 以 SSE 或 WebSocket 推送结构化事件。SSE/WS 负责高信噪调试事件；GetStream custom call event 只承担 call 内轻量状态广播。

`POST /api/qwen-omni/sessions/{session_id}/commands` 承载需要从前端发给 agent 的控制命令，例如 manual mode commit/create response、clear audio、force reconnect、snapshot request、mark test step。没有该命令通道时，Manual 只能作为后端能力展示，不能伪装成可用 UI 开关。

这个 API 契约的结论来自现有事实，不是个人偏好：Runner 原生 API 不透传 Qwen 配置；Qwen session.update 由后端 adapter 发送；浏览器不能拿 DashScope key；GetStream token 需要后端签发；开发者调试需要结构化事件，而不是事后读 460 行原始日志。

## 三、前端依赖与 SDK

浏览器加入 GetStream call 的 React 主依赖是 `@stream-io/video-react-sdk@1.37.7`。Hegel 已核查 npm registry 与 GetStream 官方文档：该包来自 `GetStream/stream-video-js`，peer 支持 React 17/18/19，依赖中包含 `@stream-io/video-client@1.53.2`。它承担 React provider、call context、hooks、设备控制、参与者布局和通话组件。

低层 GetStream Video client 是 `@stream-io/video-client@1.53.2`。它承担 call watch/query、call events、custom events、底层连接状态和可观察对象。若 React SDK 暴露的对象不足以支撑调试事件订阅，前端应显式引入该包。这个包不是可有可无的概念依赖，它对应的是开发者调试台必须观察 call state 与 custom events 的事实需求。

聊天包名是 `stream-chat@9.46.0` 与 `stream-chat-react@14.4.1`。它们只在 TideSync 把 Stream Chat channel/message 作为会话记录或旁路 transcript 表面时进入运行依赖。若 transcript、events、summary 完全由 TideSync 后端事件流提供，则 Chat SDK 不进入主前端运行依赖。这里的边界是对象职责：GetStream Video 是媒体层必需对象；Stream Chat 是消息表面候选对象，不是 Qwen Harness 的构成性条件。

React 应用栈采用外层 workspace 已有能力作为参考，并使用现代主流依赖：React `^19.2.5`、React DOM `^19.2.5`、Vite `^8.0.10`、`@vitejs/plugin-react ^6.0.1`、TypeScript `^6.0.3`、Tailwind CSS `^4.2.4`、`@tailwindcss/vite ^4.2.4`、`tailwind-merge ^3.5.0`、`clsx ^2.1.1`。服务端状态使用 `@tanstack/react-query ^5.100.9`，路由使用 `@tanstack/react-router ^1.169.1`，表单使用 `react-hook-form ^7.75.0`、`@hookform/resolvers ^5.2.2`、`zod ^4.4.3`。图标使用 `lucide-react ^1.14.0`，toast 使用 `sonner ^2.0.7`，状态转场使用 `motion ^12.38.0`。

无头组件库进入核心设计。控件不手写交互逻辑。Radix primitives 覆盖 checkbox、dialog、dropdown menu、label、select、separator、slot、switch、tabs、tooltip。具体包包括 `@radix-ui/react-checkbox ^1.3.3`、`@radix-ui/react-dialog ^1.1.15`、`@radix-ui/react-dropdown-menu ^2.1.16`、`@radix-ui/react-label ^2.1.8`、`@radix-ui/react-select ^2.2.6`、`@radix-ui/react-separator ^1.1.8`、`@radix-ui/react-slot ^1.2.4`、`@radix-ui/react-switch ^1.2.6`、`@radix-ui/react-tabs ^1.1.13`、`@radix-ui/react-tooltip ^1.2.8`。这些包对应真实表面单位：voice select、VAD segmented/radio、search/tools switch/radio、settings dialog、event tabs、icon tooltips、filter dropdown、session close confirmation。

验证依赖包括 `@playwright/test ^1.59.1`、`playwright ^1.59.1`、`@biomejs/biome ^2.4.15`、`vitest ^4.1.5`、Testing Library、`happy-dom ^20.9.0`、`msw ^2.14.2`。Playwright 验证浏览器权限、通话页面加载、布局不遮挡、设备按钮状态、事件面板、导出动作。Vitest 与 MSW 验证配置 schema、API hooks、event reducer、metrics formatting、search/tools 互斥规则。

## 四、界面蓝图

第一屏就是调试控制台，不是 landing page。页面采用四区结构：顶部 Session Bar、左侧 Config Rail、中央 Call Surface、右侧 Evidence Panel，并在会话结束后显示 Summary/Export Surface。

顶部 Session Bar 是全局事实投影。它显示 TideSync 标识、backend health、Runner ready、Stream call 状态、agent session 状态、Qwen realtime 状态、elapsed time、call id、session id、配置快照按钮、结束按钮。这里的状态不使用含混文案，而使用稳定状态集：`idle`、`preparing`、`joining_call`、`waiting_participant`、`listening`、`watching`、`processing`、`responding`、`interrupted`、`reconnecting`、`limited`、`error`、`closing`、`ended`。这些状态对应已有 08 号实时体验规范中的 public states，也对应 Qwen adapter 与 GetStream track 事件。

左侧 Config Rail 是 Qwen 与 Harness 配置面。它包含 model、voice、custom voice id、instructions、turn detection、VAD params、include video、fps、video size、search/tools mode、toolset 选择、session label。model 默认 `qwen3.5-omni-flash-realtime`。voice 支持预置音色下拉与自定义 voice id 文本框。instructions 是开发者可编辑 textarea。turn detection 使用 `server_vad`、`semantic_vad`、`manual` 三选一；Qwen3.5 推荐 semantic VAD，前端可把 semantic 作为默认配置，但显示的不是“建议”，而是“当前配置值”。Manual 需要后端命令通道支持；命令通道缺失时，Manual 显示为不满足运行前置条件，而不是伪装成可用功能。fps 默认 1，因为 Qwen 文档和当前 agent 默认均指向 1 FPS 视频抽帧。search/tools 使用互斥控件：`None`、`Web Search`、`Tools`。选择 Web Search 时显示 search options 与 usage 预期；选择 Tools 时显示后端已注册工具 schema，不允许浏览器注入任意可执行函数。

中央 Call Surface 是开发者和 agent 的实时工作面。它显示本地视频预览、远端/agent 音频状态、agent 状态圆环、麦克风按钮、摄像头按钮、屏幕共享按钮、重连按钮、结束按钮。官方 zipball 的 voice orb 可以作为状态隐喻，但不能成为页面主体。调试台的主体是观察与控制。中央区域还要显示视频 forwarding 状态：browser camera active、Stream video published、agent track added、Qwen forwarding active、target fps、last frame age。这样 15:13 那种“模型说全黑”就能现场判断是浏览器预览黑、Stream track 黑、agent forwarding 黑，还是模型理解错。

右侧 Evidence Panel 是调试台的核心。它使用 tabs：Transcript、Events、Metrics、Tools/Search、Errors、Raw。Transcript 区分 user transcript delta/final、assistant audio transcript delta/final、conversation record、被打断的旧 response。Events 显示结构化 timeline，可按 track、speech、response、tool、search、error、session 过滤。Metrics 显示 turn latency、first transcript latency、first response latency、barge-in count、track uptime、last frame age、usage tokens、search usage。Tools/Search 显示工具调用 name、arguments、call_id、output、duration、success/error；搜索显示 search count、strategy、source 开关状态。Errors 显示 Qwen structured error 的 type/code/message/param、recoverability、impact scope；也显示 GetStream join、token、track、browser permission、backend API 错误。Raw 区显示原始事件 JSON，便于复制给开发者或测试报告。

会话结束后的 Summary/Export Surface 是证据产物。它输出 markdown 与 JSON：启动配置快照、call id、session id、时间范围、参与者轨道变更、用户 final transcript 列表、agent final transcript 列表、barge-in 次数、视频 forwarding 时间段、工具/搜索 usage、错误列表、退出状态、原始日志路径。这个表面解决当前问题：我们不再要求人从 460 行或 669 行原始日志中手动提取证据。原始日志仍然保留，summary 成为人工审阅入口。

## 五、状态与事件模型

调试前端的事件模型不能只显示字符串日志。它应定义稳定类型。

Session 事件：`session.created`、`session.starting`、`session.ready`、`session.closing`、`session.closed`、`session.error`。

Call 事件：`call.joining`、`call.joined`、`participant.joined`、`participant.left`、`track.added`、`track.removed`、`track.unpublished`、`call.reconnecting`、`call.reconnected`。

Media 事件：`microphone.enabled`、`microphone.disabled`、`camera.enabled`、`camera.disabled`、`video.forwarding.started`、`video.forwarding.stopped`、`video.frame.sent`、`video.frame.dropped`、`audio.input.active`、`audio.output.active`。

Qwen/VAD 事件：`input_audio_buffer.speech_started`、`speech_stopped`、`committed`、`response.created`、`response.output_item.added`、`response.content_part.added`、`response.audio_transcript.delta`、`response.audio_transcript.done`、`response.audio.delta`、`response.audio.done`、`response.text.delta`、`response.text.done`、`response.done`、`response.cancelled`。

Interruption 事件：`barge_in.detected`、`response.cancel.requested`、`stale_response.delta_blocked`、`audio_output.flushed`、`interruption.completed`。这组事件对应 09 号书和 adapter 的 interruption/stale response 语义。没有这些投影，就无法判断“用户插话后旧回答是否真的让位”。

Tool/Search 事件：`tool.schema.declared`、`tool.call.arguments_delta`、`tool.call.arguments_done`、`tool.output.sent`、`tool.call.failed`、`search.enabled`、`search.usage.reported`。工具与搜索互斥由配置 schema 和后端 adapter 双层执行。

Error 事件：`qwen.error`、`stream.error`、`runner.error`、`browser.permission_denied`、`token.expired`、`session.limit_reached`、`metrics.stale`。错误必须有 source、code、message、recoverability、impact scope、raw payload。错误不是 toast 一闪而过；错误是证据面的一等对象。

该模型直接吸收了已有 spec 中的公共投影要求：用户可见反馈必须反映实际状态；用户 transcript、AI caption、conversation record 要区分；工具参与、权限、结果、action、cost 必须可见；错误和限制不能被吞掉。

## 六、Qwen 能力映射

音频输入与语音输出：浏览器发布麦克风轨道到 GetStream，agent 接收 audio PCM，Qwen adapter append audio，Qwen 输出 audio/text，agent audio output 回到 GetStream。前端展示 mic state、user speech state、assistant speaking state、audio done、interrupted。

视频输入：浏览器发布摄像头轨道，agent track added 后按配置 fps 抽帧转发给 Qwen。前端展示 browser preview、Stream track、agent forwarding、last frame age、track reconnect。视频不是浏览器直接发 JPEG 给 Qwen；去年 zipball 的 `/ws` JPEG 直传不进入 TideSync 主架构。

VAD：`server_vad` 与 `semantic_vad` 是可运行配置。Qwen3.5 文档推荐 semantic VAD，因此默认配置值使用 semantic VAD。VAD 参数进入 session config。前端展示 speech started/stopped/committed 和 turn boundary。

Manual：Manual 是 Qwen WebSocket 能力，也是 adapter 内已有 commit/create response 能力；在 TideSync Harness 中，它还需要前端到 agent 的命令通道和 agent 端输入窗口控制。该前置条件必须在蓝图中成为契约，不得用一个单独 toggle 伪装完成。

Voice：voice 是 Qwen session 配置。前端提供预置 voice 与自定义 voice id。声音复刻创建流程不属于主调试控制台；主控制台只使用已有 voice 标识。

Tools：工具由后端注册，前端选择工具集、查看 schema、观察调用。工具执行在后端 agent，不在浏览器。前端展示 function call arguments、call_id、output、error、final response。

Search：搜索由 `enable_search` 与 search options 控制。搜索与工具互斥。前端展示 search usage 与 source 开关状态。

Usage：Qwen response done 中的 usage、token details、plugins.search 进入 Metrics 与 Raw。usage 不应埋在日志里。

Model quality：知识问答、视觉识别、ASR 准确度、语音自然度属于基座模型表现。前端提供测试脚本与证据记录，不承担修正模型知识的责任。紫微斗数失败进入测试记录，而不是被归类为 Harness 失败。

## 七、官方 zipball 的位置

`tmp/omni-realtime_zipball_0.0.3` 是 UI 与交互参考，不是架构参考。它提供可借鉴的表面单位：voice selector、状态指示器、本地视频预览、voice orb、麦克风/摄像头/重连/结束按钮、history、interrupt、timer、音频队列状态。它的架构是浏览器采集 PCM/JPEG，通过本地 FastAPI WebSocket `/ws` 发给后端，再由后端直连 Qwen WebSocket。这个架构绕过 GetStream call、Vision Agents runner、Qwen adapter 的工具/搜索/usage/interruption 投影，也绕过当前 TideSync 已经验证的 live 主链路。

因此，TideSync 前端复用 zipball 的交互对象，不复用 zipball 的通信结构。页面视觉可以保留“实时语音状态中心”的直观性，但布局必须变成开发者控制台：配置、通话、证据、导出四个构成条件同时存在。没有 Evidence Panel 的页面只是通话页；没有 Config Rail 的页面不能体现 Qwen Omni 能力；没有后端控制 API 的页面仍然依赖 getstream.io demo；没有 Summary/Export 的页面不能支撑黑盒测试闭环。

## 八、完整性结论

TideSync Qwen Omni 调试前端的完整蓝图不是“先做一个轻量页面”。它作为人工制品成立，需要四个构成性条件同时进入设计：会话控制、能力配置、实时通话、证据投影。

会话控制保证开发者能创建、运行、观察、关闭一次受控 agent session，并且浏览器只拿 human Stream token。能力配置保证 Qwen 的 model、voice、instructions、VAD、video fps、search/tools、toolset 等能力按声明进入后端 adapter。实时通话保证人类通过 GetStream 与 agent 共享音视频现场，agent 把音视频输入转发给 Qwen，并把 Qwen 输出回到 call。证据投影保证调试者在当下看到 user transcript、assistant transcript、track、barge-in、response lifecycle、tool/search、usage、error、metrics、raw payload，并在会话结束后得到可复现 summary。

Vision Agents 没有提供浏览器 SDK。它提供 Python agent runtime、Runner HTTP API、GetStream edge、events、metrics 和 Qwen plugin。浏览器端使用 GetStream Video SDK；后端使用 TideSync 控制 API 包装 Vision Agents；Qwen 连接在 agent 内部完成。这个分层是事实推出的架构，不是风格偏好。

最终设计对象是一套开发者友好的全模态 Harness 调试控制台。它让模型的语音、视觉、搜索、工具、打断、usage、错误和退出行为都能被触发、观察、记录和复盘。它不替模型变聪明，不把基座模型上限误归责给 Harness；它保证 Harness 不遮挡模型能力，并把每一次失败准确落到浏览器、GetStream、Vision Agents、Qwen adapter、DashScope 服务、工具执行或模型本身中的对应层。
