"""模块 01：构造四条 canonical messages，不访问网络或磁盘。"""

from tau_agent import AssistantMessage, ToolCall, ToolResultMessage, UserMessage

call = ToolCall(id="call-1", name="read_demo", arguments={"path": "README.md"})
history = [
    UserMessage(content="读 README.md"),
    AssistantMessage(content=[call], model="fake", stop_reason="toolUse"),
    ToolResultMessage(tool_call_id=call.id, tool_name=call.name, content="模拟读取结果"),
    AssistantMessage(content="README.md 的示例内容", model="fake"),
]

assert [message.role for message in history] == ["user", "assistant", "toolResult", "assistant"]
assert history[1].tool_calls[0].id == history[2].tool_call_id
for index, message in enumerate(history, 1):
    print(f"{index}. {message.role}: {message.text}")
print("call_id_matched: True")
