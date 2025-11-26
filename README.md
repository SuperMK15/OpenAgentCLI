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

Extend `BaseModel` and implement `chat()` and `chat_stream()` methods.
