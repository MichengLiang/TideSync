# Vision Agents Qwen Native 治理指南

## 对象边界

`vision-agents-qwen-native` 是 TideSync 仓库内受控的 Vision Agents 派生源码区。它承载 TideSync 运行时实际加载的 `vision_agents.core`、`vision_agents.plugins.qwen` 和 `vision_agents.plugins.getstream`，并为 Qwen3.5 Omni Realtime WebSocket adapter 的实现、测试、审查和上游追溯提供可见边界。

本指南约束这个受控 fork 的走向。它不要求团队把上游 Vision Agents 全量改造成一个完美项目；它要求 TideSync 已经接手、正在修改、已经承诺的源码面保持可读、可测、可审查、可回溯。

## 核心原则

### 接手即负责

被 TideSync 修改过的文件不再只是上游遗留物。只要一个文件因为当前 adapter 合同、运行路径、测试证据或治理要求被编辑，它就进入 TideSync 当前维护责任面。

进入维护责任面的文件应满足三项要求：

- 新增或修改后的代码通过当前适用的 `ruff` 检查。
- 类型表达服务可理解的接口，不用类型忽略掩盖真实契约。
- PR 说明记录修改理由、验证方式和仍然保留的限制。

### 不死磕上游遗留类型债

Python 项目需要类型检查，但不需要把类型检查变成重写上游项目的借口。当前基线使用标准类型检查策略；它服务接口理解、运行路径保护和回归发现，不服务形式主义的零噪音表演。

允许保留的上游遗留问题包括：

- 未触达文件中的历史类型注解噪音。
- 与当前 Qwen adapter 合同无关的旧式写法。
- 上游包结构、动态导出或第三方库类型缺失带来的静态分析不完整。
- 已在 `UPSTREAM.adoc`、契约文档或 PR 留痕中说明的兼容性差异。

不允许新增的质量债包括：

- 在已编辑文件中引入新的 `ruff` 失败。
- 用宽泛忽略掩盖本来可以清楚表达的接口。
- 让运行时重新逃回 PyPI、external 或开发者本机未提交路径。
- 修改源码后不留下验证命令、失败原因或审查判断。

### 局部洁净优先于全仓净化

这个 fork 来自上游项目，上游本身可能存在格式、lint、类型和设计债。治理策略不是一次性清空所有遗留问题，而是让受控修改面持续变干净。

实践规则是：动到哪里，哪里的新增问题必须收敛。没有动到的上游遗留问题可以登记、可以暂存、可以以后处理，但不能混进当前 PR 冒充必要工作。

## 受控源码面

下列表面属于当前 fork 的受控源码面。

| 路径 | 职责 |
|---|---|
| `agents-core/vision_agents/**` | TideSync 运行时加载的 Vision Agents core。 |
| `plugins/qwen/vision_agents/plugins/qwen/**` | Qwen realtime adapter 的主要实现面。 |
| `plugins/getstream/vision_agents/plugins/getstream/**` | TideSync Qwen agent path 使用的 GetStream edge 实现面。 |
| `agents-core/pyproject.toml` | core 包元数据和局部开发配置。 |
| `plugins/qwen/pyproject.toml` | Qwen plugin 包元数据和局部开发配置。 |
| `plugins/getstream/pyproject.toml` | GetStream plugin 包元数据和局部开发配置。 |
| `UPSTREAM.adoc` | 上游来源、导入范围、删减范围和同步规则。 |
| `README.md` | 受控 fork 的入口说明。 |
| `GOVERNANCE.md` | 本 fork 的治理规则。 |
| `团队仓库的 PR 留痕与变更接纳工作流.md` | 变更进入主线时的证据链规则。 |
| `docs/qwen35-omni-adapter-contract/**` | adapter 合同执行过程中的协调、审查和证据材料。 |

受控源码面不是“全部必须立刻重构”的意思。它表示：这些路径里的变更需要明确责任、验证和留痕。

## Ruff 规则

`ruff` 是当前 fork 的基础代码质量门。

对已编辑 Python 文件，贡献者必须做到：

- 运行 `ruff check` 覆盖本次触达路径。
- 运行 `ruff format --check` 或执行格式化后确认无格式差异。
- 不用整仓历史债解释自己新增的 lint 失败。
- 不为单个问题添加全局忽略。

推荐命令：

```bash
uv run ruff check <paths>
uv run ruff format --check <paths>
```

如果某个上游文件因为历史原因暂时无法整体通过 `ruff`，但当前改动必须触达该文件，PR 应说明：

- 当前改动触达的代码范围。
- 本次已经消除或没有新增的失败类型。
- 保留失败属于上游遗留、当前合同外问题，还是后续需要单独清理的问题。

## 类型检查规则

`basedpyright` 是当前项目的类型检查工具，策略是标准检查，不追求极限严格。

类型检查的目标是让维护者理解接口和发现真实回归。以下做法符合本 fork 的质量方向：

- 对新增公共函数、事件对象、状态对象和 fake 测试工具写清楚类型。
- 对 Qwen adapter 与 Vision Agents core 的交界面保留类型信息。
- 对动态 plugin import 造成的静态分析问题，优先改成显式导入或局部解释。
- 对第三方库缺失 stub 的问题，按项目配置处理，不为了 stub 噪音阻塞 adapter 合同工作。

以下做法不符合本 fork 的质量方向：

- 为追求类型零噪音而大规模改写无关上游文件。
- 用 `Any`、`type: ignore` 或配置忽略隐藏本可以表达清楚的 contract。
- 把类型修复和 adapter 行为修复混成一个不可审查 PR。

## 测试与证据

测试选择由变更对象决定。

一般 Python 入口、配置和运行路径变更至少应考虑：

```bash
uv run pytest
uv run basedpyright
uv run ruff check <paths>
uv run ruff format --check <paths>
```

Qwen adapter contract 相关变更还应根据影响面补充：

- fake WebSocket 发送记录测试。
- event replay 测试。
- import 路径断言。
- stale delta、cancel error、usage、工具调用或搜索相关 fixture。
- 与 09 号 adapter contract 对应的断言证据。

真实服务 smoke 只能补充说明服务端兼容性。它不能替代 fake WebSocket、event replay 和路径断言。

## PR 留痕规则

本 fork 的变更应通过 PR 留痕进入主线。PR 的价值不是流程表演，而是把变更对象、验证证据、人的判断和合入事实放到同一个可回看的平台对象里。

本目录内的 `团队仓库的 PR 留痕与变更接纳工作流.md` 是 PR 留痕规则的详细说明。治理类、运行路径类、adapter 行为类、上游同步类变更都应按该工作流留下证据链。

一个合格 PR 至少说明：

- 本 PR 接纳的变更对象。
- 触达的受控源码面。
- 为什么这个变更属于当前 fork。
- 运行了哪些验证命令，结果是什么。
- 哪些检查没有运行，原因是什么。
- 是否存在上游遗留问题、当前偏离项或后续清理项。

## 提交边界

提交边界由变更对象定义。

推荐形态：

- adapter 行为修复单独提交。
- fake WebSocket 或 replay 测试单独提交，或与对应行为修复放在同一小范围提交中。
- 治理文档、来源说明、PR 留痕文档单独提交。
- 质量工具配置单独提交。

不推荐形态：

- 在同一提交中混入 adapter 行为、上游格式化、治理文档和无关测试清理。
- 为了让整仓 lint 看起来更干净而批量格式化未触达上游文件。
- 把 “顺手修一下” 的上游债混入一个有明确 contract 目标的 PR。

## 忽略与例外

忽略规则必须有对象理由。

允许的例外：

- 第三方库没有类型 stub，且项目配置已经统一处理。
- 上游动态结构无法被静态工具完整理解，且运行路径测试覆盖了真实导入。
- 当前 PR 暴露了历史债，但该历史债不属于本 PR 变更对象，且 PR 说明保留原因。

不允许的例外：

- 因为修复麻烦而扩大忽略范围。
- 因为上游文件很吵而忽略自己新增的失败。
- 因为测试慢而跳过唯一能证明行为成立的测试。
- 因为真实通话成功而删除可重复的 fake/replay 证据。

## 上游同步

上游同步不是简单覆盖本地文件。

同步前必须确认：

- 上游版本、commit 和导入范围。
- 本地 TideSync 修改是否仍然必要。
- 09 号 Qwen adapter contract 的核心断言是否仍然成立。
- TideSync root `pyproject.toml` 是否仍然解析到受控源码。
- `UPSTREAM.adoc` 是否需要更新。

上游 release note 不能替代本地断言。只有通过当前 contract 验收的上游行为，才有资格替换本地派生行为。

## 开发者判断顺序

不确定时按以下顺序判断：

1. 这次改动的对象是什么。
2. 这个对象是否属于 `vision-agents-qwen-native`。
3. 它触达哪些受控源码面。
4. 触达文件是否保持 `ruff` 干净。
5. 类型表达是否帮助维护者理解 contract。
6. 测试是否证明运行路径或行为投影成立。
7. PR 是否留下足够的接纳证据。

如果某一步答不上来，应先收敛对象，而不是扩大改动。

## 压缩规则

受控 fork 服务 TideSync 运行路径，不服务上游全仓净化。

接手文件必须保持干净。

上游遗留债可以保留，但不能新增。

Ruff 是触达文件的基础质量门。

类型检查服务接口理解，不服务形式主义。

真实服务成功不替代可重复测试证据。

PR 是变更接纳证据链，不是流程装饰。

提交边界由变更对象决定。

上游同步必须经过 TideSync contract 验收。

