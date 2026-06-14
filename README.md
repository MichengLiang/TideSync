# TideSync

TideSync 是围绕“AI 视觉对话助手”题目构建的实时全模态语音视频会话项目。它的当前运行路径使用 GetStream 承载用户与 agent 的 WebRTC 通话，使用 Vision Agents 承载 Python agent runtime，并通过 TideSync 仓库内受控的 Qwen3.5 Omni Realtime WebSocket adapter 接入阿里云 DashScope `qwen3.5-omni-flash-realtime`。

我按照题目原文的的描述，重新梳理推导了需求：语音输入、当前视觉现场、自然语音回应、可打断对话、状态投影、工具调用、联网搜索、usage 计量、错误恢复和证据材料进入同一条可审查的工程链路。
题目原文见 [docs/题目原文.md](docs/%E9%A2%98%E7%9B%AE%E5%8E%9F%E6%96%87.md)。
我使用了详细的文档来定义“AI 视觉对话助手”指的是什么，怎么样才成立，才被称之为此，8号书籍详细描述了需求与形状 [08 号书](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/book.adoc)，我复用了vision agents基础设施，调查研究后发现当前版本的vision agents对 Qwen adapter 为基础支持，包括但不限于不支持打断等一些基本需要，我按照8号书籍的需求形状详细摊开描述了现状与期望的变化 [09 号书](docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc)。

在[原始聊天记录](docs/raws)记录了想法到正式文档的形成。


## 题目理解

题目要求开发一款与 AI 对话的应用：打开摄像头与麦克风，让 AI 能看到视频内容、听到用户说话并给予回应，同时考虑视觉理解准确性、语音交互自然度与流畅性、端云协同成本控制策略，并额外提交设计文档说明计划和最终实现的用户故事，以及成本控制技巧。

我把它重述为实时全模态视频通话体验：用户在同一会话中通过麦克风提供语音，通过摄像头或等价视觉输入提供当前视觉现场，由 AI 以自然语音对语音内容、视觉现场和会话上下文作出连续回应。这个体验至少包含七个构成性条件：

- 实时语音输入。
- 当前视觉现场参与。
- 语音和视觉属于同一会话语境。
- AI 以自然语音承担主要回答。
- 用户可以在 AI 回答期间打断或纠正。
- 同一会话内的语音、视觉和回应历史可以被合理承接。
- 采集、处理、回应、错误和限制状态能够被用户观察。

这些条件来自 [08 号书的对象身份与构成性条件](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/parts/100-object-boundary/010-artifact-identity.adoc)。它们用于区分 TideSync 要做的对象与相邻对象：只听不看的语音助手、只上传单张图片的图片问答、只转发人类音视频的视频会议、只展示数字人形象的表达层 demo，都不能单独满足这个题目。

## 当前系统链路

当前 TideSync 主链路由四层组成：

```text
Browser / GetStream demo
  -> GetStream WebRTC call
  -> Vision Agents Runner + Python agent
  -> TideSync-controlled Qwen WebSocket adapter
  -> DashScope Qwen3.5 Omni Flash Realtime
```

浏览器侧负责人类参与者身份、麦克风和摄像头发布、agent 音频接收以及基础通话表面。当前可借助 Vision Agents / GetStream 的托管 demo 访问通话页面；TideSync 专属 Qwen Omni Harness 前端仍处于设计阶段，设计基线见 [docs/deep-research/05-TideSync Qwen Omni 调试前端完整蓝图汇报.md](docs/deep-research/05-TideSync%20Qwen%20Omni%20%E8%B0%83%E8%AF%95%E5%89%8D%E7%AB%AF%E5%AE%8C%E6%95%B4%E8%93%9D%E5%9B%BE%E6%B1%87%E6%8A%A5.md)。

GetStream 承担用户与 Python agent 之间的实时媒体传输。Vision Agents 的 `Runner`、`Agent`、`Edge` 和 realtime flow 承担 agent 生命周期、音频消费、视频转发、语音输出和 core event 投影。TideSync 的入口在 [src/tidesync/agent.py](src/tidesync/agent.py)：它默认使用 `qwen3.5-omni-flash-realtime`、中国内地 DashScope WebSocket 地址、`Tina` 音色、`fps=1`，并固定 `include_video=True`。

Qwen adapter 运行在 Python agent 内部。它负责把 Vision Agents 收到的音频与视频转换为 Qwen WebSocket client events，把 Qwen 服务端返回的音频、转写、VAD、响应生命周期、工具调用、搜索 usage、错误和重连事件投射回 Vision Agents core。

当前 TideSync 完成的是 Qwen WebSocket adapter，不是 Qwen 原生 WebRTC transport。GetStream WebRTC 是用户到 Vision Agents 的媒体层；Qwen 原生 WebRTC 的 SDP、RTP 和 DataChannel 是另一个相邻 transport，不属于当前完成对象。这个边界在 [09 号书的系统边界](docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/parts/100-object-boundary/040-system-boundary.adoc)中有正式定义。

## 当前实现状态

| 对象 | 状态 | 说明 |
|---|---|---|
| Python agent 入口 | 已实现 | [src/tidesync/agent.py](src/tidesync/agent.py) 创建 Vision Agents `Runner`，通过 GetStream `Edge` 加入 call，并使用 Qwen realtime provider。 |
| Qwen3.5 Omni 默认配置 | 已实现 | 默认模型、base URL、音色和 FPS 由 `RealtimeSettings` 管理，测试见 [tests/test_hello.py](tests/test_hello.py)。 |
| 受控 Vision Agents runtime fork | 已实现 | 来源为 GetStream Vision Agents `v0.6.4`，commit `9c5efe1...`，记录见 [forks/vision-agents-qwen-native/UPSTREAM.adoc](forks/vision-agents-qwen-native/UPSTREAM.adoc)。 |
| 运行时加载受控源码 | 已实现 | 本地 editable 依赖指向 `forks/vision-agents-qwen-native`，import path 测试见 [tests/test_vision_agents_runtime_path.py](tests/test_vision_agents_runtime_path.py)。 |
| Qwen WebSocket adapter contract | 已实现主要核心断言 | 六批 PR 完成 session config、视频轮次、事件映射、打断、工具/搜索、错误与重连。最终声明见 [final-conformance-statement.md](forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md)。 |
| 体验规约与成本治理 | 已完成文档建模 | 08 号书定义体验对象、用户故事、公共投影、黑盒断言和成本治理。 |
| Qwen adapter 契约书 | 已完成文档建模 | 09 号书定义源码身份、运行路径、事件契约、状态机、测试证据和 PR 符合性声明。 |
| TideSync Qwen Omni Harness 前端 | 已完成蓝图，未实现 | PR #17 只接纳前端设计和 SDK 事实材料，没有实现 React UI、后端控制 API 或 Playwright/live 验证。 |
| TypeScript CLI | 保留骨架 | [src/cli.ts](src/cli.ts) 目前仍是初始化 CLI 示例，后续服务前端和工具链扩展；它不是当前 Qwen agent 主入口。 |

## 用户故事与完成度

| 用户故事 | 当前状态 | 证据与边界 |
|---|---|---|
| 用户可以进入 AI 语音视频会话 | 后端链路已具备 | `tidesync-agent` 启动 Vision Agents Runner；浏览器入口当前依赖 Vision Agents / GetStream demo。 |
| 用户麦克风语音进入 AI 会话 | 已具备主链路 | `Agent` 通过 GetStream 接收音频，Qwen adapter 发送 `input_audio_buffer.append`。 |
| 用户摄像头画面进入 AI 会话 | 已具备主链路 | `include_video=True`，默认 `fps=1`；adapter 已补齐当前轮次图片发送许可。 |
| AI 以自然语音回应 | 已具备主链路 | Qwen `response.audio.delta` 经 adapter 映射为 `RealtimeAudioOutput`，由 Vision Agents 输出回 call。 |
| 用户围绕当前画面提问 | 已经过手动黑盒验证 | 前端蓝图汇报记录了 live smoke 中的视频 track、1 FPS forwarding 和视觉问答观察；该证据不是 CI。 |
| 用户进行中文多轮对话 | 已经过手动黑盒验证 | 前端蓝图汇报记录了中文 user transcript 与 agent transcript。 |
| 用户打断 AI 回答 | adapter 层已实现，live latency 未测 | Batch 04 实现本地 flush、remote cancel、stale delta 隔离；`interruption-latency-measured` 仍为 blocked。 |
| 工具调用 | adapter 层已实现 | Batch 05 支持 registry tool schema、function call execution、function_call_output 和 `response.create`。产品 UI 尚未暴露。 |
| 联网搜索与 usage | adapter 层已实现 | 支持 `enable_search`、`search_options`、tools/search 互斥、`usage.plugins.search` 保留。产品 UI 尚未暴露。 |
| 错误与重连 | adapter 层已实现确定性证据 | Batch 06 保留结构化 Qwen error、session config failure、recoverable reconnect reset、usage parse raw payload。live reconnect timing 未测。 |
| Qwen 专属调试前端 | 已设计，未实现 | 设计见 [05 前端蓝图](docs/deep-research/05-TideSync%20Qwen%20Omni%20%E8%B0%83%E8%AF%95%E5%89%8D%E7%AB%AF%E5%AE%8C%E6%95%B4%E8%93%9D%E5%9B%BE%E6%B1%87%E6%8A%A5.md)。 |

## 成本控制与端云协同

TideSync 没有把成本控制理解为简单的 token 节省。08 号书把成本治理定义为：在不破坏核心体验承诺的前提下，对音频、视觉、模型、工具、上下文、存储、网络、设备、用户注意力和隐私暴露进行预算、分配、调度、投影和审查的规则体系。完整模型见 [成本、资源与体验预算](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/parts/600-cost-resource-and-experience-budget/010-cost-governance-identity.adoc)。

对与题目中成本策略的建模，成本账本至少包含八类对象：

- 金钱成本：模型输入输出、音频、视觉、语音合成、工具调用、带宽、存储。
- 延迟成本：首次回应、视觉更新、打断停止、工具等待和错误投影。
- 质量损失成本：采样降低、模型路由、上下文压缩、语音质量降低带来的可靠性损失。
- 隐私暴露成本：麦克风、摄像头、屏幕共享、快照、片段、转录和工具结果的暴露面。
- 用户控制成本：拍照、录制、模式选择、授权、确认和恢复操作。
- 工程复杂度成本：端云协同、模型路由、引用资产、缓存、工具网关和测试维护。
- 容量机会成本：实时连接、模型并发、GPU 队列、工具配额、带宽和存储占用。
- 能源与设备成本：移动端电量、设备发热、网络传输和云端计算。

当前已经采用的成本策略包括：

- 默认 `QWEN_REALTIME_FPS=1`，用低频视频抽帧控制连续视觉输入成本。
- 选择 `qwen3.5-omni-flash-realtime` 作为默认模型，在实时能力与使用成本之间取平衡。
- 优先完成 Qwen WebSocket adapter，而不是同时推进 Qwen 原生 WebRTC transport，降低当前工程复杂度。
- 使用 GetStream 承担浏览器与 agent 的实时媒体通话层，复用成熟 WebRTC 基础设施。
- 在 adapter 中保留 `response.done.usage` 和 `usage.plugins.search`，为后续单位经济和成本归因提供数据表面。
- 在配置层拒绝 tools 与 search 同时启用，避免非法配置进入服务端运行时。
- 使用 fake WebSocket 和 event replay 覆盖大量协议行为，减少 live API 调试成本。

已经形成但尚未实现的成本策略包括：连续实时、事件触发视觉、快照指称、片段指称、语音优先和工具增强等模态预算；快照/片段引用资产；浏览器端 evidence panel 的 usage/search/tool/error/metrics 可视化；每成功视觉回答、每成功打断恢复、每工具增强回答等单位经济指标。这些设计见 [模态预算模型](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/parts/600-cost-resource-and-experience-budget/050-modality-budget-model.adoc)、[视觉证据与引用资产](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/parts/600-cost-resource-and-experience-budget/060-visual-evidence-and-reference-assets.adoc)和 [单位经济与成本分摊](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/parts/600-cost-resource-and-experience-budget/090-unit-economics-and-allocation.adoc)。

## Qwen3.5 Omni Realtime WebSocket Adapter

TideSync 的能力差距调查见 [docs/能力差距简报.md](docs/%E8%83%BD%E5%8A%9B%E5%B7%AE%E8%B7%9D%E7%AE%80%E6%8A%A5.md)。调查结论是：上游 Vision Agents v0.6.4 的 Qwen adapter 主要覆盖基础 WebSocket 语音视频路径，不能完整承担 Qwen3.5 Omni Realtime WebSocket contract。它可以建连、发送 `session.update`、append audio/image、接收音频 delta 和部分转写，并在部分条件下发送 `response.cancel`；但它没有完整表达 session 配置、Manual、semantic VAD、输入轮次视频时序、响应生命周期、audio done、transcript done、工具、搜索、usage、结构化错误、本地打断 flush 和 stale response 隔离。

因此，TideSync 将 Vision Agents 运行路径导入受控 fork，并按 09 号书分批完成 adapter contract。

| 批次 | 主题 | 核心内容 |
|---|---|---|
| Batch 00 / PR #9 | 受控源码与运行路径 | 导入 `agents-core`、`plugins/qwen`、`plugins/getstream`，配置本地 editable 依赖，添加 runtime import path 测试。 |
| Batch 01 / PR #11 | Session config 与 client senders | Qwen3.5 默认合同值、`pcm`、`qwen3-asr-flash-realtime`、`server_vad`/`semantic_vad`/Manual、tools/search 互斥、`input_audio_buffer.clear`、`conversation.item.create`、`response.create`。 |
| Batch 02 / PR #12 | 输入轮次与视频发送许可 | 用当前输入轮次状态替代历史 `_audio_emitted_once`，处理 speech stopped、commit、clear、track reconnect 和 image timing error。 |
| Batch 03 / PR #13 | 服务端事件映射 | 映射 response lifecycle、`response.audio.done`、assistant/user transcript delta/final、`response.done.usage` 和 search usage。 |
| Batch 04 / PR #14 | 打断与 stale response | `speech_started` 触发 user turn、本地 audio flush、remote cancel、agent interrupted、旧 response delta 隔离和 cancel error 保留。 |
| Batch 05 / PR #15 | 工具、搜索和 tool errors | registry `ToolSchema` 注入、function call 参数解析、工具执行、`function_call_output` 回传、`response.create`、工具错误可解释输出。 |
| Batch 06 / PR #16 | 结构化错误、重连和最终符合性 | Qwen error 结构化字段、session config failure、recoverable reconnect reset、usage parse raw retention、最终符合性声明。 |

最终符合性声明见 [forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md](forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md)。它记录的核心验证结果包括：

- `uv run pytest tests/test_vision_agents_runtime_path.py`：`1 passed`。
- `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`：`37 passed, 2 skipped`。
- `uv run ruff check ...`：`All checks passed!`。
- `uv run ruff format --check ...`：目标文件已格式化。

同时，最终声明也诚实登记了 live Qwen smoke、live interruption latency、live reconnect timing 和 undocumented payload variants 的阻塞或未知状态。这些项需要有效 API key、费用授权、服务可用性或更多官方/live 证据，不能用 fake replay 结果冒充。

## 第三方基础贡献

TideSync 使用并尊重第三方基础设施。README 中的“我们”指 TideSync 我围绕题目、规约、适配、运行路径和证据所做的工作，不指代第三方模型或框架本身。

| 第三方基础 | 在项目中的作用 |
|---|---|
| 阿里云 DashScope / Qwen3.5 Omni Flash Realtime | 提供实时全模态模型、WebSocket/WebRTC API、语音、视觉、工具、搜索和 usage 能力。模型摘要见 [docs/Qwen3.5-Omni-Flash-Realtime.md](docs/Qwen3.5-Omni-Flash-Realtime.md)，API 长文见 [docs/Qwen3.5-Omni-Flash-Realtime-API.md](docs/Qwen3.5-Omni-Flash-Realtime-API.md)。 |
| GetStream Vision Agents v0.6.4 | 提供 Python agent runtime、Realtime flow、GetStream Edge、Qwen/GetStream plugin 基线。来源见 [UPSTREAM.adoc](forks/vision-agents-qwen-native/UPSTREAM.adoc)。 |
| GetStream Video / WebRTC | 承担用户浏览器与 agent 之间的通话媒体层。 |
| Vision Agents core | 提供 `RealtimeAudioOutput`、`RealtimeAudioOutputDone`、speech started/ended、transcript、interrupt、audio output flush、FunctionRegistry 等承载物。 |
| Python / uv / pytest / ruff | 提供 Python runtime、依赖解析、测试和格式检查。 |
| Node / pnpm / TypeScript / Vitest / Biome | 当前保留为 TS CLI 和后续前端工具链基础。 |

| TideSync 贡献 | 说明 |
|---|---|
| 题目对象重述 | 将短题目重述为可判定的实时全模态视频通话体验，见 [08 号书](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/book.adoc)。 |
| 成本治理建模 | 建立成本账本、体验预算、模态预算、端云协同、单位经济和成本不符合案例。 |
| 能力差距调查 | 分析 Qwen3.5 Omni Realtime 官方 contract 与 Vision Agents Qwen adapter 的差距，见 [能力差距简报](docs/%E8%83%BD%E5%8A%9B%E5%B7%AE%E8%B7%9D%E7%AE%80%E6%8A%A5.md)。 |
| Adapter 契约书 | 建立 Qwen WebSocket adapter 的对象身份、配置契约、事件契约、状态机、断言和证据治理，见 [09 号书](docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc)。 |
| 受控 fork | 将运行依赖转为 TideSync 内可审查源码，并证明 runtime import path 指向受控目录。 |
| Qwen adapter 实现 | 完成六批 adapter contract 实现，覆盖 session、turn/video、event mapping、interruption、tools/search、errors/reconnect。 |
| 符合性声明 | 记录 assertion results、测试命令、live blockers、unknowns 和 rollback impact，见 [final-conformance-statement.md](forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md)。 |
| Harness 前端蓝图 | 设计后续开发者调试控制台的 session control、Qwen config、call surface、evidence panel、metrics、tools/search、errors 和 export surface。 |

## 运行当前后端

Python 是当前主入口。请先准备 `.env`：

```bash
cp .env.example .env
```

至少需要填写：

```dotenv
DASHSCOPE_API_KEY=your_dashscope_api_key
STREAM_API_KEY=your_stream_api_key
STREAM_API_SECRET=your_stream_api_secret
```

可选 Qwen 配置见 [.env.example](.env.example)：

```dotenv
QWEN_REALTIME_BASE_URL=wss://dashscope.aliyuncs.com/api-ws/v1/realtime
QWEN_REALTIME_MODEL=qwen3.5-omni-flash-realtime
QWEN_REALTIME_VOICE=Tina
QWEN_REALTIME_FPS=1
```

安装依赖并启动 agent：

```bash
uv sync
uv run tidesync-agent
```

`tidesync-agent` 会启动 Vision Agents Runner。浏览器访问链接和 call 进入方式由 Runner / GetStream demo 输出或配置决定。当前 TideSync 自研 Qwen Omni Harness 前端尚未实现，因此 Qwen 专属音色、VAD、Manual、tools/search、usage 和错误证据面暂时不会出现在 TideSync 自有前端中。

TypeScript workspace 目前保留为后续前端和工具链基础：

```bash
pnpm install
pnpm test
pnpm typecheck
pnpm lint
pnpm build
```

当前 [src/cli.ts](src/cli.ts) 仍是初始化 CLI 示例，不是 Qwen realtime agent 的主入口。

## 验证

推荐的本地验证命令：

```bash
uv run pytest tests/test_vision_agents_runtime_path.py
uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests
uv run ruff check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
uv run ruff format --check forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/qwen_realtime.py forks/vision-agents-qwen-native/plugins/qwen/vision_agents/plugins/qwen/client.py forks/vision-agents-qwen-native/plugins/qwen/tests/test_qwen_realtime.py
pnpm test
pnpm typecheck
pnpm lint
```

最终符合性声明记录的最近 adapter 验证结果为：

- runtime import path：`1 passed`。
- Qwen adapter deterministic tests：`37 passed, 2 skipped`。
- ruff check：`All checks passed!`。
- ruff format check：目标文件 already formatted。

跳过项是既有 live integration tests。live Qwen service verification 仍需要明确的 API key、费用授权、网络和服务可用性条件。

## 文档地图

| 文档 | 作用 |
|---|---|
| [docs/题目原文.md](docs/%E9%A2%98%E7%9B%AE%E5%8E%9F%E6%96%87.md) | 比赛题目原文。 |
| [08 实时全模态视频通话体验规约与符合性判定](docs/bookshelf/books/08-realtime-omnimodal-call-experience-spec/book.adoc) | 定义题目体验对象、用户旅程、公共投影、黑盒断言、成本治理和符合性声明。 |
| [09 Qwen3.5 Omni Realtime WebSocket Adapter 适配契约与验收规约](docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc) | 定义受控 Qwen adapter 的源码身份、运行路径、配置、事件、状态机、断言、证据和未知项边界。 |
| [docs/能力差距简报.md](docs/%E8%83%BD%E5%8A%9B%E5%B7%AE%E8%B7%9D%E7%AE%80%E6%8A%A5.md) | 吸收 Vision Agents Qwen adapter 与 Qwen3.5 Omni Realtime 官方 contract 的差距调查。 |
| [docs/Qwen3.5-Omni-Flash-Realtime.md](docs/Qwen3.5-Omni-Flash-Realtime.md) | 控制台模型摘要、价格、能力和示例。 |
| [docs/Qwen3.5-Omni-Flash-Realtime-API.md](docs/Qwen3.5-Omni-Flash-Realtime-API.md) | Qwen Omni Realtime API 长文材料。 |
| [05 TideSync Qwen Omni 调试前端完整蓝图汇报](docs/deep-research/05-TideSync%20Qwen%20Omni%20%E8%B0%83%E8%AF%95%E5%89%8D%E7%AB%AF%E5%AE%8C%E6%95%B4%E8%93%9D%E5%9B%BE%E6%B1%87%E6%8A%A5.md) | 后续 Qwen Omni Harness 调试前端设计基线。 |
| [final-conformance-statement.md](forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md) | Qwen adapter Batches 00-06 的最终断言结果、测试命令、live blockers、unknowns 和 rollback impact。 |
| [UPSTREAM.adoc](forks/vision-agents-qwen-native/UPSTREAM.adoc) | 受控 Vision Agents fork 的上游来源、导入范围、删减范围和同步规则。 |

## 已知限制

- TideSync 专属 Qwen Omni Harness 前端尚未实现。当前项目已经有前端蓝图，但没有 React 控制台、后端控制 API、Playwright 验证或浏览器 evidence panel。
- Qwen 原生 WebRTC transport 不属于当前实现对象。当前对象是 Qwen WebSocket adapter；浏览器到 agent 的通话媒体由 GetStream WebRTC 承担。
- live Qwen smoke、live interruption latency、live reconnect timing 和 undocumented payload variants 仍未完成验证，见 [Live Verification](forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/final-conformance-statement.md#live-verification)。
- 模型知识质量、ASR 误听率、视觉识别上限和语音自然度属于 Qwen 基座模型表现。TideSync 当前主要负责链路、配置、事件投影、打断、工具/搜索、usage、错误与证据。
- TypeScript CLI 仍是初始化骨架。它保留 TS 技术栈，不代表已经存在完整前端或产品命令面。

## 后续计划

下一阶段的核心对象是 TideSync Qwen Omni Harness 调试前端。它不是普通聊天页面，也不是 getstream.io demo 换皮，而是开发者控制台。它应包含：

- Session Bar：backend health、Runner ready、Stream call、agent session、Qwen realtime、elapsed time、call id、session id 和结束状态。
- Config Rail：model、voice、instructions、VAD、Manual 前置条件、video fps、search/tools 互斥、toolset 选择。
- Call Surface：本地视频预览、麦克风、摄像头、屏幕共享、agent 音频状态、视频 forwarding 状态、last frame age。
- Evidence Panel：Transcript、Events、Metrics、Tools/Search、Errors、Raw。
- Summary / Export：会话结束后的 Markdown / JSON 证据导出，包含配置快照、转写、轨道变化、barge-in、usage、search usage、错误和退出状态。

这个前端的设计基线已经记录在 [05 前端蓝图](docs/deep-research/05-TideSync%20Qwen%20Omni%20%E8%B0%83%E8%AF%95%E5%89%8D%E7%AB%AF%E5%AE%8C%E6%95%B4%E8%93%9D%E5%9B%BE%E6%B1%87%E6%8A%A5.md)。正式实现前，需要把后端控制 API、事件流、metrics、命令通道和浏览器 SDK 边界转化为可测试的实现计划。

## License

TideSync 当前仓库使用 Apache-2.0，见 [LICENSE](LICENSE)。受控 Vision Agents fork 保留上游来源和许可证说明，见 [forks/vision-agents-qwen-native/UPSTREAM.adoc](forks/vision-agents-qwen-native/UPSTREAM.adoc) 与 [forks/vision-agents-qwen-native/LICENSE.upstream](forks/vision-agents-qwen-native/LICENSE.upstream)。
