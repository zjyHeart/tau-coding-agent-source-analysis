---
title: "Tau 学习模块 08 - Provider 适配与自定义 API"
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
  - 学习模块
source_commit: "c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3"
status: ready
---

# 08 - Provider 适配与自定义 API

> [!summary] 本章解决什么
> v0.4.5 已提供 `/login custom`、`tau setup` 和用户级 `catalog.toml`。先用官方路径理解并配置 OpenAI 兼容 provider，再分清“配置保存成功”和“PackyAPI 协议真正兼容”；只有现成适配器不支持的协议才进入源码修改。

**官方概念参考**：[Providers and models](https://twotimespi.dev/concepts/#providers-and-models) 与 [Providers guide](https://twotimespi.dev/guides/providers-and-models/)。这页说明当前 Tau 的概念；本章具体代码行为仍以 `c66fb879` 源码和测试为准。

**本章定向阅读（同 commit 官方文档）**：[源文件](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/guides/providers-and-models.md) 的「Adding a custom / local provider」。读完先回答：①/login custom、setup 与 catalog.toml 分别做什么？ ②PackyAPI 的 endpoint 与模型 ID 还需核对什么？

## 前置与产物

- 前置：[[07 - Coding 工具与安全边界]]；如果只想研究自定义 API，可先完成 [[03 - 工具定义与调用闭环]] 后跳到本章。
- 源码：`src/tau_agent/provider.py`、`src/tau_ai/fake.py`、`src/tau_ai/openai_compatible.py`、`src/tau_ai/stream.py`、`src/tau_coding/cli.py::setup_command()`、`tui/app.py` 的自定义登录流程、`provider_config.py`、`provider_catalog.py`、`catalog_loader.py`、`provider_runtime.py`。
- 产物：一张“配置 → 凭证 → 请求 payload → 流事件 → canonical assistant”的链路图，以及一份不含密钥的中转接口核对表。

## 步骤 1：先认清 provider 协议

读 `ModelProvider.stream_response()` 与 `FakeProvider.stream_response()`：输入是 model/system/messages/tools，输出是 assistant stream events。把 `FakeProvider` 看成测试替身，不是 Tau 对自定义 API 的配置入口。运行 `tests/test_tau_ai.py::test_fake_provider_replays_scripted_events`。

## 步骤 2：分开看“可选项”和“运行对象”

读 `provider_catalog.py` 的目录条目、`catalog_loader.py` 的内置/用户目录合并、`provider_config.py` 的 `OpenAICompatibleProviderConfig` 和 `ProviderSettings`，再看 `provider_runtime.py::create_model_provider()`。依次追三条**已实现**的入口：TUI 内 `/login custom` 提示输入并保存 provider；CLI `tau --provider ... --base-url ... --api-key-env ... --model ... setup`；手写用户级 `~/.tau/catalog.toml`。后者只保存 provider/模型元数据，请求 headers、timeout、retry 属于 `~/.tau/providers.json`。对照 `tests/test_cli.py::test_setup_command_writes_provider_settings` 与 `tests/test_provider_catalog.py::test_user_catalog_adds_new_provider`。

## 步骤 3：只研究一个适配器

先读 `src/tau_ai/openai_compatible.py` 的请求构造和流解析，不必同时深入 Anthropic、Google、Mistral。运行 `tests/test_tau_ai.py::test_openai_compatible_provider_formats_request_and_streams_text` 与 `test_openai_compatible_provider_streams_tool_calls`。记下 messages、tools、model、base URL、鉴权头怎样进入请求，以及增量 tool-call 如何成为最终 `AssistantMessage`。重点区分 HTTP 连通与消息/工具协议兼容。

## 步骤 4：为 PackyAPI 填“核对表”，暂不猜值

| 要核对 | 从哪里获得 | 在 Tau 中对应 |
| --- | --- | --- |
| 实际支持的 API 形状（如 Chat Completions 或其他） | PackyAPI 文档及本地测试 | `api` 与适配器选择；`/login custom` 面向 OpenAI 兼容端点 |
| base URL 是否已包含版本路径 | PackyAPI 文档 | `base_url` |
| 鉴权头/环境变量名 | PackyAPI 文档 | `api_key_env`、credential 配置 |
| 可用模型的精确 ID、工具调用/流式支持 | 中转平台文档及返回样例 | `models`、`default_model`、能力元数据 |

先以占位值练习命令形状，**不要直接执行下面的占位命令**：

```bash
rtk tau --provider packyapi --base-url '<按 PackyAPI 文档确认的 URL>' --api-key-env PACKYAPI_API_KEY --model '<精确模型 ID>' setup
rtk tau providers
```

或者在 Tau TUI 输入 `/login custom`，按界面逐项填写；若希望版本可控，可参考同 commit [官方配置示例](https://github.com/huggingface/tau/blob/c66fb879c1058f7b3d8514fb7f92c919d3c3e3b3/website/content/guides/providers-and-models.md) 手写用户级 `catalog.toml`。不要把 API Key 写入笔记或源码。即便普通聊天成功，也要分别验证工具调用、流式结束、错误响应和重试；若协议与 `OpenAICompatibleProvider` 不匹配，才考虑在适配层做有测试的改动。

## 步骤 5：验证配置与协议边界

~~~bash
rtk uv run pytest tests/test_provider_catalog.py tests/test_provider_config.py tests/test_provider_runtime.py -q
rtk uv run pytest tests/test_tau_ai.py -q
rtk uv run pytest tests/test_cli.py::test_setup_command_writes_provider_settings -q
~~~

如果后续真的需要支持新协议，先在独立工作树里增加“配置读写 → runtime 选择 → mock HTTP 请求/事件”测试，再考虑用真实中转端到端验证。不要在固定 `c66fb879` 学习快照里直接混入未验证实现。

## 完成检查

能说清 provider catalog、持久配置、credential、runtime adapter 四者各负责什么；会区分 `/login custom`、`setup`、`catalog.toml` 三条入口；面对 PackyAPI 的具体 URL 和模型 ID，能指出还缺什么证据才能判断兼容。深入资料：[[04 - Provider 适配、消息协议与流式处理]]。

## 同步复刻任务（自己的学习版）

定义 `mini_tau/provider_config.py` 的配置数据结构（base URL、API 形状、模型 ID、凭证环境变量名），写校验测试；再用 mock HTTP 响应练习解析 text/tool-call。没有中转服务的协议证据时，不发真实 PackyAPI 请求，也不硬编码密钥。

前置：[[07 - Coding 工具与安全边界]]；后续：[[09 - 提示词上下文与项目信任]]。
