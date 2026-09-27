---
title: "Tau 学习模块 10 - Session 日志与分支"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 10 - Session 日志与分支

> [!summary] 本章解决什么
> `harness.messages` 只是内存中的运行历史。Tau 的 Session 还要落盘、恢复、保留分支。本章先掌握 JSONL entry 与活动路径，下一章再看 `CodingSession` 如何把事件写进去。

**官方概念参考**：[Sessions](https://twotimespi.dev/concepts/#sessions)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/guides/sessions.md) 的「Resuming / Branching from history」。读完先回答：①磁盘日志与当前分支是什么关系？ ②切换分支会删除另一支吗？

## 前置与产物

- 前置：[[09 - 提示词上下文与项目信任]]；熟悉四条消息和 event listener。
- 源码：`src/tau_agent/session/entries.py`、`jsonl.py`、`storage.py`、`tree.py`、`memory.py`。
- 产物：一份小型 Session 树示意图，标出 `parent_id`、活动 leaf、两条不同的投影结果。

## 步骤 1：从“一行一个 entry”开始

读 `tests/test_session.py::test_session_entry_round_trips_canonical_jsonl` 和 `test_jsonl_storage_appends_and_reads_entries`。对照 `entries.py` 识别消息、模型/设置与历史兼容的 `LeafEntry`；不要把 JSONL 的一行直接等同于一条聊天消息。v0.4.5 **不再写新的 `LeafEntry`**，旧记录仍可读，但恢复时不能把它当作活动指针。保存时应是 UTF-8，并能读回相同结构。

## 步骤 2：理解 append-only 与活动路径

读 `tree.py::path_to_entry` 对应的 `test_path_to_entry_follows_parent_chain`。画一个父节点后分出两条子路径的图；各选一个末端 entry，列出从根走到它的 entry。切换活动分支不要求删除另一条历史。普通 `/tree` 选择先只改内存中的 tip；若退出前没有后续写入，重开后仍按 JSONL 文件顺序选择最后一个非旧式 `leaf` entry。

## 步骤 3：把路径投影成模型上下文

读 `memory.py` 的 `SessionState.from_entries()`，再读 `tests/test_session.py::test_session_state_replays_linear_entries` 与 `test_session_state_applies_compaction_and_branch_summary`。比较“磁盘上全部 entries”“当前分支上的 entries”“交给模型的 active messages”，这三者不一定相同。

## 步骤 4：处理坏数据与旧格式

看 `test_invalid_jsonl_line_raises_useful_error`、`test_path_to_entry_rejects_missing_or_cyclic_parent` 和一个 legacy migration 测试。写出错误应该在哪个边界暴露或迁移；不要在练习中手工改写固定源码的历史文件。

## 运行验证与完成检查

~~~bash
rtk uv run pytest tests/test_session.py -q
~~~

能解释 `parent_id`、当前末端 entry 与 `SessionState` 各做什么；能画出同一 JSONL 中两个末端 entry 对应不同上下文，并解释旧 `LeafEntry` 为什么不能再决定恢复分支。若把 Session 描述成“直接修改一个 Python 消息列表”，回看步骤 1–3。

## 同步复刻任务（自己的学习版）

在 `mini_tau/session.py` 用 UTF-8 JSONL 追加最小 entry，并通过 parent ID 找活动路径；测试线性恢复、两个末端 entry 的不同投影、缺失 parent 的错误。另写一个测试：选择旧节点但不写新 entry 时，重开应回到文件中最后写入的非 leaf entry。先不复刻 Tau 的所有 entry 类型。

前置：[[09 - 提示词上下文与项目信任]]；后续：[[11 - CodingSession 持久化与压缩]]。深入资料：[[06 - Session、分支、恢复与上下文压缩]]。
