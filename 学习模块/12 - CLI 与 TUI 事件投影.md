---
title: "Tau 学习模块 12 - CLI 与 TUI 事件投影"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 12 - CLI 与 TUI 事件投影

> [!summary] 本章解决什么
> 同一套 AgentEvent 怎样变成命令行输出和交互界面？本章从输入入口走到 renderer/adapter，避免把 TUI 显示分组误读成工具执行或 Session 历史变化。

**官方概念参考**：[Two interfaces](https://twotimespi.dev/concepts/#two-interfaces)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/guides/print-mode.md) 的「Print mode」。读完先回答：①何时选择 plain、JSON 或 transcript？ ②它们共享哪一层 Agent 状态？

## 前置与产物

- 前置：[[11 - CodingSession 持久化与压缩]]。
- 源码：`pyproject.toml` 的 `tau` 入口、`src/tau_coding/cli.py`、`src/tau_coding/rendering/`、`src/tau_coding/tui/adapter.py`、`tui/state.py`。
- 产物：两条不超过十个节点的路径：print-mode 路径与 TUI 路径；标出共同的 `CodingSession` 与 Harness。

## 步骤 1：从命令入口追到 Session

从 `pyproject.toml` 找 `tau` 可执行入口；在 `cli.py` 找 `main()`、`run_print_mode()`、TUI 路由。读 `tests/test_cli.py::test_cli_without_prompt_invokes_tui_runner` 与 `test_run_print_mode_prints_final_assistant_text`。写下是 CLI 选择模式，还是 Agent loop 自己决定模式。

## 步骤 2：比较三种 print 输出

在 `rendering/plain.py`、`json.py`、`transcript.py` 找渲染入口。读 `tests/test_rendering.py::test_final_text_renderer_prints_only_final_message`、`test_json_renderer_emits_canonical_jsonl`、`test_transcript_renderer_streams_text_and_tool_events`。用同一事件流比较“只要最终答案”“结构化记录”“过程转录”三个用途。

v0.4.5 还提供 RPC 入口和 TUI 资源编辑交互；把它们列为应用层新增入口，先不在本章追完。想进阶时分别从 `src/tau_coding/rpc.py` 与 `src/tau_coding/tui/app.py` 追到同一个 `CodingSession`，不要把新入口误认为新 Agent loop。

## 步骤 3：看 TUI 如何形成显示状态

读 `tui/adapter.py::TuiEventAdapter` 与 `tui/state.py`，再看 `tests/test_tui_adapter.py::test_tui_adapter_builds_assistant_item_from_nested_stream_events`。标出 partial update 与最终 `MessageEndEvent` 分别怎样影响 UI item。TUI 不负责执行 `read/write/edit/bash`。

## 步骤 4：核对恢复与分组

读 `test_tui_state_restores_persisted_assistant_blocks_in_order` 和 `test_file_mutation_continuation_boundaries_match_live_and_restored`。说明界面把连续 edit/write 显示成组，不等于 loop 并行执行、不等于 JSONL 只剩一条。与 [[10 - Session 日志与分支]] 的磁盘 entries 对照。

## 运行验证与完成检查

~~~bash
rtk uv run pytest tests/test_cli.py tests/test_rendering.py tests/test_tui_adapter.py -q
~~~

能指出 CLI/TUI 的分岔点及共享内核；能从同一条事件指出 print 和 TUI 各自输出了什么。若把 UI 分组当成模型上下文压缩，回看步骤 4。

## 同步复刻任务（自己的学习版）

给练习版写 `mini_tau/renderer.py`，接收相同事件序列，提供“只输出最终回答”和“打印工具执行过程”两种文本投影；测试两者共享同一 history。无需实现 Textual TUI。

前置：[[11 - CodingSession 持久化与压缩]]；后续：[[13 - Extensions 与自定义工具]]。深入资料：[[07 - Extensions、CLI、TUI 与前端边界]]。
