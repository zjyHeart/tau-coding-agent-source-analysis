---
title: "Tau 学习模块 05 - Harness 与事件订阅"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 05 - Harness 与事件订阅

> [!summary] 本章解决什么
> Loop 负责一轮轮调用模型和工具；`AgentHarness` 在外层保管消息、运行状态、订阅者与排队输入。本章把“核心在运行什么”和“外部如何观察/插话”分开。

**官方概念参考**：[The agent loop](https://twotimespi.dev/concepts/#the-agent-loop)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/internals/architecture.md) 的「AgentHarness / AgentSession / TUI」。读完先回答：①谁保存运行时 history？ ②事件订阅者为何要在 UI 外面？

## 前置与产物

- 前置：[[04 - Agent Loop 与多轮控制]]。
- 源码：`src/tau_agent/harness.py`、`src/tau_agent/events.py`。
- 产物：一张 `Harness → Loop → EventListener/async for` 的所有权图，以及一个订阅实验的输出。

## 步骤 1：找出对象持有的状态

读 `AgentHarness.__init__`，只标 `_messages`、`_running`、`_current_signal`、`_listeners`、`_steering_queue` 和 `_follow_up_queue`。写明它们为什么不能都放进无状态的 provider 对象。再读 `prompt() → _run() → run_agent_loop()`，验证 Harness 并没有重新实现另一套工具循环。

## 步骤 2：比较两种事件消费者

`async for event in harness.prompt(...)` 是拉取事件；`harness.subscribe(listener)` 是推送订阅。复制 `tests/test_agent_harness.py::test_subscribers_receive_nested_message_updates_and_unsubscribe` 的思路，在 `tau-playground` 的 toy 脚本里加一个 `seen=[]` 和 listener，结束后比较 `seen` 与原先收集到的 `events`。预期在订阅期间看到同一轮的事件；取消订阅后 listener 不再接收下一轮。

## 步骤 3：用测试观察队列

读 `steer()`、`follow_up()`、`_drain_steering_messages()` 和 `_drain_follow_up_messages()`。运行：

~~~bash
rtk uv run pytest tests/test_agent_harness.py::test_harness_rejects_overlap_and_drains_followups -q
rtk uv run pytest tests/test_agent_harness.py::test_harness_queue_mode_all_drains_messages_together -q
~~~

预测在 Agent 正运行时再调用 `prompt()` 会怎样；再对比 `follow_up()` 是排队而不是抢占。写出 `queue_mode="one_at_a_time"` 与 `"all"` 对消息批次的影响，不需要先研究 TUI 输入框。

## 步骤 4：把事件归到三层

在 `events.py` 把事件按 run、turn、message、tool 四组列出来。对照 toy 输出，标出 `agent_end` 不等于 Session 写盘结束；后续 [[11 - CodingSession 持久化与压缩]] 才看应用层完成状态。

## 完成检查

能回答：谁保存 history，谁执行工具，谁通知监听者，为什么“一个运行中再启动第二个运行”会报错。暂不深入取消的 teardown，下一章专门处理。

## 同步复刻任务（自己的学习版）

在 `mini_tau/events.py` 定义 run/turn/message/tool 的最小事件；在 `mini_tau/harness.py` 保存 history 与 listener，并拒绝重叠运行。**本章必须实现最小 follow-up 队列**：运行中 `follow_up("第二个问题")` 先排队，当前轮完成后再送入下一次 provider 调用；先只实现 `one_at_a_time`，`all` 模式留作选做。测试断言成功路径事件顺序、listener 收到事件、取消订阅后不再收到事件、重叠启动被拒绝，以及 follow-up 最终被消费。模块 14 的内核验收将直接复用这些测试。

前置：[[04 - Agent Loop 与多轮控制]]；后续：[[06 - 错误取消与历史修复]]。
