---
title: "Tau 学习模块 13 - Extensions 与自定义工具"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 13 - Extensions 与自定义工具

> [!summary] 本章解决什么
> 学习在不改 Agent loop 的前提下，如何注册自定义工具、命令与 hook，并理解加载、reload 和信任边界。自定义工具与“自定义模型 API”是两条不同扩展路径。

**官方概念参考**：[Tools](https://twotimespi.dev/concepts/#tools)；扩展细节见 [Extensions guide](https://twotimespi.dev/guides/extensions/)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/guides/extensions.md) 的「Quick start / Tools / Dynamic providers」。读完先回答：①工具扩展和动态模型 provider 是同一种接口吗？ ②reload 怎样避免旧注册残留？

## 前置与产物

- 前置：[[12 - CLI 与 TUI 事件投影]]；已学 [[07 - Coding 工具与安全边界]] 的工具契约。
- 源码：`src/tau_coding/extensions/loader.py`、`api.py`、`runtime.py`、`src/tau_coding/data/examples/extensions/hello_tool.py`、`src/tau_coding/reload.py`。
- 产物：一个只读练习扩展的设计草图，列出注册入口、工具参数、返回值、hook 拒绝条件和 reload 检查。

## 步骤 1：读最小示例

打开 `hello_tool.py`，找扩展的 setup/注册入口；再到 `api.py` 找对外 API 的工具注册方法。与核心层 `AgentTool` 比较：扩展是在应用层把工具添加到 Harness 可用集合，不要求修改 `loop.py`。

## 步骤 2：追加载和优先级

在 `loader.py` 找发现用户级、显式路径、项目级扩展的顺序；读 `tests/test_extensions.py::test_discovers_user_extensions_and_skips_project_by_default` 与 `test_explicit_extension_paths_load_even_with_discovery_disabled`。项目扩展还要结合 [[09 - 提示词上下文与项目信任]] 的 trust 条件，不是发现文件就无条件 import。

## 步骤 3：看工具与 hook 怎样进入运行时

读 `tests/test_extensions.py::test_extension_tool_registration_and_composition` 和 `test_raising_tool_call_hook_blocks_fail_safe`。画出“注册 → 工具列表/Hook → Harness before/after tool call → 结果事件”的路径。思考 hook 抛异常为什么需要 fail-safe；不要让一个扩展异常悄悄放行危险操作。

## 步骤 4：做一个只读练习

在 `tau-playground` 写一个返回固定文本的工具扩展，不访问真实文件和网络；再加一个按参数拒绝的 hook。先模仿 `hello_tool.py` 与测试夹具，不直接放进正在工作的项目。验收重点是注册成功、拒绝可见、reload 不留下旧回调，而不只是“启动没报错”。

## 步骤 5：运行测试与标注边界

~~~bash
rtk uv run pytest tests/test_extensions.py tests/test_example_extensions.py -q
~~~

Python 扩展被 import 后是受信任代码，不是沙箱。能指出加载、注册、执行、reload、project trust 分别由哪一层负责；能解释 PackyAPI 配置应回 [[08 - Provider 适配与自定义 API]]，不是在本章注册一个工具来替代模型。

**v0.4.5 选读：**`extensions/provider_registry.py`、`extensions/providers.py`、`local_backends.py` 和 `tests/test_extension_providers.py` 展示进程内动态模型 provider；内置 `llama.cpp` 后端属于这条扩展路径。它与本章的自定义工具、模块 08 的用户级持久 provider 都不同。画一张三列表：注册对象、是否写入 `catalog.toml`、生命周期归谁；初学阶段只读，不要求复刻动态注册/取消/重载机制。

## 同步复刻任务（自己的学习版）

给练习版添加一个简单的工具注册入口与执行前 hook；测试只读工具能注册、拒绝条件可见、重复注册按你写明的规则处理。对照 Tau 扩展机制列出尚未实现的发现、trust 与 reload，不把自己的练习版称为 Tau 扩展兼容。

前置：[[12 - CLI 与 TUI 事件投影]]；后续：[[14 - 最小复刻与最终验收]]。
