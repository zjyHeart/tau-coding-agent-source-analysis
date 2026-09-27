"""模块 02：FakeProvider 的单轮文本回答与事件。"""

import asyncio

from tau_agent import AgentHarness, AgentHarnessConfig, AssistantMessage
from tau_agent.provider_events import AssistantDoneEvent, AssistantStartEvent, TextDeltaEvent
from tau_ai import FakeProvider


async def main() -> None:
    answer = AssistantMessage(content="你好", model="fake")
    provider = FakeProvider(
        [[
            AssistantStartEvent(partial=AssistantMessage(model="fake")),
            TextDeltaEvent(content_index=0, delta="你好", partial=answer),
            AssistantDoneEvent(reason="stop", message=answer),
        ]]
    )
    harness = AgentHarness(
        AgentHarnessConfig(provider=provider, model="fake", system="只回答一句话")
    )
    events = [event.type async for event in harness.prompt("Hi")]
    print("events:", " → ".join(events))
    print("history:", [(message.role, message.text) for message in harness.messages])
    print("provider_calls:", len(provider.calls))


if __name__ == "__main__":
    asyncio.run(main())
