import json
import asyncio
import os
import readline
import logging
from openagentcli.models.cohere_model import CohereModel
from openagentcli.server.mcp_server import mcp
from openagentcli.ui import Colors, Spinner
from openagentcli.tool_executor import ToolExecutor

logging.getLogger("httpx").setLevel(logging.WARNING)

class AgentCLI:
    def __init__(self):
        self.model = CohereModel()
        self.messages = []
        self.tools = asyncio.run(self._get_tools())
        functions_map = asyncio.run(self._get_functions())
        self.executor = ToolExecutor(functions_map)
        
        readline.parse_and_bind(r'"\e[A": previous-history')
        readline.parse_and_bind(r'"\e[B": next-history')
    
    async def _get_tools(self):
        tools = []
        for tool in await mcp.list_tools():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema or {"type": "object", "properties": {}}
                }
            })
        return tools
    
    async def _get_functions(self):
        return {name: tool.fn for name, tool in mcp._tool_manager._tools.items()}
    
    def run(self):
        print(f"\n{Colors.BOLD}OpenAgentCLI{Colors.RESET} {Colors.DIM}v0.1.0{Colors.RESET}")
        print(f"{Colors.DIM}Type 'quit' to exit, '!' prefix for direct bash commands{Colors.RESET}\n")

        ctrl_c_waiting = False  # when True, next Ctrl+C on blank input exits

        while True:
            try:
                user_input = input(f"\001{Colors.USER}\002>\001{Colors.RESET}\002 ").strip()

                if user_input:
                    ctrl_c_waiting = False

            except KeyboardInterrupt:
                if ctrl_c_waiting:
                    print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                    break

                print(f"\n{Colors.DIM}Press Ctrl+C again to exit{Colors.RESET}")
                ctrl_c_waiting = True
                continue
            
            if user_input.lower() == 'quit':
                print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                break
            
            if not user_input:
                continue
            
            ctrl_c_waiting = False

            if user_input.startswith('!'):
                os.system(user_input[1:].strip())
                print()
                continue
            
            self.messages.append({"role": "user", "content": user_input})
            
            while True:
                spinner = Spinner()
                spinner.start()
                try:
                    response = self.model.chat(self.messages, self.tools)
                except KeyboardInterrupt:
                    spinner.stop()
                    print(f"\n{Colors.DIM}Interrupted{Colors.RESET}\n")
                    break
                finally:
                    spinner.stop()
                
                if not response.message.tool_calls:
                    print(f"\n{Colors.ASSISTANT}> {Colors.RESET}{response.message.content[0].text}\n")
                    self.messages.append({"role": "assistant", "content": response.message.content[0].text})
                    break
                
                if response.message.tool_plan:
                    print(f"\n{Colors.ASSISTANT}> {Colors.RESET}{response.message.tool_plan}")
                
                self.messages.append({
                    "role": "assistant",
                    "tool_plan": response.message.tool_plan,
                    "tool_calls": response.message.tool_calls
                })
                
                for tc in response.message.tool_calls:
                    tool_name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    result_msg = self.executor.execute_tool(tool_name, args, tc.id)
                    self.messages.append(result_msg)

def main():
    cli = AgentCLI()
    cli.run()

if __name__ == "__main__":
    main()
