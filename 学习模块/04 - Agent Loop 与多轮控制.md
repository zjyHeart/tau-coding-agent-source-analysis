---
title: "Tau 学习模块 04 - Agent Loop 与多轮控制"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 04 - Agent Loop 与多轮控制

> [!summary] 本章解决什么
> 模块 03 的两次 provider 调用由谁决定？本章只读 loop 控制流：何时继续、何时停止、如何顺序执行多个工具，以及何时把消息交给下一次模型调用。

**官方概念参考**：[The agent loop](https://twotimespi.dev/concepts/#the-agent-loop)；进阶再读 [Agent loop & events](https://twotimespi.dev/internals/agent-loop/)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/internals/agent-loop.md) 的「What the loop does / What the loop does not do」。读完先回答：①什么时候继续下一轮？ ②什么时候停止或报错？

## 前置与产物

- 前置：[[03 - 工具定义与调用闭环]]。
- 重点源码：`src/tau_agent/loop.py` 的 `run_agent_loop()`、`_provider_context()`、`_assistant_events()`、`_execute_tool_call()`。
- 产物：一张状态转移表，至少包含“普通回答、工具调用、错误、达到上限”四行。

## 步骤 1：从成功路径建立骨架

从 `run_agent_loop()` 的 `agent_start` 读到 `agent_end`。只标四个位置：prompt 被加入 history、provider 被调用、assistant 被加入 history、tool result 被加入 history。把 `while` 的两层循环分别标出，再用 [[03 - 工具定义与调用闭环]] 的输出核对两个 `turn_start`。

## 步骤 2：解释终止条件

普通 assistant 没有 tool call 时，本轮结束；存在 tool call 时，执行后继续下一轮。`stop_reason` 为 `error/aborted` 时提前结束；`max_turns` 限制循环上限。读 `tests/test_agent_loop.py::test_agent_loop_stops_with_assistant_error_after_max_turns`，记下超过上限时 history 和事件里出现的错误消息。

## 步骤 3：观察多个工具的顺序

读 `for call in calls` 和 `tests/test_agent_loop.py::test_agent_loop_passes_call_id_signal_and_progress_to_tool`。检查工具进度怎样转成 `ToolExecutionUpdateEvent`。再看 `src/tau_agent/tools.py` 的 `execution_mode` 字段：在这个固定快照中，loop 仍逐个执行 calls；字段名称不能证明并行运行。

## 步骤 4：区分历史与 provider 上下文

`_provider_context()` 会为下一次请求准备可回放消息。读 `tests/test_agent_loop.py::test_agent_loop_excludes_empty_failed_assistant_from_next_provider_call`：失败消息可留在持久历史中，但空的失败 assistant 不一定继续传给 provider。写出这两个列表的用途，避免把“history 存在”误当作“模型看得到”。

## 运行验证与完成检查

~~~bash
rtk uv run pytest tests/test_agent_loop.py -q
~~~

能画出 `tool call → _execute_tool_call → tool result → 下一次 provider` 的箭头；能解释为何本章不需要打开 CLI 和 TUI。碰到复杂的 steering/follow-up 与取消，先记录接口位置，分别到 [[05 - Harness 与事件订阅]] 和 [[06 - 错误取消与历史修复]] 处理。

## 同步复刻任务（自己的学习版）

将上一章固定的两次调用改成 `mini_tau/loop.py` 的循环：没有 tool call 就停止，有 call 就继续，超过 `max_turns` 返回明确错误。自己的测试至少覆盖一次普通回答、一次工具调用、一次上限停止；不要求实现 Tau 的全部事件。

前置：[[03 - 工具定义与调用闭环]]；后续：[[05 - Harness 与事件订阅]]。深入资料：[[03 - Agent Harness、Agent Loop 与事件模型]]。
