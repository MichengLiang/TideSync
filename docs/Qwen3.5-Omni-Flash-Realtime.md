# 阿里云百炼控制台：Qwen3.5-Omni-Flash-Realtime 模型详情与集成指南

## 一、 页面导航与核心定位

* **所属平台**：大模型服务平台百炼 `.bailian.aliyun-console`
* **当前路由**：模型广场 `/` Qwen3.5-Omni-Flash-Realtime
* **服务地域**：中国内地

---

## 二、 模型基本信息与价格

### 1. 模型介绍

* **模型名称**：Qwen3.5-Omni-Flash-Realtime
* **模型Code**：`qwen3.5-omni-flash-realtime`
* **快照版本**：`qwen3.5-omni-flash-realtime-2026-03-15`
* **模型标签**：实时全模态
* **核心能力**：
> Qwen3.5-Omni是Qwen最新一代全模态大模型，支持文本，图片，音频，音视频理解与交互。作为 Qwen3-Omni 的全面进化版本，支持60+种语言音频输入，30+语言语音输出以及可控语音对话，WebSearch和复杂FunctionCall的调用，并且具备智能语义打断的交互能力，广泛应用于文本创作、语音助手、多媒体分析等场景，提供自然流畅的多模态交互体验。



### 2. 计费方案（每百万 tokens）

* **输入：文本/图片/视频**：3.3 元
* **输入：音频**：27.5 元
* **输出：文本**：20.0 元
* **输出：文本+音频**：107.0 元 *(注：输出的文本不计费)*
* **工具调用价格（联网搜索等）**：4 元 / 千次调用 (`search_strategy:agent`)

### 3. 免费额度

* **当前状态**：剩余 100%（额度总量为 `1,000,000 / 1,000,000`）
* **过期时间**：2026/06/23
* **策略配置**：已开启“免费额度用完即停”

---

## 三、 模型限流与上下文指标

| 指标项 | 配置参数 |
| --- | --- |
| **上下文长度** | 256K |
| **最大输入长度** | 192K |
| **最大输出长度** | 64K |
| **RPM (每分钟请求数)** | 60 |
| **TPM (每分钟Token数)** | 100,000 |

### 矩阵能力支持情况

* **输入模态**：文本（`spark-text-line`）、图片（`spark-picture-line`）、视频（`spark-videoCall-line`）、音频（`spark-voiceChat02-line`）
* **输出模态**：文本、图片、视频、音频
* **特性支持**：
* 开箱即用支持：**Function Calling** $\checkmark$、**联网搜索** $\checkmark$
* 当前未开放/未支持：模型体验 $\times$、结构化输出 $\times$、前缀续写 $\times$、Cache缓存 $\times$、批量推理 $\times$、模型调优 $\times$



---

## 四、 API 代码示例 (Python)

以下是控制台内集成的 DashScope Realtime 实时双向音频对话 SDK 使用示例：

```python
# 依赖：dashscope >= 1.23.9，pyaudio
import os
import base64
import time
import pyaudio
from dashscope.audio.qwen_omni import MultiModality, AudioFormat, OmniRealtimeCallback, OmniRealtimeConversation
import dashscope

url = f'wss://dashscope.aliyuncs.com/api-ws/v1/realtime'

# 配置 API Key，若没有设置环境变量，请用 API Key 将下行替换为 dashscope.api_key = "sk-xxx"
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

# 指定音色
voice = 'Ethan'
# 指定模型
model = 'qwen3.5-omni-flash-realtime'
# 指定模型角色
instructions = "你是个人助理小云，请用幽默风趣的方式回答用户的问题"

class SimpleCallback(OmniRealtimeCallback):
    def __init__(self, pya):
        self.pya = pya
        self.out = None

    def on_open(self):
        # 初始化音频输出流
        self.out = self.pya.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True
        )

    def on_event(self, response):
        if response['type'] == 'response.audio.delta':
            # 播放音频
            self.out.write(base64.b64decode(response['delta']))
        elif response['type'] == 'conversation.item.input_audio_transcription.completed':
            # 打印转录文本
            print(f"[User] {response['transcript']}")
        elif response['type'] == 'response.audio_transcript.done':
            # 打印助手回复文本
            print(f"[LLM] {response['transcript']}")

# 1. 初始化音频设备
pya = pyaudio.PyAudio()

# 2. 创建回调函数和会话
callback = SimpleCallback(pya)
conv = OmniRealtimeConversation(model=model, callback=callback, url=url)

# 3. 建立连接并配置会话
conv.connect()
conv.update_session(
    output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
    voice=voice,
    instructions=instructions
)

# 4. 初始化音频输入流
mic = pya.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True
)

# 5. 主循环处理音频输入
print("对话已开始，对着麦克风说话 (Ctrl+C 退出)...")
try:
    while True:
        audio_data = mic.read(3200, exception_on_overflow=False)
        conv.append_audio(base64.b64encode(audio_data).decode())
        time.sleep(0.01)
except KeyboardInterrupt:
    # 清理资源
    conv.close()
    mic.close()
    callback.out.close()
    pya.terminate()
    print("\n对话结束")

```

---

## 五、 云产品侧边面板上下文 (云资源概览)

在控制台全局抽屉面板中，当前关联的云资源清单如下：

### 最近访问产品

* 大模型服务平台百炼
* 费用与成本
* 人工智能平台 PAI
* 域名与网站
* 专有网络 VPC
* 云服务器 ECS

### 个人专属资源统计

* **人工智能平台 PAI**：已开通
* **云服务器 ECS**：拥有 `1 个安全组`
* **对象存储 OSS**：拥有 `1 个 Bucket`
* **专有网络 VPC**：拥有 `1 个专有网络`、`1 个交换机`、`1 个路由表`
* **大数据开发治理平台 DataWorks**：拥有 `1 个工作空间`
* **访问控制 RAM**：拥有 `14 个角色`
