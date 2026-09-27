---
title: "Tau 学习模块 02 - FakeProvider 与单轮回答"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 02 - FakeProvider 与单轮回答

> [!summary] 本章解决什么
> 先让模型“只回答一句话”，不引入工具。`FakeProvider` 回放预设事件，便于观察 Tau 如何把 provider 事件提升为 Agent 事件。

**官方概念参考**：[Providers and models](https://twotimespi.dev/concepts/#providers-and-models)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/internals/agent-loop.md) 的「Event-first design」。读完先回答：①stream event 与最终消息差在哪里？ ②为什么 delta 不等于一条 history 消息？

## 前置与产物

- 前置：[[01 - Agent 闭环与消息协议]]；会用 `async for`。
- 重点源码：`src/tau_ai/fake.py`、`src/tau_agent/provider_events.py`、`src/tau_agent/loop.py` 的 `_assistant_events()`。
- 产物：一个“输入事件 → 输出事件 → history 消息”的三列表。

## 步骤 1：先读现成的最小测试

打开 `tests/test_agent_harness.py::test_prompt_appends_user_and_assistant_with_pi_lifecycle`。只圈出 `FakeProvider` 的预设流、`AgentHarnessConfig`、`harness.prompt("Hi")` 和最终 history 断言。这里还没有工具，也没有网络请求。

## 步骤 2：先预测再运行

在源码目录执行：

~~~bash
rtk uv run pytest tests/test_agent_harness.py::test_prompt_appends_user_and_assistant_with_pi_lifecycle -q
rtk uv run pytest tests/test_agent_loop.py::test_agent_loop_streams_canonical_nested_events -q
~~~

第一个测试的 history 应只有 user 和 assistant；事件含 `agent_start`、`turn_start`、user 的 `message_start/end`、assistant 的 `message_start/end`、`turn_end`、`agent_end`。第二个测试增加两个 text delta，因此多出两个 `message_update`，但最终 assistant 仍是一条消息。

## 步骤 3：追踪两个协议层

在 `fake.py` 看 `FakeProvider.stream_response()` 如何逐个 yield 预设的 `AssistantMessageEvent`；在 `loop.py::_assistant_events()` 看 `AssistantStartEvent`、`AssistantDoneEvent` 和 delta 分别被转换成什么 `AgentEvent`。记录：谁负责生成 assistant 的最终消息，谁负责把它加入 history。

## 步骤 4：做一个小改动

参照上述测试，在 `tau-playground` 自己写一个单轮脚本，把回答从 “Hello” 改成 “你好”，并加入一个 text delta；打印事件类型和 history。不要改测试或 Tau 源码。预期只增加 `message_update`，history 中仍只有一条 assistant 消息。

## 完成检查

- 能说明 provider stream event、AgentEvent、canonical AssistantMessage 分别在哪里使用。
- 能预测加入一段 text delta 后事件数如何变化，而 history 消息数为何不变。
- 如果看到 `MessageStartEvent` 的 partial 内容与最终内容不同，能解释它还不是持久化边界。

## 同步复刻任务（自己的学习版）

在 `mini_tau/fake_provider.py` 实现“按预设次序返回 assistant”的对象，记录每次收到的 history；自己的测试断言用户问“Hi”时只发生一次调用、返回一条 assistant。先不用流式；再加一个可观察的 text delta。

## 跟练卡：把一次预设流送进 Harness

**最小代码：**[02_single_turn.py](../tau-playground/02_single_turn.py) 是完整可运行参考解。核心三步是让 `FakeProvider` 接收一组 `AssistantStartEvent → TextDeltaEvent → AssistantDoneEvent` → 构造 `AgentHarness(AgentHarnessConfig(...))` → 用 `async for` 消费 `harness.prompt("Hi")`。这里 `prompt()` 返回异步事件流，不能写成 `await harness.prompt("Hi")`。

**运行：**在 `tau-source/` 执行 `rtk uv run python ../tau-playground/02_single_turn.py`。**预期：**事件中恰有一次 `message_update`；`history: [('user', 'Hi'), ('assistant', '你好')]`；`provider_calls: 1`。

**改一个变量：**把 `TextDeltaEvent.delta` 从 `你好` 改成 `你`，保留最终 `AssistantDoneEvent.message` 为 `你好`。预测事件里的增量与最终 history 为什么不同。**参考解：**delta 是过程通知；最终 canonical assistant 由 done event 给出，因此 history 仍是 `你好`。要改变最终消息，修改 done event 中的 `answer`。

**排错：**若 `provider_calls: 0`，检查是否真的用 `async for` 消费了 `harness.prompt()`；只创建 async generator 并不会运行内部循环。若使用全局 Python 报 `ModuleNotFoundError`，回到 `tau-source/` 用 `rtk uv run`。

前置：[[01 - Agent 闭环与消息协议]]；后续：[[03 - 工具定义与调用闭环]]。
