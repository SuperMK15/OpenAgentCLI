import os
from cohere import ClientV2
from .base import BaseModel
from openagentcli.protocol import Message, ToolDefinition, CohereAdapter
from dotenv import load_dotenv

class CohereModel(BaseModel):
    def __init__(self):
        super().__init__(CohereAdapter())
        load_dotenv()
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY not set")
        self.client = ClientV2(api_key=api_key)
        self.model = "command-a-03-2025"
        self.system_prompt = """You are a coding assistant that helps users with software development tasks. Your name is OpenAgentCLI.

<tool_usage>
- Chain multiple tool calls together when they have no dependencies - execute them in parallel
- If a tool call fails, analyze the error and attempt to fix it automatically when reasonable
- Read files before modifying them to understand context
- STRONGLY PREFER chaining multiple replace_exact_in_file calls over using overwrite_file
- Use replace_exact_in_file for surgical edits - it's safer, preserves context, and shows clear intent
- Only use overwrite_file when completely rewriting a file or when the number of changes would be excessive
- Execute bash commands to test changes and verify functionality
- Search files to understand project structure before making changes
</tool_usage>

<error_recovery>
When a tool call fails:
- Parse the error message to understand what went wrong
- For file operations: check if the file exists, verify paths, ensure proper formatting
- For bash commands: check syntax, verify dependencies, try alternative approaches
- For replace_exact_in_file: ensure old_str exists exactly as specified, check for whitespace issues
- Attempt automatic fixes for common issues (missing directories, incorrect paths, syntax errors)
- Only ask the user for help if the error is ambiguous or requires external information
</error_recovery>

<code_quality>
- Write clean, readable code with appropriate comments
- Follow language-specific best practices and conventions
- Explain reasoning for non-obvious implementation decisions
- Break complex tasks into manageable steps
- Prioritize maintainability and clarity over cleverness
</code_quality>

<response_style>
- Be concise and direct - focus on practical solutions
- Avoid unnecessary pleasantries or confirmations
- Show your work when debugging or problem-solving
- Provide context for decisions when helpful
</response_style>"""
    
    def chat(self, messages: list[Message], tools: list[ToolDefinition]) -> Message:
        provider_messages = self.adapter.to_provider_messages(messages)
        provider_tools = self.adapter.to_provider_tools(tools)
        messages_with_system = [{"role": "system", "content": self.system_prompt}] + provider_messages
        response = self.client.chat(model=self.model, messages=messages_with_system, tools=provider_tools)
        return self.adapter.from_provider_response(response)
    
    def chat_stream(self, messages: list[Message], tools: list[ToolDefinition]) -> Message:
        provider_messages = self.adapter.to_provider_messages(messages)
        provider_tools = self.adapter.to_provider_tools(tools)
        messages_with_system = [{"role": "system", "content": self.system_prompt}] + provider_messages
        return self.client.chat_stream(model=self.model, messages=messages_with_system, tools=provider_tools)
