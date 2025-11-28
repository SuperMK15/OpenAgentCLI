from abc import ABC, abstractmethod
from typing import Any
from .types import Message, ToolDefinition, Role

class ProtocolAdapter(ABC):
    # Role string mappings - override in subclass if provider uses different strings
    ROLE_USER: str = "user"
    ROLE_ASSISTANT: str = "assistant"
    ROLE_TOOL: str = "tool"
    ROLE_SYSTEM: str = "system"
    
    def role_to_provider(self, role: Role) -> str:
        """Convert internal Role to provider string"""
        mapping = {
            Role.USER: self.ROLE_USER,
            Role.ASSISTANT: self.ROLE_ASSISTANT,
            Role.TOOL: self.ROLE_TOOL,
            Role.SYSTEM: self.ROLE_SYSTEM
        }
        return mapping[role]
    
    @abstractmethod
    def to_provider_messages(self, messages: list[Message]) -> Any:
        """Convert internal messages to provider format"""
        pass
    
    @abstractmethod
    def from_provider_response(self, response: Any) -> Message:
        """Convert provider response to internal format"""
        pass
    
    @abstractmethod
    def to_provider_tools(self, tools: list[ToolDefinition]) -> Any:
        """Convert internal tools to provider format"""
        pass
    
    @abstractmethod
    def to_tool_result(self, tool_call_id: str, result: dict) -> Any:
        """Convert tool result to provider format"""
        pass
