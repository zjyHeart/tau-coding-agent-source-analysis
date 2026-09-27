---
title: "Tau 学习模块 11 - CodingSession 持久化与压缩"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 11 - CodingSession 持久化与压缩

> [!summary] 本章解决什么
> `CodingSession` 把 Harness、工具、prompt、资源、provider 与 Session storage 组装成可恢复的 coding agent。本章只追一次请求和一次取消/压缩，不逐行读完整个大文件。

**官方概念参考**：[Sessions](https://twotimespi.dev/concepts/#sessions) 与 [Context and compaction](https://twotimespi.dev/concepts/#context-and-compaction)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/guides/context.md) 的「compaction 与上下文管理」。读完先回答：①摘要替换哪部分模型上下文？ ②原始 JSONL 是否仍保留？

## 前置与产物

- 前置：[[10 - Session 日志与分支]]。
- 源码：`src/tau_coding/session.py`、`context_window.py`、`session_usage.py`、`branch_summary.py`。
- 产物：一张“事件 → listener → JSONL → 恢复 → active context”的时序图和一张压缩前后对比表。

## 步骤 1：只看组装入口

在 `CodingSession.load()` 找 provider、tools、system prompt、Session storage、Harness 的创建顺序。把每一项连回前面已经学过的模块，不要跳入所有辅助方法。回答：`AgentHarness` 为什么不能单独代表完整 coding agent？

## 步骤 2：追一条普通请求

从 `CodingSession.prompt()` 追到 Harness，再找事件监听者如何持久化消息。读 `tests/test_coding_session.py::test_prompt_persists_user_and_assistant_entries_without_leaves`：确认 user/assistant 写成 `MessageEntry`，`leaf_entries == []`。比较“UI 消费 `async for`”与“订阅者 push 写盘”：即便前端中途不再渲染，持久化也不应仅依赖 UI 循环。

## 步骤 3：追取消后的修复

读 `tests/test_coding_session.py::test_cancelled_prompt_teardown_persists_interrupted_tool_result` 与 `test_load_persists_repair_for_session_with_interrupted_tail_tool_call`。画出取消 → synthetic tool result → listener → JSONL → 下次加载的链路。要区分 Harness 负责补齐消息、CodingSession 负责写入和恢复。

## 步骤 4：研究压缩，但保留历史

在 `session.py` 搜 compaction 相关方法，读 `context_window.py` 和 `tests/test_session.py::test_session_state_applies_compaction_and_branch_summary`。分别记录压缩前后：磁盘原始 entries 是否还在、活动上下文给模型哪些消息、摘要可能丢失哪些细节。不要把压缩当作文件删除。

## 步骤 5：看可靠性分支

读 `tests/test_coding_session.py::test_message_persistence_retry_is_idempotent` 与 `test_next_prompt_flushes_a_repair_that_failed_twice`。写出一次写入失败怎样被后续动作发现和修复；证据来自测试，不用凭异常名字猜测。

## 运行验证与完成检查

~~~bash
rtk uv run pytest tests/test_coding_session.py tests/test_context_window.py -q
~~~

能区分“原始会话日志”“当前分支”“模型可见上下文”“界面显示内容”；能解释取消修复为何需要事件订阅者。

## 同步复刻任务（自己的学习版）

在练习版把 Harness 的终态消息交给 Session 写入；测试一次正常请求和一次缺失工具结果的恢复。再实现一个“旧消息摘要替代活动上下文”的最小示例，断言原始 JSONL 仍保留；摘要质量不作生产保证。

**版本关键点：**对照 [drop-leaf 设计说明](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/dev-notes/drop-leaf-session-entries.md) 与 `tests/test_coding_session.py::test_prompt_persists_user_and_assistant_entries_without_leaves`。持久化重试只重试同一个稳定 ID 的 entry；普通 `/tree` 导航本身不写盘，后续消息/设置写入才让新分支持久化。

前置：[[10 - Session 日志与分支]]；后续：[[12 - CLI 与 TUI 事件投影]]。
