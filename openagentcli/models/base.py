from abc import ABC, abstractmethod
from openagentcli.protocol import Message, ToolDefinition, ProtocolAdapter

class BaseModel(ABC):
    def __init__(self, adapter: ProtocolAdapter):
        self.adapter = adapter
    
    @abstractmethod
    def chat(self, messages: list[Message], tools: list[ToolDefinition]) -> Message:
        pass
    
    @abstractmethod
    def chat_stream(self, messages: list[Message], tools: list[ToolDefinition]) -> Message:
        pass
