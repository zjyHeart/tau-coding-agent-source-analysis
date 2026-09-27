import asyncio

from tau_agent import AgentHarness, AgentHarnessConfig, AgentTool, AgentToolResult
from tau_agent import AssistantMessage, ToolCall
from tau_agent.provider_events import AssistantDoneEvent, AssistantStartEvent, ToolCallEndEvent
from tau_ai import FakeProvider


async def read_demo(tool_call_id, arguments, signal=None, on_update=None):
    return AgentToolResult(content=f"模拟读取：{arguments['path']}")


async def main():
    call = ToolCall(id="call-1", name="read_demo", arguments={"path": "README.md"})
    first = AssistantMessage(content=[call], model="fake", stop_reason="toolUse")
    last = AssistantMessage(content="已读取 README.md", model="fake")
    provider = FakeProvider([
        [AssistantStartEvent(partial=AssistantMessage(model="fake")),
         ToolCallEndEvent(content_index=0, tool_call=call, partial=first),
         AssistantDoneEvent(reason="toolUse", message=first)],
        [AssistantStartEvent(partial=AssistantMessage(model="fake")),
         AssistantDoneEvent(reason="stop", message=last)],
    ])
    tool = AgentTool(
        name="read_demo", label="Read demo", description="Return a fixed sample",
        parameters={"type": "object"}, execute_fn=read_demo,
    )
    harness = AgentHarness(AgentHarnessConfig(
        provider=provider, model="fake", system="You are Tau.", tools=[tool],
    ))
    events = [event.type async for event in harness.prompt("读 README.md")]
    print("events:", " → ".join(events))
    print("history:", [(m.role, getattr(m, "text", "")) for m in harness.messages])
    print("provider_calls:", len(provider.calls))


asyncio.run(main())
