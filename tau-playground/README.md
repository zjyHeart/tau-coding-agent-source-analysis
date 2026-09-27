# Tau 学习练习区

这里的代码是学习版，使用旁边 `tau-source/` 的 v0.4.5 环境，不改 Tau 源码。

在 `tau-source/` 目录运行：

```bash
rtk uv run python ../tau-playground/01_messages.py
rtk uv run python ../tau-playground/02_single_turn.py
rtk uv run python ../tau-playground/toy_agent.py
```

三个脚本依次展示四条消息、单轮流式回答、两次 provider 调用的工具闭环。运行不需要 API Key。
