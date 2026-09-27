#!/usr/bin/env python3
"""Build the Tau source-analysis diagrams from deterministic SVG primitives."""

from __future__ import annotations

from html import escape
from pathlib import Path


OUT = Path(__file__).resolve().parent
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
ACCENT = "#eb6c36"
LINK = "#2e5aa8"
SANS = "'Geist', 'Hiragino Sans', 'Noto Sans CJK SC', sans-serif"
MONO = "'Geist Mono', 'Noto Sans Mono CJK SC', monospace"


def wrap(slug: str, title: str, kind: str, desc: str, width: int, height: int, body: str) -> str:
    min_width = 900 if width >= 1200 else 760
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--accent:{ACCENT}}}
    body{{font-family:{SANS};background:var(--paper);color:var(--ink);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:3rem 2rem}}
    .frame{{max-width:{width}px;width:100%}} .diagram{{overflow-x:auto}}
    .eyebrow{{font-family:{MONO};font-size:.66rem;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem}}
    h1{{font-family:'Instrument Serif',serif;font-size:clamp(1.5rem,2.4vw + .75rem,2rem);font-weight:400;letter-spacing:-.02em;line-height:1.15;margin-bottom:1.5rem}}
    svg{{width:100%;min-width:{min_width}px;display:block}}
  </style>
</head>
<body><main class="frame"><p class="eyebrow">{escape(kind)} · Diagram Design</p><h1>{escape(title)}</h1><div class="diagram">
<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
  <title id="{slug}-title">{escape(title)}</title>
  <desc id="{slug}-desc">{escape(desc)}</desc>
  <defs>
    <marker id="{slug}-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{MUTED}"/></marker>
    <marker id="{slug}-arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{ACCENT}"/></marker>
    <marker id="{slug}-arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{LINK}"/></marker>
    <marker id="{slug}-arrow-open" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polyline points="0 0,8 3,0 6" fill="none" stroke="{MUTED}" stroke-width="1.2"/></marker>
  </defs>
  <rect width="100%" height="100%" fill="{PAPER}"/>
{body}
</svg></div></main></body></html>
"""


def marker(slug: str, style: str) -> str:
    return f"url(#{slug}-arrow-{style})" if style in {"accent", "link", "open"} else f"url(#{slug}-arrow)"


def edge(slug: str, d: str, *, style: str = "muted", dashed: bool = False, width: float = 1.2) -> str:
    color = {"muted": MUTED, "accent": ACCENT, "link": LINK, "open": MUTED}[style]
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    return f'  <path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash} marker-end="{marker(slug, style)}"/>'


def straight(slug: str, x1: int, y1: int, x2: int, y2: int, *, style: str = "muted", dashed: bool = False, width: float = 1.2) -> str:
    return edge(slug, f"M {x1},{y1} L {x2},{y2}", style=style, dashed=dashed, width=width)


def edge_label(x: int, y: int, text: str, *, color: str = MUTED, width: int | None = None) -> str:
    w = width or max(40, ((len(text) + 3) // 4) * 16)
    w = ((w + 3) // 4) * 4
    return (
        f'  <rect x="{x - w // 2}" y="{y - 12}" width="{w}" height="12" rx="2" fill="{PAPER}"/>'
        f'\n  <text x="{x}" y="{y - 4}" fill="{color}" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing=".06em">{escape(text)}</text>'
    )


def zone(x: int, y: int, w: int, h: int, label: str) -> str:
    label_w = ((len(label) * 8 + 20 + 3) // 4) * 4
    return (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="rgba(45,49,66,.02)" stroke="rgba(45,49,66,.10)" stroke-width=".8"/>'
        f'\n  <rect x="{x + 12}" y="{y + 4}" width="{label_w}" height="12" rx="2" fill="{PAPER}"/>'
        f'\n  <text x="{x + 12 + label_w // 2}" y="{y + 12}" fill="rgba(45,49,66,.48)" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing=".14em">{escape(label.upper())}</text>'
    )


def box(x: int, y: int, w: int, h: int, title: str, sub: str = "", *, tag: str = "STEP", kind: str = "backend") -> str:
    styles = {
        "backend": ("#ffffff", INK, INK),
        "focal": ("rgba(235,108,54,.08)", ACCENT, ACCENT),
        "store": ("rgba(45,49,66,.05)", MUTED, MUTED),
        "external": ("rgba(45,49,66,.03)", "rgba(45,49,66,.30)", SOFT),
        "input": ("rgba(79,93,117,.10)", SOFT, SOFT),
        "optional": ("rgba(45,49,66,.02)", "rgba(45,49,66,.22)", SOFT),
    }
    fill, stroke, tag_color = styles[kind]
    title_lines = title.split("\n")
    title_y = y + 32 if len(title_lines) == 1 else y + 28
    title_svg = []
    for i, line in enumerate(title_lines):
        title_svg.append(f'<tspan x="{x + w // 2}" dy="{0 if i == 0 else 16}">{escape(line)}</tspan>')
    sub_y = y + h - 12
    dash = ' stroke-dasharray="4,3"' if kind == "optional" else ""
    return (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PAPER}"/>'
        f'\n  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"{dash}/>'
        f'\n  <rect x="{x + 8}" y="{y + 8}" width="40" height="12" rx="2" fill="transparent" stroke="{tag_color}" stroke-opacity=".45" stroke-width=".8"/>'
        f'\n  <text x="{x + 28}" y="{y + 17}" fill="{tag_color}" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing=".08em">{escape(tag)}</text>'
        f'\n  <text x="{x + w // 2}" y="{title_y}" fill="{INK}" font-size="12" font-weight="600" font-family="{SANS}" text-anchor="middle">{"".join(title_svg)}</text>'
        + (f'\n  <text x="{x + w // 2}" y="{sub_y}" fill="{MUTED}" font-size="9" font-family="{MONO}" text-anchor="middle">{escape(sub)}</text>' if sub else "")
    )


def oval(x: int, y: int, w: int, h: int, title: str, *, focal: bool = False) -> str:
    stroke = ACCENT if focal else INK
    fill = "rgba(235,108,54,.08)" if focal else "#ffffff"
    return (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h // 2}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
        f'\n  <text x="{x + w // 2}" y="{y + h // 2 + 4}" fill="{INK}" font-size="12" font-weight="600" font-family="{SANS}" text-anchor="middle">{escape(title)}</text>'
    )


def diamond(cx: int, cy: int, w: int, h: int, title: str, *, focal: bool = False) -> str:
    stroke = ACCENT if focal else INK
    fill = "rgba(235,108,54,.08)" if focal else "#ffffff"
    points = f"{cx},{cy-h//2} {cx+w//2},{cy} {cx},{cy+h//2} {cx-w//2},{cy}"
    return (
        f'  <polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
        f'\n  <text x="{cx}" y="{cy + 4}" fill="{INK}" font-size="12" font-weight="600" font-family="{SANS}" text-anchor="middle">{escape(title)}</text>'
    )


def legend(y: int, width: int, items: list[tuple[str, str]]) -> str:
    out = [f'  <line x1="40" y1="{y}" x2="{width - 40}" y2="{y}" stroke="rgba(45,49,66,.12)" stroke-width=".8"/>',
           f'  <text x="40" y="{y + 20}" fill="{MUTED}" font-size="8" font-family="{MONO}" letter-spacing=".18em">LEGEND</text>']
    x = 140
    for label, kind in items:
        if kind == "focal":
            out.append(f'  <rect x="{x}" y="{y + 12}" width="16" height="12" rx="2" fill="rgba(235,108,54,.08)" stroke="{ACCENT}"/>')
        elif kind == "dashed":
            out.append(f'  <line x1="{x}" y1="{y + 20}" x2="{x + 28}" y2="{y + 20}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="5,4"/>')
        elif kind == "link":
            out.append(f'  <line x1="{x}" y1="{y + 20}" x2="{x + 28}" y2="{y + 20}" stroke="{LINK}" stroke-width="1.2"/>')
        else:
            out.append(f'  <rect x="{x}" y="{y + 12}" width="16" height="12" rx="2" fill="#ffffff" stroke="{INK}"/>')
        offset = 36 if kind in {"dashed", "link"} else 24
        out.append(f'  <text x="{x + offset}" y="{y + 22}" fill="{MUTED}" font-size="9" font-family="{SANS}">{escape(label)}</text>')
        x += max(132, len(label) * 14 + 48)
    return "\n".join(out)


def core_architecture() -> str:
    s = "tau-core-architecture"
    parts = [zone(176, 88, 416, 448, "tau_coding · application"), zone(608, 88, 304, 448, "tau_agent · core"), zone(928, 88, 304, 448, "adapters")]
    parts += [
        straight(s, 160, 292, 208, 292, style="link"),
        straight(s, 352, 292, 400, 292, style="accent", width=1.4),
        straight(s, 560, 292, 640, 292),
        straight(s, 760, 292, 784, 292),
        edge(s, "M 928,280 H 1072 Q 1080,280 1080,272 V 224"),
        edge(s, "M 928,304 H 1072 Q 1080,304 1080,312 V 360"),
        edge(s, "M 856,324 V 372 Q 856,380 848,380 H 544 Q 536,380 536,372 V 324", dashed=True),
        edge(s, "M 504,324 V 432 Q 504,440 496,440", style="accent"),
        edge(s, "M 432,324 V 400 Q 432,408 424,408 H 296 Q 288,408 288,416 V 440"),
        edge_label(696, 368, "AGENT EVENTS"),
        box(40, 260, 120, 64, "用户", "prompt", tag="IN", kind="input"),
        box(208, 260, 144, 64, "CLI / TUI", "Typer · Textual", tag="HOST"),
        box(400, 260, 160, 64, "CodingSession", "策略 · 资源 · 持久化", tag="APP", kind="focal"),
        box(640, 260, 120, 64, "AgentHarness", "状态 · 队列 · 取消", tag="CORE"),
        box(784, 260, 144, 64, "Agent Loop", "模型 ↔ 工具", tag="LOOP"),
        box(1000, 160, 160, 64, "Provider Layer", "Protocol + tau_ai", tag="AI", kind="external"),
        box(1000, 360, 160, 64, "Coding Tools", "read · write · edit · bash", tag="TOOL", kind="backend"),
        box(400, 440, 192, 64, "Frontend Projection", "text · JSON · transcript", tag="VIEW"),
        box(208, 440, 160, 64, "Session Log", "append-only JSONL tree", tag="DATA", kind="store"),
        legend(656, 1280, [("应用组合根", "focal"), ("核心协议", "normal"), ("事件回流", "dashed"), ("外部适配", "link")]),
    ]
    return wrap(s, "Tau Coding Agent 核心架构", "Architecture", "Tau 从用户输入经过 CodingSession、Harness 和 Agent Loop，再连接模型、工具、前端投影与追加式会话日志。", 1280, 720, "\n".join(parts))


def package_dependencies() -> str:
    s = "tau-package-dependencies"
    parts = [
        edge(s, "M 440,144 V 200 Q 440,208 432,208 H 168 Q 160,208 160,216 V 280"),
        straight(s, 480, 144, 480, 280, style="accent", width=1.4),
        straight(s, 240, 312, 360, 312),
        straight(s, 600, 312, 680, 312, dashed=True),
        edge_label(640, 300, "OWNS PROTOCOL", width=112),
        box(360, 80, 240, 64, "tau_coding", "CLI · Session · tools · TUI", tag="APP"),
        box(80, 280, 160, 64, "tau_ai", "Provider implementations", tag="ADAPT", kind="external"),
        box(360, 280, 240, 64, "tau_agent", "messages · loop · harness", tag="CORE", kind="focal"),
        box(680, 280, 200, 64, "依赖倒置边界", "ModelProvider Protocol", tag="PORT", kind="optional"),
        legend(536, 960, [("应用层", "normal"), ("核心层", "focal"), ("抽象边界", "dashed")]),
    ]
    return wrap(s, "Tau 三层真实依赖关系", "Architecture", "tau_coding 组合应用和适配器，tau_ai 实现由 tau_agent 拥有的 ModelProvider 协议。", 960, 600, "\n".join(parts))


def actor(cx: int, title: str, sub: str, *, focal: bool = False) -> str:
    return box(cx - 80, 80, 160, 56, title, sub, tag="ACT", kind="focal" if focal else "backend")


def lifeline(cx: int, bottom: int = 632) -> str:
    return f'  <line x1="{cx}" y1="136" x2="{cx}" y2="{bottom}" stroke="rgba(45,49,66,.22)" stroke-width="1" stroke-dasharray="4,4"/>'


def message(s: str, x1: int, x2: int, y: int, label: str, *, style: str = "muted", dashed: bool = False) -> str:
    direction = 1 if x2 > x1 else -1
    start = x1 + 8 * direction
    end = x2 - 8 * direction
    label_x = (x1 + x2) // 2
    return straight(s, start, y, end, y, style=style, dashed=dashed) + "\n" + edge_label(label_x, y - 8, label, color=ACCENT if style == "accent" else MUTED)


def print_sequence() -> str:
    s = "tau-print-startup-sequence"
    xs = [120, 380, 640, 900, 1160]
    parts = [lifeline(x) for x in xs]
    parts += [
        message(s, 120, 380, 176, 'tau --print "prompt"', style="link"),
        message(s, 380, 640, 224, "ProviderConfig"),
        message(s, 640, 380, 272, "concrete provider", dashed=True),
        message(s, 380, 900, 320, "load / create session"),
        message(s, 900, 1160, 368, "construct Harness + Loop"),
        message(s, 900, 1160, 416, "prompt + tools + messages", style="accent"),
        edge(s, "M 1168,456 H 1216 Q 1224,456 1224,464 V 488 Q 1224,496 1216,496 H 1168"),
        edge_label(1192, 452, "MODEL ↔ TOOLS", width=112),
        message(s, 1160, 900, 528, "AgentEvent stream", dashed=True),
        message(s, 900, 380, 576, "persisted events", dashed=True),
        message(s, 380, 120, 624, "text / JSON / transcript", style="accent"),
        actor(120, "User", "terminal"), actor(380, "CLI / Print Host", "main + render mode"),
        actor(640, "Provider Factory", "runtime adapter"), actor(900, "CodingSession", "resources + persistence", focal=True),
        actor(1160, "Agent Core", "Harness + Loop"),
        legend(660, 1280, [("同步调用", "normal"), ("返回事件", "dashed"), ("关键路径", "focal")]),
    ]
    return wrap(s, "Print Mode 启动与执行链", "Sequence", "用户请求经过 CLI、Provider Factory、CodingSession 和 Agent Core，最终以持久化事件流返回渲染结果。", 1280, 720, "\n".join(parts))


def agent_loop_flow() -> str:
    s = "tau-agent-loop-flow"
    parts = [
        straight(s, 640, 80, 640, 104), straight(s, 640, 160, 640, 192), straight(s, 640, 256, 640, 272),
        straight(s, 640, 368, 640, 384), straight(s, 752, 432, 880, 432, style="accent"),
        edge(s, "M 1120,436 H 1144 Q 1152,436 1152,428 V 232 Q 1152,224 1144,224 H 780"),
        edge(s, "M 528,432 H 368 Q 360,432 360,440 V 492"),
        edge(s, "M 248,540 H 168 Q 160,540 160,532 V 140 Q 160,132 168,132 H 520"),
        edge(s, "M 360,588 V 616 Q 360,624 368,624 H 520"),
        edge(s, "M 752,320 H 1168 Q 1176,320 1176,328 V 616 Q 1176,624 1168,624 H 760"),
        edge_label(804, 420, "YES", color=ACCENT, width=40), edge_label(496, 420, "NO", width=40),
        edge_label(672, 380, "NO", width=40), edge_label(1080, 308, "YES", width=40),
        edge_label(204, 528, "YES", width=40), edge_label(400, 612, "NO", width=40),
        oval(520, 32, 240, 48, "AgentStart + TurnStart"),
        box(520, 104, 240, 56, "写入输入队列", "prompt / steering", tag="QUEUE"),
        box(500, 192, 280, 64, "流式响应并组装消息", "provider → AssistantMessage", tag="MODEL", kind="focal"),
        diamond(640, 320, 224, 96, "error / aborted?"),
        diamond(640, 432, 224, 96, "有 tool_calls?", focal=True),
        box(880, 404, 240, 64, "顺序执行工具", "result + steering queue", tag="TOOLS"),
        diamond(360, 540, 224, 96, "有 follow-up?"),
        oval(520, 600, 240, 48, "TurnEnd + AgentEnd"),
        legend(664, 1280, [("模型响应", "focal"), ("普通步骤", "normal"), ("循环回路", "dashed")]),
    ]
    return wrap(s, "run_agent_loop 控制流", "Flowchart", "Agent Loop 处理输入、模型流、错误、工具调用、steering 与 follow-up，直到本轮结束。", 1280, 720, "\n".join(parts))


def provider_pipeline() -> str:
    s = "tau-provider-event-pipeline"
    xs = [40, 192, 344, 496, 648, 800, 952, 1104]
    parts = []
    for i in range(7):
        parts.append(straight(s, xs[i] + 120, 308, xs[i + 1], 308, style="accent" if i == 3 else "muted"))
    nodes = [
        ("HTTP SSE", "provider chunks", "WIRE", "external"),
        ("协议解析器", "provider-specific", "PARSE", "backend"),
        ("Provider Events", "text · thinking · tool", "EVENT", "backend"),
        ("tau_ai.stream", "canonicalize stream", "NORM", "focal"),
        ("Assistant Events", "block start/delta/end", "AI", "focal"),
        ("Agent Adapter", "_assistant_events", "LOOP", "backend"),
        ("Agent Events", "message lifecycle", "EVENT", "backend"),
        ("Frontend", "session · renderer · TUI", "VIEW", "external"),
    ]
    for x, (title, sub, tag, kind) in zip(xs, nodes):
        parts.append(box(x, 260, 120, 96, title, sub, tag=tag, kind=kind))
    parts.append(legend(656, 1280, [("供应商边界", "normal"), ("Canonical 转换", "focal"), ("消费端", "link")]))
    return wrap(s, "Provider 流的双阶段规范化", "Architecture", "供应商 SSE 先转换为统一 Assistant 事件，再提升为 Agent 消息生命周期事件供 Session 和前端消费。", 1280, 720, "\n".join(parts))


def session_tree() -> str:
    s = "tau-session-branch-tree"
    parts = [
        straight(s, 480, 88, 480, 140), straight(s, 480, 188, 480, 240),
        edge(s, "M 480,288 V 320 Q 480,328 472,328 H 288 Q 280,328 280,336 V 360"),
        edge(s, "M 480,288 V 320 Q 480,328 488,328 H 672 Q 680,328 680,336 V 360", style="accent"),
        straight(s, 680, 408, 680, 460, style="accent"),
        box(400, 40, 160, 48, "root: user prompt", tag="ROOT", kind="input"),
        box(400, 140, 160, 48, "assistant", tag="MSG"),
        box(400, 240, 160, 48, "tool result", tag="MSG", kind="focal"),
        box(200, 360, 160, 48, "原分支继续", tag="LEAF", kind="optional"),
        box(600, 360, 160, 48, "回到 C 后的新 prompt", tag="BRANCH", kind="focal"),
        box(600, 460, 160, 48, "新分支 assistant", tag="LEAF"),
        legend(536, 960, [("活动分支", "focal"), ("保留历史", "dashed"), ("消息节点", "normal")]),
    ]
    return wrap(s, "Append-only Session 分支树", "Tree", "会话从 tool result 节点分叉，原分支保留，新 prompt 形成新的活动叶节点。", 960, 600, "\n".join(parts))


def frontend_projection() -> str:
    s = "tau-frontend-event-projection"
    parts = [zone(504, 80, 224, 320, "print renderers")]
    parts += [
        straight(s, 200, 296, 248, 296, style="accent"),
        edge(s, "M 424,248 H 448 Q 456,248 456,240 V 148 Q 456,140 464,140 H 536"),
        edge(s, "M 424,272 H 464 Q 472,272 472,264 V 248 Q 472,240 480,240 H 536"),
        edge(s, "M 424,296 H 480 Q 488,296 488,304 V 348 Q 488,356 496,356 H 536"),
        edge(s, "M 424,320 H 488 Q 496,320 496,328 V 488 Q 496,496 504,496", style="accent"),
        straight(s, 704, 496, 752, 496, style="accent"),
        straight(s, 952, 496, 1000, 496, style="accent"),
        box(40, 260, 160, 72, "CodingSession", "canonical AgentEvent", tag="SOURCE"),
        box(248, 224, 176, 144, "AgentEvent stream", "single frontend contract", tag="EVENT", kind="focal"),
        box(536, 120, 160, 56, "Final Text", "human output", tag="TEXT"),
        box(536, 220, 160, 56, "NDJSON", "automation stream", tag="JSON"),
        box(536, 320, 160, 56, "Transcript", "readable process", tag="LOG"),
        box(504, 464, 200, 64, "TUI Adapter", "events → display state", tag="ADAPT", kind="focal"),
        box(752, 464, 200, 64, "TuiState", "ChatItem projection", tag="STATE", kind="store"),
        box(1000, 464, 200, 64, "Textual App", "widgets · modals · paging", tag="VIEW"),
        legend(656, 1280, [("Canonical 事件", "focal"), ("Print 投影", "normal"), ("TUI 投影", "link")]),
    ]
    return wrap(s, "AgentEvent 到多前端投影", "Architecture", "同一 CodingSession 事件流分别投影为文本、NDJSON、Transcript 与 Textual TUI 状态。", 1280, 720, "\n".join(parts))


def extension_sequence() -> str:
    s = "tau-extension-lifecycle"
    xs = [160, 480, 800, 1120]
    parts = [lifeline(x) for x in xs]
    parts += [
        message(s, 160, 480, 184, "discover + load paths"),
        message(s, 480, 800, 240, "import + setup(api)", style="link"),
        message(s, 800, 1120, 296, "register tools / hooks / UI", style="accent"),
        message(s, 1120, 160, 368, "bind session + commands", dashed=True),
        message(s, 160, 1120, 432, "dispatch lifecycle / input / tool"),
        message(s, 160, 1120, 496, "reload / dispose"),
        message(s, 1120, 800, 560, "cleanup callbacks", dashed=True),
        actor(160, "CodingSession / Host", "application lifecycle"),
        actor(480, "Extension Loader", "import isolation"),
        actor(800, "setup(tau)", "extension entrypoint"),
        actor(1120, "ExtensionRuntime", "registry + hook dispatch", focal=True),
        legend(660, 1280, [("注册关键路径", "focal"), ("生命周期调用", "normal"), ("回调 / 返回", "dashed")]),
    ]
    return wrap(s, "Extension 装载与运行时生命周期", "Sequence", "Host 发现扩展并调用 setup，ExtensionRuntime 收集注册、绑定 Session、分发事件并在 reload 时清理旧回调。", 1280, 720, "\n".join(parts))


DIAGRAMS = {
    "tau-core-architecture.html": core_architecture,
    "tau-package-dependencies.html": package_dependencies,
    "tau-print-startup-sequence.html": print_sequence,
    "tau-agent-loop-flow.html": agent_loop_flow,
    "tau-provider-event-pipeline.html": provider_pipeline,
    "tau-session-branch-tree.html": session_tree,
    "tau-frontend-event-projection.html": frontend_projection,
    "tau-extension-lifecycle.html": extension_sequence,
}


def main() -> None:
    for name, builder in DIAGRAMS.items():
        target = OUT / name
        target.write_text(builder(), encoding="utf-8")
        print(target)


if __name__ == "__main__":
    main()
