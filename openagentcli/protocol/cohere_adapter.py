import json
from typing import Any
from .adapter import ProtocolAdapter
from .types import Message, ToolCall, ToolDefinition, Role

class CohereAdapter(ProtocolAdapter):   
    def to_provider_messages(self, messages: list[Message]) -> list[dict]:
        """Convert internal messages to Cohere format"""
        cohere_messages = []
        for msg in messages:
            if msg.role == Role.TOOL:
                cohere_messages.append({
                    "role": self.role_to_provider(Role.TOOL),
                    "tool_call_id": msg.tool_call_id,
                    "content": [{"type": "document", "document": {"data": msg.content}}]
                })
            elif msg.role == Role.ASSISTANT and msg.tool_calls:
                cohere_msg = {"role": self.role_to_provider(Role.ASSISTANT)}
                if msg.tool_plan:
                    cohere_msg["tool_plan"] = msg.tool_plan
                cohere_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments)
                        }
                    }
                    for tc in msg.tool_calls
                ]
                cohere_messages.append(cohere_msg)
            else:
                cohere_messages.append({
                    "role": self.role_to_provider(msg.role),
                    "content": msg.content
                })
        return cohere_messages
    
    def from_provider_response(self, response: Any) -> Message:
        """Convert Cohere response to internal format"""
        msg = response.message
        
        if msg.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                for tc in msg.tool_calls
            ]
            return Message(
                role=Role.ASSISTANT,
                tool_calls=tool_calls,
                tool_plan=msg.tool_plan if hasattr(msg, 'tool_plan') else None
            )
        
        content = msg.content[0].text if msg.content else None
        return Message(role=Role.ASSISTANT, content=content)
    
    def to_provider_tools(self, tools: list[ToolDefinition]) -> list[dict]:
        """Convert internal tools to Cohere format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in tools
        ]
    
    def to_tool_result(self, tool_call_id: str, result: dict) -> Message:
        """Convert tool result to internal format"""
        return Message(
            role=Role.TOOL,
            tool_call_id=tool_call_id,
            content=json.dumps(result)
        )
