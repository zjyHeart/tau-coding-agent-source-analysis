---
title: "Tau 学习模块 01 - Agent 闭环与消息协议"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 01 - Agent 闭环与消息协议

> [!summary] 本章解决什么
> 在读 loop 前，先弄清模型输出“调用工具”和程序真正“执行工具”是两件事；再认识历史记录里的四条消息。后续所有模块都复用这张最小消息图。

**官方概念参考**：[The agent loop](https://twotimespi.dev/concepts/#the-agent-loop)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/internals/agent-loop.md) 的「What the loop does」。读完先回答：①谁执行 tool call？ ②哪些消息会进入下一轮？

## 前置与产物

- 前置：[[00 - 环境与学习边界]]；知道字典和列表。
- 重点源码：`src/tau_agent/messages.py`、`src/tau_agent/tools.py`。
- 产物：一张四行消息表，列出角色、关键字段、谁产生、下一步交给谁。

## 步骤 1：用一个具体请求写出闭环

例子固定为“读 README.md 后告诉我内容”。手写：

1. 用户消息：`UserMessage(content="读 README.md")`。
2. 助手消息：含 `ToolCall(id="call-1", name="read", arguments={"path": "README.md"})`。
3. 工具结果：`ToolResultMessage(tool_call_id="call-1", tool_name="read", ...)`。
4. 助手最终消息：根据第三条回答。

解释为什么需要第二次模型调用：模型第一次只有“要读文件”的意图，直到程序执行并回填结果后，才有文件内容可用于回答。模型服务本身不直接执行本机 Python 工具。

## 步骤 2：逐个读四种结构

在 `messages.py` 只找 `UserMessage`、`ToolCall`、`AssistantMessage`、`ToolResultMessage`。记录字段 `role`、`content`、`id`、`tool_call_id`、`is_error`；不要一开始研究 thinking/image/usage。注意 assistant 的 `content` 是有序 block，可能只有工具调用而没有可见文字。

## 步骤 3：区分“消息”和“事件”

消息会进入 history，供下一轮模型读取；`message_start/update/end` 等事件用于通知运行过程。事件数可以多于消息数，流式 delta 也不必各自保存为一条会话消息。先画两条线：上方四条最终消息，下方运行时通知；在 [[02 - FakeProvider 与单轮回答]] 再用真实事件输出核对。

## 步骤 4：从测试验证序列化

在源码目录运行：

~~~bash
rtk uv run pytest tests/test_agent_types.py -q
~~~

重点读 `test_assistant_message_keeps_ordered_content_blocks` 和 `test_tool_result_message_records_canonical_tool_output`。自己预测模型序列化后 `ToolCall` 是否仍在 assistant 的 content 里，再读断言。能解释 `call.id` 与结果 `tool_call_id` 的配对，就是本章验收。

## 常见卡点与完成检查

- `ToolCall` 是模型提出的请求；`AgentTool.execute` 才发生实际副作用。
- `ToolResultMessage` 是消息，`ToolExecutionEndEvent` 是事件，两者有相关信息但用途不同。
- 能在不看代码时写对四条消息顺序，并指出产生它们的组件；否则先重做步骤 1。

## 同步复刻任务（自己的学习版）

在 `tau-playground/mini_tau/messages.py` 自己定义最小的 UserMessage、ToolCall、AssistantMessage、ToolResultMessage（dataclass 即可）；在 `tau-playground/tests/test_messages.py` 验证四条消息顺序和 call ID 配对。只做学习版必要字段，不复制 Tau 的完整 Pydantic 模型。测试命令见 [[00 - 环境与学习边界]]。

## 跟练卡：先跑官方模型，再写自己的 dataclass

**最小代码：**参考 [01_messages.py](../tau-playground/01_messages.py) 的完整可运行版本，先看这五行就够：

```python
call = ToolCall(id="call-1", name="read_demo", arguments={"path": "README.md"})
history = [UserMessage(content="读 README.md"),
           AssistantMessage(content=[call], model="fake", stop_reason="toolUse"),
           ToolResultMessage(tool_call_id=call.id, tool_name=call.name, content="模拟读取结果"),
           AssistantMessage(content="README.md 的示例内容", model="fake")]
```

**运行：**在 `tau-source/` 执行 `rtk uv run python ../tau-playground/01_messages.py`。**预期：**依次输出 `user → assistant → toolResult → assistant`，第二行 assistant 的 `text` 为空，最后输出 `call_id_matched: True`。这只是在构造消息，尚未调用 provider 或执行工具。

**改一个变量：**把 `call.id` 改成 `call-2`，但把结果的 `tool_call_id` 固定写成 `call-1`，预测最后的断言如何失败。**参考解：**结果的 `tool_call_id=call.id`；ID 由请求带到结果，不能凭角色顺序猜配对。恢复后再写自己的 dataclass 版本，至少保留 `role`、`content`、`id/tool_call_id`。

**排错：**`AssistantMessage.content` 是 block 列表，`text` 属性只拼可见文字，所以只有 `ToolCall` 时打印空字符串并非丢失工具调用；检查 `history[1].tool_calls`。

前置：[[00 - 环境与学习边界]]；后续：[[02 - FakeProvider 与单轮回答]]。深入资料：[[03 - Agent Harness、Agent Loop 与事件模型]]。
