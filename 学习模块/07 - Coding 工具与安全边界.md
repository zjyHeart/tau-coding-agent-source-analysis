---
title: "Tau 学习模块 07 - Coding 工具与安全边界"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 07 - Coding 工具与安全边界

> [!summary] 本章解决什么
> 把 [[03 - 工具定义与调用闭环]] 的无副作用工具换成真实的文件/进程工具，弄清参数、文件写入、取消、超时及权限边界。

**官方概念参考**：[Tools](https://twotimespi.dev/concepts/#tools) 与 [Tools reference](https://twotimespi.dev/reference/tools/)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/reference/tools.md) 的「read / write / edit / bash」。读完先回答：①哪种工具有文件或进程副作用？ ②cwd 为什么不是沙箱？

## 前置与产物

- 前置：[[06 - 错误取消与历史修复]]。
- 源码：`src/tau_coding/tools.py`、`src/tau_agent/tools.py`、`src/tau_coding/data/docs/security.md`。
- 产物：`read/write/edit/bash` 四行能力表，每行列出参数、真实副作用、失败分支、对应测试。

## 步骤 1：读工具是怎样被注册的

在 `create_coding_tools()` 找初始工具集合。比较 `ToolDefinition` 与核心层 `AgentTool`：谁提供 schema、description、执行函数和面向 prompt 的说明。运行 `tests/test_coding_tools.py::test_create_coding_tools_returns_initial_tool_set`，确认工具名不是从提示词自由生成的。

## 步骤 2：先读，不写

看 `read` 的 offset/limit、文本与图片分支，再运行 `test_read_tool_reads_file_with_offset_and_limit`。在 `tau-playground` 自己创建一个 UTF-8 小文件作为练习对象；先预测“只读第几行”，再执行/核对。不要把 toy agent 的模拟返回误认成真实文件读取。

## 步骤 3：在自己的文件上观察写与改

看 `test_write_tool_creates_parent_directories`、`test_edit_tool_applies_multiple_exact_replacements`、`test_edit_tool_rolls_back_when_any_edit_fails`、`test_edit_tool_requires_unique_matches`。先写出编辑前内容，再预测成功/失败后内容；只在练习目录的普通文件上实验。关键问题是多处 edit 为什么要先验证，再落盘；失败时哪些内容应保持原样。

## 步骤 4：把 Bash 当作进程能力

看 `test_bash_tool_reports_timeout` 与 `test_bash_tool_timeout_kills_shell_children`，再读工具实现中的超时、取消、输出截断路径。先只运行测试，不让模型自由生成命令。记录：`cwd` 是相对路径的基准，不是操作系统沙箱；project trust 与系统提示词也不会自动限制文件、进程和网络权限。

## 步骤 5：集中验证

~~~bash
rtk uv run pytest tests/test_coding_tools.py -q
~~~

这份固定快照没有默认的 workspace sandbox 或逐命令审批。学习时应把真实副作用和“模型是否愿意遵守提示”分开讨论；具体安全结论参考 [[08 - 安全边界、测试体系、局限与设计评价]]。

## 完成检查

能指出四个内置工具各自的副作用，解释至少一个失败后不应改变文件的场景，并说明为什么不能用 `cwd` 代替沙箱。

## 同步复刻任务（自己的学习版）

只给 `mini_tau` 增加一个限制在练习目录内、读取自己 UTF-8 文件的 read 工具，测试路径、offset/limit 和文件不存在；write/edit/bash 可先只读 Tau 的实现。若扩展它们，必须只操作练习目录并为失败不改动写测试。

前置：[[06 - 错误取消与历史修复]]；后续：[[08 - Provider 适配与自定义 API]]。
