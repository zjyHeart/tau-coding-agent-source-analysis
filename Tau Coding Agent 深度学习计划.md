---
title: "Tau Coding Agent 深度学习计划"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习计划
source_type: learning-plan
source_repo: "https://github.com/huggingface/tau"
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# Tau Coding Agent 深度学习计划

> [!info] 学习对象与证据边界
> 本计划研究 [huggingface/tau](https://github.com/huggingface/tau) 的固定源码快照 [`c66fb879`](https://github.com/huggingface/tau/tree/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3)（2026-09-23，项目版本 `0.4.5`，Python 3.12+）。本地可按 [README](README.md) 将该 commit 克隆到本目录的 `tau-source/`；GitHub 仓库只保存分析笔记和练习代码。官网会继续更新；具体实现以此 commit 的源码、测试和同 commit 文档为准。

## 这套计划究竟要学什么

目标是**边运行、边拆解 Tau，并逐章实现一个小型 Agent 内核**。每章先用现有 Tau 的测试确认行为，再在 `tau-playground/mini_tau/` 增量实现一个同概念的小件；模块 14 做集成验收。这个练习是以 Tau 为参照的最小复刻，不是从零重建完整 Tau。学习对象有三层：`tau_ai` 的模型适配、`tau_agent` 的消息/工具/loop/Harness、`tau_coding` 的 coding 工具/资源/Session/UI。先掌握“模型请求工具 → 程序执行 → 结果回填 → 模型再回答”，再看产品工程层。

本计划按章节化教程组织：先给整条主线，每章再拆成问题、前置、源码入口、逐步操作、验证、产物与过关标准。Tau 的具体事实来自固定源码，不从其他教程迁移实现结论。

## 官方文档作为概念主教材

先读 [Tau 官方 Core concepts](https://twotimespi.dev/concepts/) 建立术语和功能图景，再进入每章的代码/测试。本次官网显示 v0.4.5，与固定源码的项目版本一致；各章还给出同 commit 的 `website/content/` 文档链接，用于避免官网以后更新造成漂移。**功能说明看官方文档，具体调用与边界再由源码和测试确认**。

| 官方概念入口 | 对应学习模块 | 深入的官方页面 |
| --- | --- | --- |
| [Agent loop](https://twotimespi.dev/concepts/#the-agent-loop) | 01、03–06、14 | [Agent loop & events](https://twotimespi.dev/internals/agent-loop/) |
| [Providers and models](https://twotimespi.dev/concepts/#providers-and-models) | 02、08 | [Providers & models](https://twotimespi.dev/guides/providers-and-models/) |
| [Tools](https://twotimespi.dev/concepts/#tools) | 03、07、13 | [Tools reference](https://twotimespi.dev/reference/tools/) |
| [Sessions](https://twotimespi.dev/concepts/#sessions) | 10、11 | [Sessions guide](https://twotimespi.dev/guides/sessions/) |
| [Project instructions](https://twotimespi.dev/concepts/#project-instructions-agentsmd)、[Skills](https://twotimespi.dev/concepts/#skills-and-prompt-templates) | 09 | [Project instructions](https://twotimespi.dev/guides/project-instructions/) |
| [Context and compaction](https://twotimespi.dev/concepts/#context-and-compaction) | 11 | [Managing context](https://twotimespi.dev/guides/context/) |
| [Two interfaces](https://twotimespi.dev/concepts/#two-interfaces) | 12 | [TUI](https://twotimespi.dev/guides/tui/)、[Print mode](https://twotimespi.dev/guides/print-mode/) |
| 扩展主题（Concepts 页面不展开） | 13 | [Extensions guide](https://twotimespi.dev/guides/extensions/) |

每章先读表中对应的 Concepts 小节，再按章内“本章定向阅读”读同 commit 官方文档的指定小节，回答两个问题；随后用本章测试和源码核对“`c66fb879` 实际怎样实现”。API 中转是否真正兼容还需另查中转服务自己的接口说明与测试返回。

## 一条主线：先跑通，再逐层加固

~~~text
环境和术语
  → 四条消息的 Agent 闭环
  → FakeProvider 单轮回答
  → 无副作用工具 + 两轮模型调用
  → Loop 多轮控制 + Harness/事件
  → 未知工具、异常、取消和历史修复
  → 真实 coding 工具与安全边界
  → Provider/自定义 API、提示词/上下文/信任
  → Session 日志、CodingSession 持久化/压缩
  → CLI/TUI、Extensions
  → 自己复刻一个有测试的小内核
~~~

每一章只新增一层能力，并明确“它解决了上章留下的什么问题”。进阶工程能力不会在第一章同时压给初学者。

## 两个工作目录，各做一件事

| 位置 | 用途 | 操作边界 |
| --- | --- | --- |
| 本目录的 `tau-source/` | v0.4.5 固定源码、`pyproject.toml`、定向 pytest；以下 `rtk uv ...` 命令默认从这里执行 | 保持 `c66fb879` 快照不变 |
| 本目录的 `tau-playground/` | 01–03 可运行示例、自己的临时文本和最终 `mini_tau/` | 与 Tau 源码分开 |

入口验证：在 `tau-source/` 执行 `rtk git rev-parse --short HEAD`，预期 `c66fb87`；再执行 `rtk uv sync --dev --locked`。按顺序运行 `rtk uv run python ../tau-playground/01_messages.py`、`rtk uv run python ../tau-playground/02_single_turn.py`、`rtk uv run python ../tau-playground/toy_agent.py`，预期分别是四条构造消息、一次 provider 调用、两次 provider 调用且四条 history 消息。`rtk` 是本地终端代理；没有安装 `rtk` 时去掉命令前缀即可。00–07 的练习用 `FakeProvider`，不需要 API Key；模块 08 才研究真实/中转 API。

自己的复刻代码放在 `tau-playground/mini_tau/`，自己的测试放在 `tau-playground/tests/`。从 `tau-playground/` 运行自己的测试时使用 `rtk uv run --project ../tau-source python -m pytest tests -q`；它借用 Tau 的开发依赖，但测试的是你自己的练习代码。与 Tau 原仓库测试分开记录结果。

## 逐章路线

### 第一段：把 Agent 的最短闭环跑通【必修】

| 模块 | 要解决的问题 | 本章可检查的产物 |
| --- | --- | --- |
| [[00 - 环境与学习边界]] | 源码与练习目录如何分开？Python/pytest 能否运行？ | commit、测试结果、三层包职责表 |
| [[01 - Agent 闭环与消息协议]] | 用户、assistant/tool call、tool result 如何组成历史？ | 四条消息表、`id/tool_call_id` 配对 |
| [[02 - FakeProvider 与单轮回答]] | 没有工具时 provider 事件怎样变成 AgentEvent？ | 单轮输出及“事件 vs 消息”对照表 |
| [[03 - 工具定义与调用闭环]] | 为什么需要两次模型调用，工具在哪里执行？ | 运行 `toy_agent.py`，记录四条消息与事件序列 |

### 第二段：看懂可复用 Agent 内核【必修】

| 模块 | 要解决的问题 | 本章可检查的产物 |
| --- | --- | --- |
| [[04 - Agent Loop 与多轮控制]] | 哪些条件让 loop 继续或停止？ | 普通回答、工具调用、错误、上限状态表 |
| [[05 - Harness 与事件订阅]] | 谁持有历史，谁通知 listener，运行中如何排队输入？ | Harness/Loop 所有权图与订阅实验 |
| [[06 - 错误取消与历史修复]] | 未知工具、异常、取消后 history 如何保持可继续？ | 故障矩阵和 synthetic result 时序 |
| [[07 - Coding 工具与安全边界]] | `read/write/edit/bash` 的实际副作用和权限边界是什么？ | 四工具副作用/失败/测试表 |

### 第三段：把内核装成可配置的 coding agent【按目标深入】

| 模块 | 要解决的问题 | 本章可检查的产物 |
| --- | --- | --- |
| [[08 - Provider 适配与自定义 API]] | `/login custom`、`tau setup`、Catalog、凭证和适配器如何连接？PackyAPI 需要核对哪些协议事实？ | 无密钥接口核对表和 provider 链路图 |
| [[09 - 提示词上下文与项目信任]] | 项目资源如何进入 prompt，trust 管哪一层？ | 资源发现/决策/加载流程表 |
| [[10 - Session 日志与分支]] | JSONL、`parent_id` 与当前末端 entry 如何恢复不同历史？ | 两分支 Session 树和投影结果 |
| [[11 - CodingSession 持久化与压缩]] | 事件怎样写盘，取消/压缩后如何恢复？ | 事件到 JSONL 时序、压缩前后对比 |

### 第四段：观察产品界面与扩展【按目标深入】

| 模块 | 要解决的问题 | 本章可检查的产物 |
| --- | --- | --- |
| [[12 - CLI 与 TUI 事件投影]] | 同一事件怎样显示在 print 和 TUI 中？ | 两条入口路径和 renderer 对比 |
| [[13 - Extensions 与自定义工具]] | 如何注册工具/hook，如何处理信任与 reload？ | 只读扩展设计草图和验证记录 |
| [[14 - 最小复刻与最终验收]] | 脱离 Tau 现成实现，能否自己写出可测试的小内核？ | `mini_tau/`、确定性测试、与 Tau 的差异表 |

默认按 00 → 14 顺序学习，不按天数。想先解决**自定义 API / PackyAPI 中转**，至少完成 00–03，再重点读 08；v0.4.5 已有官方自定义 OpenAI 兼容 provider 路径，先验证配置与协议，不预设必须改源码。想先掌握 Agent 内核，完成 00–07 后做模块 14 的**内核入门验收**；想理解完整工程，再完成 08–13 和**完整工程验收**。

## 可选的产品使用练习

完成模块 08 后，按 [同 commit Quickstart](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/quickstart.md) 的「Connect a model → Start a session → Come back later → One-shot mode」依次尝试首次运行、`/login`、`tau -p` 和恢复会话。需要真实模型和账号的部分是选做，不是 00–07 的门槛。模块 09 再选做一次 skill/模板调用与 thinking mode 切换，并记录它们分别改变了什么输入或请求参数。

## 每章都执行同一个六步循环

1. **说清问题**：先读本章摘要，自己用一句话写“上章还做不到什么”。
2. **预测行为**：读测试名与输入，但先遮住断言，写出消息、事件、文件或配置的预期。
3. **运行最小实验**：在 `tau-source` 跑本章定向测试；自己的脚本和临时文件放 `tau-playground`。
4. **追一条源码路径**：只从本章指定入口走到最终结果，记录“谁调用谁、状态归谁、异常在哪里处理”。
5. **增量实现一个小件**：按章节的“同步复刻任务”在 `mini_tau/` 增加最小功能与自己的测试；换一个变量观察失败分支。真实副作用只在自己的练习文件上验证。
6. **留下证据**：写一页学习记录，包含输入、预测、关键源码/测试、实际输出、还没解决的问题；能独立讲清后再进入下一章。

可复用的记录模板：

~~~markdown
### 本章问题
- 为什么需要这一层：
- 我预测的输入/事件/结果：
- 实际运行命令和观察：
- 对应源码函数与测试：
- 失败分支或边界：
- 我能否不用看笔记复述：
~~~

“跑过命令”不等于学会；每章的过关标准以可解释的行为和可复现的验证为准。测试失败时保存原始错误，不为了凑进度跳过它。每章都说明哪些任务只读、哪些会对练习文件产生副作用。

## 学完后应能回答的五个问题

1. 一次含 tool call 的请求为什么会让 provider 调用两次？四条 canonical messages 和运行时事件各是什么？
2. Loop、Harness、CodingSession、CLI/TUI 各拥有什么状态，错误和取消在哪层被处理？
3. 第三方模型接入时，Catalog 选项、持久配置、凭证、运行时适配器、远端 API 形状为何必须分别验证？
4. Session 原始日志、活动分支、模型可见上下文和 UI 显示内容为什么可能不同？
5. 自己的 `mini_tau` 与 Tau 还差哪些工程能力与安全边界？

## 原有源码分析资料怎么用

这套“学习模块”是逐步操作的路线；下列笔记是完整源码论证与文件索引，不要求在第一章就读完：

- 总目录与固定基线：[[Tau Coding Agent 源码分析 MOC]]、[[Tau 源码索引与参考资料]]
- 项目地图与启动：[[源码分析/Tau Coding Agent/01 - 项目定位、技术栈与源码地图]]、[[02 - 三层架构、依赖方向与启动链路]]
- 内核与 provider：[[03 - Agent Harness、Agent Loop 与事件模型]]、[[04 - Provider 适配、消息协议与流式处理]]
- 工具、资源、Session：[[05 - 工具系统、系统提示词与上下文资源]]、[[06 - Session、分支、恢复与上下文压缩]]
- 前端、扩展与边界：[[07 - Extensions、CLI、TUI 与前端边界]]、[[08 - 安全边界、测试体系、局限与设计评价]]

> [!note] 后续修改 Tau 源码
> 学习脚本放独立练习目录。准备真的改 Tau（例如实现新的 provider 适配或改扩展系统）时，再建立独立工作树并写对应测试；固定学习快照继续作为对照证据。
