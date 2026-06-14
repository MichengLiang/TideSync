<Taylor id="1">
# 已完成

已按确认方案完成分支、提交、PR、评论和合并。

## 分支与提交

创建并推送过的分支：

```text
feature/qwen35-realtime-agent
```

提交：

```text
36f8bdc feat: 接入 Qwen3.5 Realtime Python agent
```

该提交进入 PR 后通过 squash merge 合并到 `main`，合并提交为：

```text
b6b92ac 接入 Qwen3.5 Realtime Python agent
```

当前本地与远端状态：

```text
HEAD -> main, origin/main
```

## PR

PR：

```text
#3 接入 Qwen3.5 Realtime Python agent
https://github.com/MichengLiang/TideSync/pull/3
```

状态：

```text
MERGED
```

合并方式：

```text
squash merge
```

远端 feature 分支已删除；本地 stale tracking 引用也已通过 `git fetch --prune origin` 清理。

## PR 评论

已添加运行记录评论：

```text
https://github.com/MichengLiang/TideSync/pull/3#issuecomment-4699255057
```

评论内容只记录运行配置和后续维护约束，没有写排障过程。

## 合并内容

合并进入 `main` 的文件：

```text
.env.example
.gitignore
pyproject.toml
src/tidesync/__init__.py
src/tidesync/agent.py
tests/test_hello.py
uv.lock
```

合并统计：

```text
7 files changed, 1663 insertions(+)
```

## 验证

合并前已通过：

```text
uv run pytest -q
uv run ruff check .
pnpm lint
pnpm typecheck
pnpm test
```

GitHub 上的 GitGuardian Security Checks 也通过。

## 当前工作区

当前仍有一个未跟踪目录：

```text
?? docs/superpowers/
```

这是之前的计划文档目录，按确认方案没有纳入本次 PR。真实 `.env` 没有提交。
</Taylor>

<Miran id="1">
请你开始深入调查与确认。  首先第一点，我发现我不能打断，不能像这个OpenAI的那种视频通话那样子，或者说是谷歌的那个Gemini Live那样子。 第二点，我发现它不是流式传输的，它好像是把这个文字全部都打出来了，然后语音才慢慢播出来？？ 我想请你去全面调查一下，就是在这里我们这个通义千问这个模型，它到底承担哪些职责？我们的这一个Agent是吧？也就是我们程序在这边处理的东西到底又有哪些？ 比如说像这个什么打断机制到底是谁提供的？但是目前好像我并没有看到。当前的这些代码是吧？我们用的这个SDK到底有没有很好的去发挥模型的能力？有没有做到？  那么这个基座模型它本身到底支持什么？什么是模型已经处理掉的东西？你全面调查展开，你都确定你调查好之后，弹窗报告汇报给我，不少于4000字或者更多，请你开始吧。

日志：
t103o@TiOzoloooo:~/workbench/micheng-ts/projects/TideSync$ uv run tidesync-agent run --call-id tidesync-qwen-smoke --log-level INFO
      Built tidesync @ file:///home/t103o/workbench/micheng-ts/projects/TideSync
Uninstalled 1 package in 2ms
Installed 1 package in 0.74ms
2026-06-14 01:44:39.808614820 [W:onnxruntime:Default, device_discovery.cc:283 GetGpuDevices] Failed to detect devices under "/sys/class/drm/card0": device_discovery.cc:93 ReadFileContents Failed to open file: "/sys/class/drm/card0/device/vendor"

░█░█░▀█▀░█▀▀░▀█▀░█▀█░█▀█░░░█▀█░█▀▀░█▀▀░█▀█░▀█▀░█▀▀
░▀▄▀░░█░░▀▀█░░█░░█░█░█░█░░░█▀█░█░█░█▀▀░█░█░░█░░▀▀█
░░▀░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░░░▀░▀░▀▀▀░▀▀▀░▀░▀░░▀░░▀▀▀
                                            v0.6.4

01:44:39.981 | INFO     | 🚀 Launching agent...
01:44:39.981 | INFO     | Creating agent...
01:44:40.019 | INFO     | Warming up agent components...
01:44:40.120 | INFO     | Agent warmup completed
01:44:40.121 | INFO     | [Agent: tidesync-agent] | 🤖 Stopping the agent
01:44:40.126 | INFO     | [Agent: tidesync-agent] | 🤖 Agent stopped
01:44:40.126 | INFO     | ✅ Agent warmed up and ready
01:44:40.126 | INFO     | 📞 Joining call: default/tidesync-qwen-smoke
01:44:40.145 | INFO     | Started agent session with id db07b10e-a635-4d49-9f93-06bb890c01a1
01:44:40.145 | INFO     | 🌐 Opening demo UI...
01:44:41.943 | INFO     | [Agent: tidesync-agent] | 🤖 Agent joining call: tidesync-qwen-smoke
01:44:44.609 | INFO     | 🌐 Opening browser to: https://getstream.io/video/demos/join/tidesync-qwen-smoke?api_key=wk7gb8mhjjxd&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3ODEzNzI2NzksInVzZXJfaWQiOiJ1c2VyLWRlbW8tYWdlbnQiLCJleHAiOjE3ODEzNzYyODR9.1ubVF9seaMvycPrEs0HjmpM6Pjx9TOddAodRhe1Mjg0&skip_lobby=true&user_name=Human+User&video_encoder=h264&bitrate=12000000&w=1920&h=1080&channel_type=messaging                                                                          
01:44:44.618 | INFO     | ✅ Browser opened successfully!
gio: https://getstream.io/video/demos/join/tidesync-qwen-smoke?api_key=wk7gb8mhjjxd&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3ODEzNzI2NzksInVzZXJfaWQiOiJ1c2VyLWRlbW8tYWdlbnQiLCJleHAiOjE3ODEzNzYyODR9.1ubVF9seaMvycPrEs0HjmpM6Pjx9TOddAodRhe1Mjg0&skip_lobby=true&user_name=Human+User&video_encoder=h264&bitrate=12000000&w=1920&h=1080&channel_type=messaging: Operation not supported
01:44:46.158 | INFO     | [Agent: tidesync-agent] | 🤖 Agent joined call: tidesync-qwen-smoke
01:44:47.666 | INFO     | 🤖 Agent ready to speak
01:44:47.982 | INFO     | [Agent: tidesync-agent] | Waiting for other participants to join
01:44:57.983 | INFO     | [Agent: tidesync-agent] | No participants joined after 10.0s timeout, proceeding.
Already subscribed to track: user_id: "user-demo-agent"
session_id: "7cb34f15-e57d-4095-b91f-d4d1e18e80d2"
type: TRACK_TYPE_AUDIO
participant {
  user_id: "user-demo-agent"
  session_id: "7cb34f15-e57d-4095-b91f-d4d1e18e80d2"
  published_tracks: TRACK_TYPE_AUDIO
  joined_at {
    seconds: 1781372720
    nanos: 545893565
  }
  track_lookup_prefix: "1198d7d2bed53e40"
  connection_quality: CONNECTION_QUALITY_EXCELLENT
  name: "Resonant Gauge"
  roles: "user"
}

01:45:26.716 | INFO     | [Agent: tidesync-agent] | 📺 Track added: VIDEO from user-demo-agent
01:45:26.716 | INFO     | Started video forwarding with 1 FPS
01:45:29.667 | INFO     | Track unpublished: user-demo-agent, tracks: ['TRACK_TYPE_VIDEO']
01:45:29.667 | INFO     | [Agent: tidesync-agent] | 📺 Track removed: VIDEO from user-demo-agent
01:45:29.667 | INFO     | 🛑 Stopped video forwarding to Qwen (participant left)
01:45:29.993 | INFO     | Track unpublished: user-demo-agent, tracks: ['TRACK_TYPE_AUDIO']
01:45:43.742 | INFO     | 🎤 [Agent transcript]: 你好
01:45:43.751 | INFO     | 🎤 [Agent transcript]: 呀
01:45:43.752 | INFO     | 🎤 [Agent transcript]: ，
01:45:43.760 | INFO     | 🎤 [Agent transcript]: 我是
01:45:43.773 | INFO     | 🎤 [Agent transcript]:  Tide
01:45:43.773 | INFO     | 🎤 [Agent transcript]: Sync
01:45:43.785 | INFO     | 🎤 [Agent transcript]:  的
01:45:43.789 | INFO     | 🎤 [Agent transcript]: 实时
01:45:43.790 | INFO     | 🎤 [Agent transcript]: 全
01:45:43.809 | INFO     | 🎤 [Agent transcript]: 模
01:45:43.812 | INFO     | 🎤 [Agent transcript]: 态
01:45:43.819 | INFO     | 🎤 [Agent transcript]: 语音视频
01:45:43.819 | INFO     | 🎤 [Agent transcript]: 助手
01:45:43.829 | INFO     | 🎤 [Agent transcript]: 。
01:45:43.830 | INFO     | 🎤 [Agent transcript]: 你可以
01:45:43.839 | INFO     | 🎤 [Agent transcript]: 叫我
01:45:43.847 | INFO     | 🎤 [Agent transcript]:  Tide
01:45:43.848 | INFO     | 🎤 [Agent transcript]: Sync
01:45:43.848 | INFO     | 🎤 [User transcript]: 你好呀，你是谁呀？
01:45:43.870 | INFO     | 🎤 [Agent transcript]: ，
01:45:43.870 | INFO     | 🎤 [Agent transcript]: 随时
01:45:43.870 | INFO     | 🎤 [Agent transcript]: 能
01:45:43.870 | INFO     | 🎤 [Agent transcript]: 看见
01:45:43.879 | INFO     | 🎤 [Agent transcript]: 画面
01:45:43.879 | INFO     | 🎤 [Agent transcript]: 、
01:45:43.889 | INFO     | 🎤 [Agent transcript]: 听见
01:45:43.889 | INFO     | 🎤 [Agent transcript]: 声音
01:45:43.895 | INFO     | 🎤 [Agent transcript]: ，
01:45:43.905 | INFO     | 🎤 [Agent transcript]: 也能
01:45:43.905 | INFO     | 🎤 [Agent transcript]: 和你
01:45:43.914 | INFO     | 🎤 [Agent transcript]: 聊天
01:45:43.931 | INFO     | 🎤 [Agent transcript]: 或
01:45:43.931 | INFO     | 🎤 [Agent transcript]: 帮你
01:45:43.932 | INFO     | 🎤 [Agent transcript]: 处理
01:45:43.934 | INFO     | 🎤 [Agent transcript]: 任务
01:45:43.935 | INFO     | 🎤 [Agent transcript]: 。
01:45:43.944 | INFO     | 🎤 [Agent transcript]: 有什么
01:45:43.953 | INFO     | 🎤 [Agent transcript]: 想
01:45:43.953 | INFO     | 🎤 [Agent transcript]: 问
01:45:43.962 | INFO     | 🎤 [Agent transcript]: 的
01:45:43.964 | INFO     | 🎤 [Agent transcript]: 或
01:45:43.976 | INFO     | 🎤 [Agent transcript]: 需要
01:45:43.986 | INFO     | 🎤 [Agent transcript]: 帮忙
01:45:43.986 | INFO     | 🎤 [Agent transcript]: 的吗
01:45:43.987 | INFO     | 🎤 [Agent transcript]: ？
01:45:46.608 | INFO     | 🎤 [Agent transcript]: 
01:46:02.481 | INFO     | Track unpublished: user-demo-agent, tracks: ['TRACK_TYPE_AUDIO']
01:46:16.748 | INFO     | [Agent: tidesync-agent] | 📺 Track added: VIDEO from user-demo-agent
01:46:16.748 | INFO     | 🛑 Stopped video forwarding to Qwen (participant left)
01:46:16.748 | INFO     | Started video forwarding with 1 FPS
01:46:20.199 | INFO     | Track unpublished: user-demo-agent, tracks: ['TRACK_TYPE_VIDEO']
01:46:20.199 | INFO     | [Agent: tidesync-agent] | 📺 Track removed: VIDEO from user-demo-agent
01:46:20.200 | INFO     | 🛑 Stopped video forwarding to Qwen (participant left)
01:46:21.052 | INFO     | [Agent: tidesync-agent] | 📺 Track added: VIDEO from user-demo-agent
01:46:21.052 | INFO     | 🛑 Stopped video forwarding to Qwen (participant left)
01:46:21.052 | INFO     | Started video forwarding with 1 FPS
01:46:28.986 | INFO     | 🎤 [Agent transcript]: 我看
01:46:28.995 | INFO     | 🎤 [Agent transcript]: 了一下
01:46:28.996 | INFO     | 🎤 [Agent transcript]: ，
01:46:29.005 | INFO     | 🎤 [Agent transcript]: 这是一个
01:46:29.006 | INFO     | 🎤 [Agent transcript]: 有点
01:46:29.015 | INFO     | 🎤 [User transcript]: 这里面有什么呀？
01:46:29.016 | INFO     | 🎤 [Agent transcript]: 乱的
01:46:29.025 | INFO     | 🎤 [Agent transcript]: 桌面
01:46:29.026 | INFO     | 🎤 [Agent transcript]: 。
01:46:29.035 | INFO     | 🎤 [Agent transcript]: 上面
01:46:29.036 | INFO     | 🎤 [Agent transcript]: 有一
01:46:29.044 | INFO     | 🎤 [Agent transcript]: 台
01:46:29.055 | INFO     | 🎤 [Agent transcript]: 笔记本电脑
01:46:29.056 | INFO     | 🎤 [Agent transcript]: ，
01:46:29.072 | INFO     | 🎤 [Agent transcript]: 旁边
01:46:29.073 | INFO     | 🎤 [Agent transcript]: 还有
01:46:29.075 | INFO     | 🎤 [Agent transcript]: 耳机
01:46:29.075 | INFO     | 🎤 [Agent transcript]: 、
01:46:29.084 | INFO     | 🎤 [Agent transcript]: 鼠标
01:46:29.084 | INFO     | 🎤 [Agent transcript]: 和
01:46:29.094 | INFO     | 🎤 [Agent transcript]: 充电
01:46:29.094 | INFO     | 🎤 [Agent transcript]: 线
01:46:29.104 | INFO     | 🎤 [Agent transcript]: 。
01:46:29.114 | INFO     | 🎤 [Agent transcript]: 下面
01:46:29.115 | INFO     | 🎤 [Agent transcript]: 还
01:46:29.124 | INFO     | 🎤 [Agent transcript]: 压
01:46:29.125 | INFO     | 🎤 [Agent transcript]: 着
01:46:29.133 | INFO     | 🎤 [Agent transcript]: 一些
01:46:29.134 | INFO     | 🎤 [Agent transcript]: 纸
01:46:29.143 | INFO     | 🎤 [Agent transcript]: 和一个
01:46:29.143 | INFO     | 🎤 [Agent transcript]: 红色的
01:46:29.153 | INFO     | 🎤 [Agent transcript]: 本子
01:46:29.166 | INFO     | 🎤 [Agent transcript]: 。
01:46:29.166 | INFO     | 🎤 [Agent transcript]: 你
01:46:29.178 | INFO     | 🎤 [Agent transcript]: 是在
01:46:29.178 | INFO     | 🎤 [Agent transcript]: 整理
01:46:29.185 | INFO     | 🎤 [Agent transcript]: 东西
01:46:29.185 | INFO     | 🎤 [Agent transcript]: 吗
01:46:29.192 | INFO     | 🎤 [Agent transcript]: ？
01:46:29.192 | INFO     | 🎤 [Agent transcript]: 需要
01:46:29.203 | INFO     | 🎤 [Agent transcript]: 我
01:46:29.212 | INFO     | 🎤 [Agent transcript]: 帮忙
01:46:29.217 | INFO     | 🎤 [Agent transcript]: 看看
01:46:29.222 | INFO     | 🎤 [Agent transcript]: 吗
01:46:29.223 | INFO     | 🎤 [Agent transcript]: ？
01:46:31.848 | INFO     | 🎤 [Agent transcript]: 
01:46:31.985 | ERROR    | Error received from Qwen3Realtime API: {'type': 'invalid_request_error', 'message': 'Error append image before append audio.'}
01:46:45.140 | INFO     | 🎤 [Agent transcript]: 刚才
01:46:45.140 | INFO     | 🎤 [Agent transcript]: 画面
01:46:45.149 | INFO     | 🎤 [Agent transcript]: 里
01:46:45.150 | INFO     | 🎤 [Agent transcript]: 有一只
01:46:45.157 | INFO     | 🎤 [Agent transcript]: 手
01:46:45.160 | INFO     | 🎤 [Agent transcript]: 从
01:46:45.162 | INFO     | 🎤 [User transcript]: 好的，刚才有什么东西晃了一下过去了。
01:46:45.167 | INFO     | 🎤 [Agent transcript]: 右边
01:46:45.177 | INFO     | 🎤 [Agent transcript]: 伸
01:46:45.177 | INFO     | 🎤 [Agent transcript]: 进来
01:46:45.188 | INFO     | 🎤 [Agent transcript]: ，
01:46:45.198 | INFO     | 🎤 [Agent transcript]: 拿着一张
01:46:45.207 | INFO     | 🎤 [Agent transcript]: 纸
01:46:45.207 | INFO     | 🎤 [Agent transcript]: ，
01:46:45.216 | INFO     | 🎤 [Agent transcript]: 然后
01:46:45.225 | INFO     | 🎤 [Agent transcript]: 放
01:46:45.225 | INFO     | 🎤 [Agent transcript]: 到了
01:46:45.234 | INFO     | 🎤 [Agent transcript]: 鼠标
01:46:45.235 | INFO     | 🎤 [Agent transcript]: 垫
01:46:45.243 | INFO     | 🎤 [Agent transcript]: 旁边
01:46:45.244 | INFO     | 🎤 [Agent transcript]: 。
01:46:46.407 | INFO     | 🎤 [Agent transcript]: 
01:46:50.292 | INFO     | 🎤 [User transcript]: 好的，刚。
01:46:50.296 | INFO     | 🎤 [Agent transcript]: 刚才
01:46:50.296 | INFO     | 🎤 [Agent transcript]: 画面
01:46:50.296 | INFO     | 🎤 [Agent transcript]: 里
01:46:50.304 | INFO     | 🎤 [Agent transcript]: 又
01:46:50.304 | INFO     | 🎤 [Agent transcript]: 有一只
01:46:50.309 | INFO     | 🎤 [Agent transcript]: 手
01:46:50.310 | INFO     | 🎤 [Agent transcript]: 从
01:46:50.320 | INFO     | 🎤 [Agent transcript]: 右边
01:46:50.330 | INFO     | 🎤 [Agent transcript]: 伸
01:46:50.330 | INFO     | 🎤 [Agent transcript]: 进来
01:46:50.357 | INFO     | 🎤 [Agent transcript]: ，拿着一张
01:46:50.358 | INFO     | 🎤 [Agent transcript]: 纸
01:46:50.368 | INFO     | 🎤 [Agent transcript]: ，
01:46:50.368 | INFO     | 🎤 [Agent transcript]: 然后
01:46:50.377 | INFO     | 🎤 [Agent transcript]: 放
01:46:50.378 | INFO     | 🎤 [Agent transcript]: 到了
01:46:50.386 | INFO     | 🎤 [Agent transcript]: 鼠标
01:46:50.397 | INFO     | 🎤 [Agent transcript]: 垫
01:46:50.397 | INFO     | 🎤 [Agent transcript]: 旁边
01:46:50.406 | INFO     | 🎤 [Agent transcript]: 。
01:46:51.673 | INFO     | 🎤 [Agent transcript]: 
01:47:09.454 | INFO     | 🎤 [User transcript]: 是什么颜色呢？
01:47:09.479 | INFO     | 🎤 [Agent transcript]: 那张
01:47:09.489 | INFO     | 🎤 [Agent transcript]: 纸
01:47:09.489 | INFO     | 🎤 [Agent transcript]: 是
01:47:09.498 | INFO     | 🎤 [Agent transcript]: 白色的
01:47:09.499 | INFO     | 🎤 [Agent transcript]: 。
01:47:09.540 | INFO     | 🎤 [Agent transcript]: 
01:47:14.739 | INFO     | 🎤 [Agent transcript]: 是
01:47:14.751 | INFO     | 🎤 [User transcript]: 是什么颜色的呢？
01:47:14.751 | INFO     | 🎤 [Agent transcript]: 白色的
01:47:14.751 | INFO     | 🎤 [Agent transcript]: 。
01:47:14.996 | INFO     | 🎤 [Agent transcript]: 
01:47:15.316 | ERROR    | Error received from Qwen3Realtime API: {'type': 'invalid_request_error', 'message': 'Error append image before append audio.'}
01:47:31.732 | INFO     | 🎤 [User transcript]: 那刚才又换了什么东西呢？那么刚才又换动了什么东西呢？
01:47:31.806 | INFO     | 🎤 [Agent transcript]: 刚才
01:47:31.806 | INFO     | 🎤 [Agent transcript]: 那只
01:47:31.815 | INFO     | 🎤 [Agent transcript]: 手
01:47:31.815 | INFO     | 🎤 [Agent transcript]: 又
01:47:31.825 | INFO     | 🎤 [Agent transcript]: 伸
01:47:31.840 | INFO     | 🎤 [Agent transcript]: 过来了
01:47:31.840 | INFO     | 🎤 [Agent transcript]: ，
01:47:31.845 | INFO     | 🎤 [Agent transcript]: 把
01:47:31.857 | INFO     | 🎤 [Agent transcript]: 那张
01:47:31.858 | INFO     | 🎤 [Agent transcript]: 白纸
01:47:31.877 | INFO     | 🎤 [Agent transcript]: 拿走了
01:47:31.877 | INFO     | 🎤 [Agent transcript]: 。
01:47:31.888 | INFO     | 🎤 [Agent transcript]: 然后
01:47:31.888 | INFO     | 🎤 [Agent transcript]: 它
01:47:31.894 | INFO     | 🎤 [Agent transcript]: 又
01:47:31.896 | INFO     | 🎤 [Agent transcript]: 放
01:47:31.907 | INFO     | 🎤 [Agent transcript]: 了一个
01:47:31.907 | INFO     | 🎤 [Agent transcript]: 黑色的
01:47:31.916 | INFO     | 🎤 [Agent transcript]: 长
01:47:31.916 | INFO     | 🎤 [Agent transcript]: 条
01:47:31.925 | INFO     | 🎤 [Agent transcript]: 物体
01:47:31.929 | INFO     | 🎤 [Agent transcript]: 在
01:47:31.935 | INFO     | 🎤 [Agent transcript]: 鼠标
01:47:31.945 | INFO     | 🎤 [Agent transcript]: 垫
01:47:31.945 | INFO     | 🎤 [Agent transcript]: 上
01:47:31.954 | INFO     | 🎤 [Agent transcript]: ，
01:47:31.955 | INFO     | 🎤 [Agent transcript]: 看起来
01:47:31.964 | INFO     | 🎤 [Agent transcript]: 像
01:47:31.974 | INFO     | 🎤 [Agent transcript]: 是一支
01:47:31.974 | INFO     | 🎤 [Agent transcript]: 笔
01:47:31.986 | INFO     | 🎤 [Agent transcript]: 或者
01:47:31.986 | INFO     | 🎤 [Agent transcript]: 一个
01:47:31.996 | INFO     | 🎤 [Agent transcript]: U
01:47:32.011 | INFO     | 🎤 [Agent transcript]: 盘
01:47:32.011 | INFO     | 🎤 [Agent transcript]: 。
01:47:34.106 | INFO     | 🎤 [Agent transcript]: 
01:47:53.175 | INFO     | 🎤 [User transcript]: U盘有哪种类型呢？
01:47:53.181 | INFO     | 🎤 [Agent transcript]: 从
01:47:53.188 | INFO     | 🎤 [Agent transcript]: 画面
01:47:53.189 | INFO     | 🎤 [Agent transcript]: 来看
01:47:53.198 | INFO     | 🎤 [Agent transcript]: ，
01:47:53.207 | INFO     | 🎤 [Agent transcript]: 这个
01:47:53.208 | INFO     | 🎤 [Agent transcript]: U
01:47:53.218 | INFO     | 🎤 [Agent transcript]: 盘
01:47:53.227 | INFO     | 🎤 [Agent transcript]: 是黑色的
01:47:53.246 | INFO     | 🎤 [Agent transcript]: ，
01:47:53.246 | INFO     | 🎤 [Agent transcript]: 外形
01:47:53.246 | INFO     | 🎤 [Agent transcript]: 比较
01:47:53.255 | INFO     | 🎤 [Agent transcript]: 细长
01:47:53.257 | INFO     | 🎤 [Agent transcript]: ，
01:47:53.265 | INFO     | 🎤 [Agent transcript]: 插在
01:47:53.265 | INFO     | 🎤 [Agent transcript]: 笔记本
01:47:53.275 | INFO     | 🎤 [Agent transcript]: 的
01:47:53.276 | INFO     | 🎤 [Agent transcript]: USB
01:47:53.284 | INFO     | 🎤 [Agent transcript]: 接口
01:47:53.294 | INFO     | 🎤 [Agent transcript]: 上
01:47:53.295 | INFO     | 🎤 [Agent transcript]: 。
01:47:53.304 | INFO     | 🎤 [Agent transcript]: 它
01:47:53.313 | INFO     | 🎤 [Agent transcript]: 看起来
01:47:53.314 | INFO     | 🎤 [Agent transcript]: 属于
01:47:53.314 | INFO     | 🎤 [Agent transcript]: 常见的
01:47:53.323 | INFO     | 🎤 [Agent transcript]: USB
01:47:53.332 | INFO     | 🎤 [Agent transcript]: -A
01:47:53.333 | INFO     | 🎤 [Agent transcript]: 接口
01:47:53.343 | INFO     | 🎤 [Agent transcript]: U
01:47:53.343 | INFO     | 🎤 [Agent transcript]: 盘
01:47:53.352 | INFO     | 🎤 [Agent transcript]: ，
01:47:53.362 | INFO     | 🎤 [Agent transcript]: 体积
01:47:53.362 | INFO     | 🎤 [Agent transcript]: 小巧
01:47:53.371 | INFO     | 🎤 [Agent transcript]: ，
01:47:53.371 | INFO     | 🎤 [Agent transcript]: 适合
01:47:53.383 | INFO     | 🎤 [Agent transcript]: 日常
01:47:53.383 | INFO     | 🎤 [Agent transcript]: 数据传输
01:47:53.390 | INFO     | 🎤 [Agent transcript]: 使用
01:47:53.391 | INFO     | 🎤 [Agent transcript]: 。
01:47:53.401 | INFO     | 🎤 [Agent transcript]: 如果你
01:47:53.401 | INFO     | 🎤 [Agent transcript]: 需要
01:47:53.410 | INFO     | 🎤 [Agent transcript]: 更
01:47:53.420 | INFO     | 🎤 [Agent transcript]: 具体的
01:47:53.421 | INFO     | 🎤 [Agent transcript]: 型号
01:47:53.429 | INFO     | 🎤 [Agent transcript]: 或
01:47:53.430 | INFO     | 🎤 [Agent transcript]: 品牌
01:47:53.440 | INFO     | 🎤 [Agent transcript]: 信息
01:47:53.448 | INFO     | 🎤 [Agent transcript]: ，
01:47:53.449 | INFO     | 🎤 [Agent transcript]: 可能需要
01:47:53.459 | INFO     | 🎤 [Agent transcript]: 放大
01:47:53.460 | INFO     | 🎤 [Agent transcript]: 画面
01:47:53.470 | INFO     | 🎤 [Agent transcript]: 或者
01:47:53.480 | INFO     | 🎤 [Agent transcript]: 查看
01:47:53.481 | INFO     | 🎤 [Agent transcript]: 包装
01:47:53.481 | INFO     | 🎤 [Agent transcript]: 标签
01:47:53.487 | INFO     | 🎤 [Agent transcript]: 哦
01:47:53.497 | INFO     | 🎤 [Agent transcript]: 。
01:47:57.312 | INFO     | 🎤 [Agent transcript]: 
01:48:07.506 | INFO     | 🎤 [Agent transcript]: 固态
01:48:07.515 | INFO     | 🎤 [Agent transcript]: U
01:48:07.516 | INFO     | 🎤 [Agent transcript]: 盘
01:48:07.523 | INFO     | 🎤 [Agent transcript]: ，
01:48:07.527 | INFO     | 🎤 [Agent transcript]: 也叫
01:48:07.536 | INFO     | 🎤 [Agent transcript]: 固态硬盘
01:48:07.544 | INFO     | 🎤 [Agent transcript]: U
01:48:07.544 | INFO     | 🎤 [Agent transcript]: 盘
01:48:07.558 | INFO     | 🎤 [User transcript]: 什么是固态 U 盘？什么是固态 U 盘？什么是固态 U 盘？
01:48:07.558 | INFO     | 🎤 [Agent transcript]: ，
01:48:07.558 | INFO     | 🎤 [Agent transcript]: 是一种
01:48:07.570 | INFO     | 🎤 [Agent transcript]: 用
01:48:07.588 | INFO     | 🎤 [Agent transcript]: 闪存芯片来
01:48:07.588 | INFO     | 🎤 [Agent transcript]: 存储
01:48:07.598 | INFO     | 🎤 [Agent transcript]: 数据的
01:48:07.599 | INFO     | 🎤 [Agent transcript]: U
01:48:07.609 | INFO     | 🎤 [Agent transcript]: 盘
01:48:07.610 | INFO     | 🎤 [Agent transcript]: 。
01:48:07.621 | INFO     | 🎤 [Agent transcript]: 它
01:48:07.631 | INFO     | 🎤 [Agent transcript]: 没有
01:48:07.632 | INFO     | 🎤 [Agent transcript]: 机械
01:48:07.642 | INFO     | 🎤 [Agent transcript]: 部件
01:48:07.642 | INFO     | 🎤 [Agent transcript]: ，
01:48:07.653 | INFO     | 🎤 [Agent transcript]: 所以
01:48:07.656 | INFO     | 🎤 [Agent transcript]: 读写
01:48:07.664 | INFO     | 🎤 [Agent transcript]: 速度
01:48:07.676 | INFO     | 🎤 [Agent transcript]: 比普通
01:48:07.676 | INFO     | 🎤 [Agent transcript]: U
01:48:07.686 | INFO     | 🎤 [Agent transcript]: 盘
01:48:07.686 | INFO     | 🎤 [Agent transcript]: 快
01:48:07.709 | INFO     | 🎤 [Agent transcript]: 很多
01:48:07.709 | INFO     | 🎤 [Agent transcript]: ，
01:48:07.710 | INFO     | 🎤 [Agent transcript]: 也更
01:48:07.710 | INFO     | 🎤 [Agent transcript]: 耐用
01:48:07.719 | INFO     | 🎤 [Agent transcript]: 、
01:48:07.730 | INFO     | 🎤 [Agent transcript]: 抗震
01:48:07.730 | INFO     | 🎤 [Agent transcript]: 。
01:48:07.740 | INFO     | 🎤 [Agent transcript]: 简单来说
01:48:07.744 | INFO     | 🎤 [Agent transcript]: ，
01:48:07.757 | INFO     | 🎤 [Agent transcript]: 就是
01:48:07.768 | INFO     | 🎤 [Agent transcript]: 更
01:48:07.768 | INFO     | 🎤 [Agent transcript]: 高速
01:48:07.769 | INFO     | 🎤 [Agent transcript]: 、
01:48:07.778 | INFO     | 🎤 [Agent transcript]: 更
01:48:07.779 | INFO     | 🎤 [Agent transcript]: 可靠的
01:48:07.789 | INFO     | 🎤 [Agent transcript]: U
01:48:07.790 | INFO     | 🎤 [Agent transcript]: 盘
01:48:07.800 | INFO     | 🎤 [Agent transcript]: 。
01:48:12.950 | INFO     | 🎤 [Agent transcript]: 
01:48:13.061 | ERROR    | Error received from Qwen3Realtime API: {'type': 'invalid_request_error', 'message': 'Error append image before append audio.'}
^C01:48:15.244 | INFO     | [Agent: tidesync-agent] | 🤖 Stopping the agent
01:48:15.244 | INFO     | [Agent: tidesync-agent] | 🎵 Audio consumer task cancelled
01:48:15.244 | INFO     | [Agent: tidesync-agent] | 🎵 Audio producer task cancelled
^C01:48:17.841 | INFO     | [Agent: tidesync-agent] | 🤖 Stopping the agent
01:48:17.841 | INFO     | 🛑 Stopped video forwarding to Qwen (participant left)
^C01:48:19.013 | INFO     | 👋 Agent shutdown complete
Exception ignored in: <coroutine object SfuStatsReporter._run at 0x7feb9022ed40>

Tip:
完成后记得使用弹窗与我沟通。
</Miran>

<Taylor id="2">
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
</Taylor>

<Miran id="2">
好的，接下来暂时就靠你的记忆回答，请你告诉我，你知不知道Claude Code还有Codex？ 他们是非常好、非常优秀的Agent Runtime运行时 他们呢？比如说Codex是吧？它不仅可以自身作为MCP去接入其他的这一个MCP服务器，它自己也可以成为服务器去给别人接上。而且呢，它这个核心是吧？有这个是分开的嘛，它的这个前端，Electron的这个官方的前端是吧？在消费核心。同时呢，它还有这个CLI是吧？反正就是非常经典的分层。 然后呢，就是完完全全地实现100%的Responses接口，因为人家是官方自己做的嘛，是吧？ 好，然后呢，Codex是开源的。那克劳德Code呢，是闭源的。 啊，当然这里我不管什么开源闭源啊。没错，在这里，首先呢，它是什么呢？它是对于GPT 5.5啊适配能力是吧？它对GPT的适配是100%完整的，因为是官方的亲儿子是吧？对Responses这种就是这一个GPT的专属接口嘛，完整适配。那对于对对于这个我们这个通义千问这个Omni。  对于它来说，它是不是也得要一整套完整的属于模型的运行时？ 我们当前这个什么Vision Agent呢？它是运行时吗？  也就是对这个real time这种模型100%完全原生适配。也就是说，把模型的能力完全地激发出来，而不是让环境的偶然复杂性去拖垮模型。我就很好奇，是这个比如说阿里云官方，它里面自己测试到底用的是什么什么框架吗？他们有开源出来吗？还是说他们用的还是还是零散的呢？也就是说你看，在这一个Code Agent是吧？有现象级的，就是Codex跟Claude Code是非常好的这种代表性的一种运行时框架。其实还有什么AutoGPT之类的，这些东西还什么Langchain你应该都是知道的，是吧？ 那目前对于这种Real time.这种系列的接口，是不是目前是不是没有什么非常好现象级别的完整的运行时吗？ 按照你之前所看到的这一个阿里云模型，是吧？就这个基座模型，你觉得它到底需要怎样的这种Harness呢？  我再举些例子，比如说Codex是吧？比如说你自己当前所在的会话，我们自己所在的整个环境其实就是Codex运行时，是吧？你会发现你有很多工具，有很多官方内置的，也有很多社区贡献的，还有我给你做的，是不是？然后呢在这里有很多很多细节，比如说上下文的控制啊、一些过滤呀，是不是？然后呢，比如说什么截断呀，是吧？什么省token呀，提升上下文效率呀，什么过长的什么压缩啊，Compact呀，是不是？甚至OpenAI对于这种会话压缩还专门训练了这一个，诶，还专门去做了这个叫什么强化学习，没错，把强化学习都用在压缩上面。能够进行更长程的任务的执行。 按照这个Real time这个API接口，你觉得就是最理想、最完整的，没错，就是专属于这个的运行时，你觉得需要哪些能力？没有什么最大，没有什么最小，就好像你渴了想喝水一样。那你就说水就是了，是不是？你听懂这个比喻吗？那你觉得它需要完整的，什么才叫完整？把完整定义出来。它需要什么？理想的、最理想的、最完整的运行时到底是什么？好，请你仔细想一想，想好了弹窗和我分享，不少于4000字或者更多，开始吧。

Tip:
完成后记得使用弹窗与我沟通。
</Miran>

<Taylor id="3">
# 我对“Qwen Realtime 原生运行时”的重新判断

我知道你说的 Codex、Claude Code 这类对象。这里不把它们当作“一个 CLI”或“一个聊天壳”，而是当作 **Agent Runtime** 来理解：模型只是核心推理器，运行时负责把模型能力变成可持续执行、可观察、可恢复、可协作的工作系统。

你举 Codex 很准确。Codex 不是简单把模型 API 包一层命令行。它有模型适配层、工具调用层、文件系统交互、shell 执行、上下文管理、补丁编辑、计划状态、权限边界、摘要压缩、长任务恢复、MCP 接入、插件/技能/AGENTS 指令体系、不同前端消费同一个核心能力等。它的价值不只是“能调用 GPT”，而是把 GPT 的 agentic 能力放进一个能工作很久、能处理复杂状态、能和人协作、能保留执行纪律的环境里。

Claude Code 也是类似对象，哪怕它闭源。它不是“Claude + shell”。它有自己的项目理解、上下文筛选、工具调用、编辑策略、交互协议、权限控制和任务推进方式。它的强不是因为模型裸能力强，而是模型能力被一个相对完整的运行时持续承载。

所以你问 Qwen3.5-Omni-Flash-Realtime 是否也需要一套专属运行时，我认为答案是：**需要，而且非常需要。**

更准确地说，Realtime Omni 模型比普通文本 agent 更需要专属运行时。因为它不是离散的“用户发一句，模型回一句”。它面对的是连续时间里的音频、视频、文本、工具、状态、打断、播放、字幕、延迟、噪声、回声、网络抖动、会话记忆和多端投影。只要运行时没有把这些对象管住，模型能力就会被环境偶然复杂性拖垮。

我们刚才看到的 Vision Agents Qwen 适配问题，就是一个小型证明：Qwen 本身有 realtime 事件，有 VAD，有 `response.audio.delta`，有 `input_audio_buffer.speech_started`，有 `response.cancel`，有音频和文本流式输出。但当前适配层没有把这些事件完整映射到本地播放控制、WebRTC 音轨清理、turn lifecycle、视频帧时序和错误恢复里。结果用户感知不是“模型不行”，而是“这个产品不像一个完整实时通话 agent”。

这就是运行时的意义：**模型拥有能力，不等于能力已经进入产品世界。运行时负责让能力在真实世界中成立。**

## Vision Agents 是不是运行时

Vision Agents 是运行时的一部分，或者说是一个通用 realtime agent 框架。它不是完全没有运行时意识。它有 agent、edge、conversation、RealtimeInferenceFlow、AudioOutputStream、GetStream transport、事件管理、音频输入输出、视频 forwarder、transcript store。这些都属于运行时部件。

但它不是 Qwen Realtime 的完整原生运行时。

原因不是它代码少，而是它的抽象中心不是 Qwen。它的设计是通用 realtime agent：接不同 provider，接不同 edge，抽象出 LLM/STT/TTS/VAD/Realtime。这个方向有价值，但代价是：provider 的细粒度协议语义很容易被压扁。

Qwen Realtime 的能力不是只有“音频进、音频出”。它有一套事件语法：`input_audio_buffer.*`、`response.*`、`conversation.item.*`、`input_image_buffer.*`、`response.cancel`、server VAD、audio transcript、audio delta、audio done、response done。一个 Qwen-native runtime 必须以这些事件为核心建模，而不是只把它们翻译成几个泛化事件。

当前 Vision Agents 的 Qwen 插件更像 adapter demo：能连上，能说话，能看图，能转写，但没有把 provider control plane 完整接入。它不是“把模型能力完全激发出来”的 runtime。

## 阿里云官方有没有现象级运行时

只凭我目前掌握和刚才调查过的材料，我不能断言阿里云内部测试用的完整框架是什么。大厂内部一定有测试 harness、压测工具、回放工具、指标面板、协议验证器、模型评测系统、SDK 集成测试。但这些是否组成一个面向开发者开放的、像 Codex/Claude Code 那样现象级的 realtime agent runtime，我没有看到明确证据。

公开层面能看到的是三类东西：

第一，DashScope / 百炼 Realtime API 和 SDK。它提供连接、session update、append audio/video、callback、事件分发等基础能力。

第二，官方示例仓库。示例展示了 server VAD、语音打断、流式音频播放、摄像头图像发送等能力。但示例是薄 harness，不是完整产品运行时。比如官方 Python 示例自己写了一个 `B64PCMPlayer`，收到 `input_audio_buffer.speech_started` 就 `cancel_playing()`，这很直接，也很说明问题：官方示例把很多运行时职责留给应用层。

第三，模型控制台和文档。它定义模型能力、事件、参数、音色、限流、计费、接口行为。

这些组合起来足够开发 demo，但还不是一个“现象级 Qwen Realtime Runtime”。至少我目前没有看到像 Codex 之于 Responses/GPT 那样，官方提供一个完整的、可扩展的、可长期运行的、具备工具生态和复杂会话治理的 Qwen Omni runtime。

所以我的判断是：**Qwen Realtime API 已经有模型能力和协议能力，但围绕它的完整运行时生态还没有形成 Codex/Claude Code 那种行业标杆形态。**

这不是说做不到，而是说现在公开可用的东西更接近“SDK + samples + 若干通用框架 adapter”。Vision Agents 是其中一个 adapter/runtime 尝试，但还没有达到模型原生完整适配。

## 什么叫完整

你说“没有最大，没有最小；渴了就是要水”。我理解这个意思：完整不是功能堆叠，不是“再加十个模块”。完整是对象的构成性条件。缺了这些条件，它就不再是一个能把 realtime omni 模型能力完整承载出来的运行时。

我会这样定义：

**Qwen Realtime 原生运行时，是一个以 Qwen Realtime 事件协议为中心，管理连续音视频输入、模型响应生成、本地播放、打断、上下文、工具、错误恢复、观测和多端投影的执行环境。它的职责是让模型的实时全模态能力在真实交互中保持低延迟、可打断、可同步、可恢复、可审计、可扩展。**

这个定义里有几个关键词。

“以事件协议为中心”：不是把 Qwen 当普通 LLM。Qwen Realtime 的基本单位不是 message，而是事件流。

“连续音视频输入”：它要处理时间，不只是处理内容。

“本地播放”：语音输出不是返回值，它会进入播放器和缓冲区。

“打断”：打断不是远端 cancel 一下，而是远端生成、本地音频、字幕、会话状态共同收敛。

“多端投影”：同一个模型响应会投影成声音、字幕、聊天记录、状态提示、日志、指标。

“可恢复”：实时系统一定会遇到 track 断开、WebSocket 抖动、音频空洞、摄像头重连、API error。

下面我按构成性条件拆开。

## 1. 协议原生事件机

完整运行时首先需要一个 Qwen-native event state machine。

它必须把 Qwen Realtime 的客户端事件和服务端事件作为一等对象：

- `session.created`
- `session.update`
- `input_audio_buffer.append`
- `input_audio_buffer.speech_started`
- `input_audio_buffer.speech_stopped`
- `input_audio_buffer.committed`
- `input_image_buffer.append`
- `conversation.item.input_audio_transcription.*`
- `response.created`
- `response.audio.delta`
- `response.audio.done`
- `response.audio_transcript.delta`
- `response.audio_transcript.done`
- `response.done`
- `response.cancel`
- `error`

这些事件不能只被零散 if/elif 消费。它们要进入一个明确的状态机：

- session 未连接
- session 已创建
- 正在接收用户音频
- 用户正在说话
- 用户说话结束
- 输入已提交
- 模型正在生成
- 模型正在输出音频
- 模型输出完成
- 响应被打断
- 会话错误/恢复

完整运行时必须知道每个事件在什么状态下合法，收到非法事件怎么处理，重复事件是否幂等，缺失事件怎么兜底，错误事件是否需要重置本地状态。

我们现在的问题之一，就是没有这个完整事件机。`_is_responding` 一个布尔值承担了太多职责。它不能表达“远端仍在生成”“本地仍在播放”“字幕仍在流式更新”“当前输入轮次是否已经 append audio”“视频帧是否可以发送”。

## 2. 音频输入运行时

完整运行时必须管理麦克风/WebRTC 输入到 Qwen 的整个链路。

它需要：

- 接收 WebRTC audio track。
- 按 Qwen 要求转成 16kHz、mono、16-bit PCM。
- 控制 chunk 大小和发送节奏。
- 区分用户真实语音、静音、回声、agent 自己的播放声。
- 支持 server VAD 模式下持续发送音频。
- 支持非 server VAD 模式下手动 commit。
- 对多参与者音频做选择、混音或拒绝。
- 处理音频 track unpublished / republished。
- 记录输入音频时间轴，能和视频帧对齐。

这里不能只“收到 pcm 就 send_audio”。真实通话里，音频输入是运行时的时钟。VAD、打断、视频帧发送、turn boundary 都依赖它。

## 3. 音频输出运行时

完整运行时必须有低延迟、可中断的音频播放器。

对于浏览器/WebRTC 场景，这个播放器不是 pyaudio，而是 outbound audio track 和浏览器播放缓冲。运行时要控制：

- `response.audio.delta` 到 PCM 的解码。
- PCM 格式转换和重采样。
- 20ms 或更细粒度的分块。
- 输出 buffer 上限。
- 首包播放延迟。
- 响应完成后的 tail flush。
- 用户打断时立即清 buffer。
- cancel 后丢弃迟到 audio delta。
- 避免旧响应的音频混进新响应。

官方示例的 `B64PCMPlayer.cancel_playing()` 做的就是这个职责的最小版本：清 b64 buffer 和 raw audio buffer。Qwen 原生运行时必须把这个职责做成核心能力，而不是让每个应用临时补。

## 4. 打断控制平面

这是完整运行时的核心。

打断不是一个函数，而是一组同步动作：

1. 服务端 VAD 或语义打断识别用户开始说话。
2. 本地立即停止播放当前 agent 音频。
3. 本地字幕/聊天投影停止继续追加旧响应，或标记为 interrupted。
4. 向 Qwen 发送 `response.cancel`，取消远端生成。
5. 丢弃已经到达但属于旧 response 的迟到 audio/text delta。
6. 清理当前 response id、item id、音频队列、agent transcript buffer。
7. 保留用户新语音输入，进入新一轮 turn。

OpenAI / Gemini 那种“自然打断”的体验，本质上就是这组动作做得快、做得一致。

Qwen 原生运行时应该把打断做成一等状态转换，而不是在某个 callback 里顺手 `cancel_response()`。

它还需要区分几类打断：

- 用户真实开始说话。
- 用户只是嗯、啊、附和声。
- 环境噪声误触发。
- 用户语音控制指令，比如“停一下”“说慢点”。
- 程序主动取消，比如用户点击停止按钮。
- 新任务覆盖旧任务。

Qwen 文档里提到语义打断，说明模型侧可以帮助识别意图。但运行时仍然要执行本地中断动作。模型判断“该不该打断”，运行时负责“如何让打断在产品里成立”。

## 5. 多模态时间轴

Realtime Omni 的“看”和“听”不是两个无关输入。完整运行时必须维护音频、视频、文本、工具事件的时间关系。

例如用户问“刚才那个东西是什么颜色”，模型要知道“刚才”指哪个视频片段。用户说话时摄像头帧在变，视频帧和音频 turn 必须有时序关系。

运行时需要：

- 按 fps 采样视频帧。
- 控制图像大小、质量、格式、上限。
- 记录 frame timestamp。
- 将 frame 绑定到当前音频输入窗口或当前 turn。
- 按 Qwen 规则保证先 audio 后 image。
- track 重连后重置图像发送状态。
- 避免无意义帧持续消耗 token 和带宽。
- 必要时选择关键帧，而不是机械 1 FPS。

当前 `include_video=True` + `fps=1` 只是最粗糙的策略。日志里的 `Error append image before append audio` 说明运行时没有正确维护 Qwen 的多模态输入时序。完整运行时必须把“图像属于哪一轮用户输入”建模出来。

## 6. 输出投影协调

Qwen 返回的同一响应会投影到多个表面：

- 音频播放。
- 实时字幕。
- 聊天记录。
- 日志。
- 指标。
- UI 状态。

完整运行时必须协调这些投影。

如果 transcript delta 很快，文字可能比语音先显示很多。这个不一定错，但运行时要决定产品语义：

- 是允许字幕抢跑？
- 还是字幕跟随音频播放进度？
- 聊天记录显示完整文本，字幕显示当前播放片段？
- 被打断时旧字幕如何收尾？
- 被打断的 assistant message 是否保留、截断、标记 interrupted？

OpenAI Voice 的体感不只是模型快，它的投影策略也被设计过。Qwen runtime 也需要明确这些策略。否则用户会觉得“文字全出来了，语音还在慢慢播”，这会破坏实时对话感。

## 7. 会话上下文与记忆

Realtime 模型会产生大量连续事件。完整运行时不能把所有 raw event 都塞回上下文，也不能只靠模型内部 session 黑箱。

它需要维护几种上下文：

- 当前 turn 的用户转写。
- 当前 turn 相关视频帧摘要或关键帧引用。
- assistant 已说出的内容。
- 被打断但未完成的内容。
- 用户明确确认的事实。
- 临时视觉状态，比如桌面上刚放了什么。
- 长会话摘要。
- 工具调用结果。

Codex 有上下文压缩、文件筛选、任务状态外化。Realtime Omni runtime 也需要自己的压缩机制：音视频输入太密，不能无限保留。它需要把连续感知压缩成可用状态，比如“最近 10 秒画面变化”“当前桌面物体列表”“用户刚问的指代对象”。

这不是模型裸 API 会自动替你做好的。模型 session 可能保留上下文，但产品级 runtime 需要可观察、可控、可修正的上下文层。

## 8. 工具与动作层

Qwen3.5-Omni 文档提到 function calling、联网搜索、语音控制等能力。完整运行时必须有工具层。

这包括：

- 工具 schema 注册。
- 工具调用事件解析。
- 工具权限控制。
- 工具执行超时。
- 工具结果回写模型。
- 工具动作投影给用户。
- 语音中断工具执行。
- 长工具任务的状态播报。
- 工具失败时的恢复策略。

如果没有工具层，Realtime Omni 只是会看会说的助手；有了工具层，它才是 agent。

类比 Codex：Codex 之所以是 coding agent，不是因为 GPT 会写代码，而是因为它能读文件、搜代码、打补丁、跑测试、管理计划、接受审查。Qwen Omni runtime 之所以是 realtime agent，也不能只靠会说话，它要能在实时对话里安全地执行动作。

## 9. 延迟与 QoS 控制

Realtime runtime 的完成性必须包括延迟控制。

它需要指标：

- 麦克风输入到 server VAD speech_started 的时间。
- 用户停止说话到 response.created 的时间。
- response.created 到 first text delta 的时间。
- response.created 到 first audio delta 的时间。
- first audio delta 到本地播放的时间。
- 打断触发到本地静音的时间。
- 打断触发到远端停止 delta 的时间。
- 视频帧采集到模型可用的时间。

官方示例里已经有 first text delay、first audio delay。完整运行时要把这些变成常规指标，而不是 demo 打印。

它还要有 QoS 策略：

- 网络慢时降视频 fps。
- 图片过大时压缩。
- 音频 buffer 过长时丢旧音频还是延迟播放。
- 模型响应太长时是否提示用户可打断。
- 多端延迟不一致时如何同步字幕和声音。

没有 QoS，实时系统会逐渐变成“能跑但不像实时”。

## 10. 错误恢复与生命周期

完整运行时必须处理错误，而不是只打印错误。

例如你日志里的：

```text
Error append image before append audio.
```

这类错误应该触发明确策略：暂停图像发送，等待下一段音频 append，重置当前 multimodal input state，而不是继续每隔一段时间报错。

还需要处理：

- WebSocket 断开。
- API key / 地域 / 模型权限错误。
- voice 不支持。
- audio format 错误。
- image 太大。
- session 超时。
- Stream track unpublished。
- 浏览器权限撤销。
- 用户离开 call。
- Ctrl+C graceful shutdown。

每类错误都要归属到对应状态机，而不是散落在日志里。

## 11. 回放、测试、评测

Codex 这种运行时之所以能复杂任务，是因为它不只是 live 执行，还有可测试的边界。Qwen Realtime runtime 也需要 replay/eval。

它应该能记录一次会话的事件流：

- 入站 audio chunk metadata。
- 视频帧 timestamp。
- Qwen server events。
- 本地播放事件。
- interrupt event。
- tool call。
- error。

然后可以离线回放：

- 是否在 speech_started 后 200ms 内 flush 音频？
- 被打断 response 是否还有迟到 delta 被播放？
- 视频帧是否在 audio 前被发送？
- 字幕是否和音频严重错位？
- 长会话摘要是否保留关键指代？

没有 replay，就只能靠人耳朵和主观感觉调 realtime，这是不可持续的。

## 12. 开发者接口

完整运行时还必须给开发者一个清楚接口。

应用开发者不应该直接处理几十种 raw event。它应该能订阅高层事件：

- user_speech_started
- user_speech_final_transcript
- assistant_speech_started
- assistant_audio_delta
- assistant_text_delta
- assistant_interrupted
- assistant_response_done
- visual_context_updated
- tool_call_started
- tool_call_done
- session_recovering
- session_failed

同时保留 raw event tap 给调试使用。

这就像 Codex 不要求每个用户直接操作 Responses API 的每个底层事件。运行时要把模型协议变成可用的工程接口。

## 13. 前端不是附属品

Realtime runtime 的前端也很重要。Electron、Web、CLI 都可以是前端，但它们必须消费同一个核心运行时。

对于 Qwen Realtime，前端要显示：

- 麦克风状态。
- 摄像头状态。
- agent 是否正在听。
- agent 是否正在想。
- agent 是否正在说。
- 是否可打断。
- 当前字幕。
- 聊天历史。
- 视频帧是否被模型接收。
- 网络/延迟状态。
- 错误和恢复状态。

如果前端只播放音频和显示聊天，它就无法让用户理解实时状态。OpenAI/Gemini 的体验里，“正在听/正在说/可打断”的状态反馈是核心交互的一部分。

## 14. 我认为完整运行时的最小构成性条件

不是“最小版本”，而是构成性条件。缺一个就不能叫完整原生 runtime。

1. Qwen Realtime 事件状态机。
2. 连续音频输入管理。
3. 可中断音频输出管理。
4. 服务端 VAD 和本地播放打断的统一控制面。
5. 视频帧时序和多模态上下文管理。
6. 文本、字幕、音频、日志、UI 状态的多投影协调。
7. response 生命周期管理，包括 started、audio done、response done、interrupted。
8. 迟到事件丢弃和 response epoch 管理。
9. 工具调用和动作执行层。
10. 长会话上下文压缩和摘要层。
11. 错误恢复和 session lifecycle。
12. 延迟、质量、成本指标。
13. 事件录制、回放、评测 harness。
14. 开发者 API 和前端消费接口。

这才是“水”。不是为了显得大，而是 realtime omni 这个对象本身就需要这些条件。它面对的不是单句文本生成，而是一个持续发生的多模态世界。

## 15. 当前我们应该如何定位 TideSync

TideSync 现在不应该被理解为“已经有了完整 Qwen runtime”。它现在是一个早期接入点：Stream call + Vision Agents + Qwen Realtime。

下一步如果继续做，方向不是在现有代码上随便补几个 if，而是要决定：TideSync 是继续依赖 Vision Agents 做通用 runtime，然后我们写一个更完整的 Qwen adapter；还是我们逐渐抽出一个 TideSync 自己的 Qwen Realtime runtime，把 Vision Agents/GetStream 当作边缘接入层。

我倾向后者或中间路线：短期 fork/包裹 Qwen plugin，补齐事件映射和打断；中期定义 TideSync 的 realtime core，把 Qwen event state machine、audio output、video timing、turn state 从通用框架里抽出来；长期再考虑 provider abstraction。

因为如果一开始就追求 provider-agnostic，很容易再次犯 Vision Agents 当前的问题：抽象层看起来通用，但 provider 的关键能力被压扁。Qwen Realtime 需要先被完整理解，再谈抽象。

## 16. 最后判断

你这个类比是成立的。Codex/Claude Code 证明了一件事：强模型需要强运行时。模型 API 给的是能力原料；运行时把能力变成可工作对象。

Qwen3.5-Omni-Flash-Realtime 这种模型更是如此。它不是一个普通 LLM endpoint，而是一个连续多模态事件系统。完整运行时必须围绕事件、时间、媒体、打断、上下文、工具和投影来设计。

当前 Vision Agents 是一个有价值的通用 agent runtime 起点，但不是 Qwen Realtime 的完整原生 runtime。它能让模型跑起来，但还没有把模型能力完整激发出来。

如果要做真正的 TideSync，核心工作不是“再接一个 SDK”，而是定义并实现一个 Qwen Realtime Harness：让每个模型事件都有归属，让每个用户动作都有即时反馈，让每段音频和视频都有时间关系，让每次打断都同时停止远端生成和本地播放，让上下文能长期维持，让错误能恢复，让行为能回放和评测。

这才是这个模型需要的完整运行时。
</Taylor>

