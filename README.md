# OpenAgentCLI

A coding agent with MCP server and native tool calling.

## Installation

```bash
pip install -e .
```

## Usage

Set your API key via environment variable:
```bash
export COHERE_API_KEY="your-api-key"
```

Or create a `.env` file at the project root:
```
COHERE_API_KEY=your-api-key
```

Run the CLI:
```bash
openagentcli
```

## Commands

- `/help` - Show available commands
- `/tools` - List all available tools
- `/tools <name>` - Show detailed information for a specific tool
- `/clear` - Clear chat context
- `/quit` - Exit the CLI
- `!<command>` - Execute bash commands directly

## Structure

- `openagentcli/models/` - AI model interfaces (BaseModel, CohereModel)
- `openagentcli/server/` - FastMCP server with coding tools
- `openagentcli/main.py` - Main entry point with native tool calling

## Available Tools

- `read_file(path)` - Read file contents
- `write_file(path, content, command)` - Write to file (create/str_replace/insert/append)
- `list_directory(path, depth)` - List directory contents (depth=0 for current only, depth>0 for recursive)
- `search_files_by_name(pattern, path)` - Search for files by name using regex pattern
- `search_files_by_content(pattern, path)` - Search for files by content using regex pattern
- `shell(command)` - Execute bash commands

## Features

- Native Cohere tool calling (command-a-03-2025)
- Multi-step tool use with automatic reasoning
- Fine-grained citations
- Y/N/T confirmation for mutating operations

## Adding New Models

1. Create a new adapter in `openagentcli/protocol/`:
```python
from openagentcli.protocol import ProtocolAdapter, Message, ToolDefinition

class MyProviderAdapter(ProtocolAdapter):
    # Override role strings if provider uses different names
    ROLE_USER = "user"  # default
    ROLE_ASSISTANT = "assistant"  # default
    ROLE_TOOL = "tool"  # default
    ROLE_SYSTEM = "system"  # default
    
    def to_provider_messages(self, messages: list[Message]) -> Any:
        # Convert internal Message format to provider's format
        pass
    
    def from_provider_response(self, response: Any) -> Message:
        # Convert provider's response to internal Message format
        pass
    
    def to_provider_tools(self, tools: list[ToolDefinition]) -> Any:
        # Convert internal ToolDefinition to provider's format
        pass
    
    def to_tool_result(self, tool_call_id: str, result: dict) -> Message:
        # Convert tool result to internal Message format
        pass
```

2. Create model class extending `BaseModel`:
```python
from openagentcli.models.base import BaseModel
from openagentcli.protocol import Message, ToolDefinition

class MyProviderModel(BaseModel):
    def __init__(self):
        super().__init__(MyProviderAdapter())
        # Initialize your provider's client
    
    def chat(self, messages: list[Message], tools: list[ToolDefinition]) -> Message:
        provider_messages = self.adapter.to_provider_messages(messages)
        provider_tools = self.adapter.to_provider_tools(tools)
        response = self.client.chat(...)  # Call provider API
        return self.adapter.from_provider_response(response)
    
    def chat_stream(self, messages: list[Message], tools: list[ToolDefinition]) -> Message:
        # Implement streaming if supported
        pass
```
