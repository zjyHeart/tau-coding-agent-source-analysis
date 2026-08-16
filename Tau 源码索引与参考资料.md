---
tags:
  - Agent/Coding-Agent
  - 源码分析/Tau
aliases:
  - Tau 源码索引
  - Tau 参考资料
source_type: source-index
status: complete
---

# Tau 源码索引与参考资料

## 证据基线

- 分析时间：2026-08-16 至 2026-08-17（Asia/Shanghai）。
- 固定 commit：[`15f77f77acfb20608c3a86638aabf59bd614755d`](https://github.com/huggingface/tau/tree/15f77f77acfb20608c3a86638aabf59bd614755d)。
- release：[`v0.3.10`](https://github.com/huggingface/tau/releases/tag/v0.3.10)。
- Python package version：`0.3.10`。
- 在线统计只代表 2026-08-16 查询快照：2340 stars、279 forks、83 open issues。

## 源码入口索引

### 项目与架构

| 主题 | 文件 |
|---|---|
| package、依赖、CLI entry | [`pyproject.toml`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/pyproject.toml) |
| 项目定位与三层说明 | [`README.md`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/README.md) |
| 贡献边界与测试原则 | [`CONTRIBUTING.md`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/CONTRIBUTING.md) |
| CI | [`.github/workflows/ci.yml`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/.github/workflows/ci.yml) |

### `tau_agent`

| 主题 | 文件/定位 |
|---|---|
| Harness 状态与队列 | [`harness.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/harness.py) |
| Agent loop | [`loop.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/loop.py) |
| AgentEvent | [`events.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/events.py) |
| Canonical messages | [`messages.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/messages.py) |
| Provider Protocol | [`provider.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/provider.py) |
| Tool contract | [`tools.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/tools.py) |
| Tool history repair | [`tool_history.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/tool_history.py) |
| Session entries | [`session/entries.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/session/entries.py) |
| State projection/compaction | [`session/memory.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/session/memory.py) |
| JSONL storage/migration | [`session/storage.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/session/storage.py)、[`session/jsonl.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/session/jsonl.py) |
| Tree traversal | [`session/tree.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_agent/session/tree.py) |

### `tau_ai`

| 主题 | 文件 |
|---|---|
| Provider parser → assistant stream | [`stream.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/stream.py) |
| OpenAI compatible | [`openai_compatible.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/openai_compatible.py) |
| OpenAI Codex | [`openai_codex.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/openai_codex.py) |
| Anthropic | [`anthropic.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/anthropic.py) |
| Google | [`google.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/google.py) |
| Mistral | [`mistral.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/mistral.py) |
| Retry/HTTP errors | [`retry.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/retry.py)、[`http_errors.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_ai/http_errors.py) |

### `tau_coding`

| 主题 | 文件 |
|---|---|
| CLI 与 print/TUI 路由 | [`cli.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/cli.py) |
| 应用层 Session facade | [`session.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/session.py) |
| Provider runtime factory | [`provider_runtime.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/provider_runtime.py) |
| Provider config/catalog | [`provider_config.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/provider_config.py)、[`data/catalog.toml`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/data/catalog.toml) |
| 内置 coding tools | [`tools.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/tools.py) |
| System prompt | [`system_prompt.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/system_prompt.py) |
| Project context/resources | [`context.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/context.py)、[`resources.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/resources.py) |
| Skills/prompts | [`skills.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/skills.py)、[`prompt_templates.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/prompt_templates.py) |
| Slash commands | [`commands.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/commands.py) |
| Project trust | [`project_trust.py`](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/project_trust.py) |
| Extension API/loader/runtime | [`extensions/`](https://github.com/huggingface/tau/tree/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/extensions) |
| TUI adapter/state/app | [`tui/`](https://github.com/huggingface/tau/tree/15f77f77acfb20608c3a86638aabf59bd614755d/src/tau_coding/tui) |

## 官方资料

### 当前说明

- [Tau README](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/README.md)
- [官方文档首页](https://twotimespi.dev/)
- [Architecture](https://twotimespi.dev/internals/architecture/)
- [Agent loop & events](https://twotimespi.dev/internals/agent-loop/)
- [Custom frontend](https://twotimespi.dev/internals/custom-frontend/)
- [Providers and models](https://twotimespi.dev/guides/providers-and-models/)
- [Sessions](https://twotimespi.dev/guides/sessions/)
- [Extensions](https://twotimespi.dev/guides/extensions/)
- [Project trust](https://twotimespi.dev/guides/project-trust/)
- [TUI](https://twotimespi.dev/guides/tui/)
- [CLI reference](https://twotimespi.dev/reference/cli/)
- [Tools reference](https://twotimespi.dev/reference/tools/)

### 演进资料

- [Roadmap issue #1](https://github.com/huggingface/tau/issues/1)：用于理解阶段目标；其 Extensions checklist 已滞后于当前实现。
- [Releases](https://github.com/huggingface/tau/releases)：用于核对最近行为变化。
- [`dev-notes/`](https://github.com/huggingface/tau/tree/15f77f77acfb20608c3a86638aabf59bd614755d/dev-notes)：设计与实现日志。
- [Textual ADR](https://github.com/huggingface/tau/blob/15f77f77acfb20608c3a86638aabf59bd614755d/dev-notes/adr/0001-use-textual-for-tui.md)。

## 外部参照

- [Pi repository](https://github.com/earendil-works/pi)：当前包结构包含 `packages/ai`、`agent`、`coding-agent`、`tui` 等；Tau 借鉴的是架构形状，不是功能完全等价声明。
- [[Clippings/Bilibili/Tau：学习 Agent 架构]]：库内视频整理，只作为二级材料。

## 本地验证记录

```bash
git rev-parse HEAD
# 15f77f77acfb20608c3a86638aabf59bd614755d

uv run pytest -q
# 1513 passed, 2 skipped in 94.44s
```

未把 Ruff、format、mypy 和 Hugo 在本地重复执行；它们是仓库 CI 的门禁，但本次只实际运行 pytest。不要把“CI 配置包含”表述为“本地已运行”。

## 资料可信度说明

1. 固定 commit 源码与实际测试优先级最高；
2. 官网/README 用于理解作者意图，但遇到冲突以固定源码为准；
3. Roadmap/Release 有时间性；
4. GitHub stars/issues 会变化；
5. 本分析没有给 Tau 的 coding 成功率打分，因为仓库没有提供可复核 benchmark 结果。

## 导航

- 总览：[[Tau Coding Agent 源码分析 MOC]]
- 评价：[[08 - 安全边界、测试体系、局限与设计评价]]

