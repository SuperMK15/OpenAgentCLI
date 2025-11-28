import json
import asyncio
import os
import readline
import logging
from openagentcli.models.cohere_model import CohereModel
from openagentcli.server.mcp_server import mcp
from openagentcli.ui import Colors, Spinner
from openagentcli.chat_storage import ChatStorage
from openagentcli.tool_executor import ToolExecutor
from openagentcli.tool_display import display_tool_list, display_tool_detail

logging.getLogger("httpx").setLevel(logging.WARNING)

class AgentCLI:
    def __init__(self):
        self.model = CohereModel()
        self.messages = []
        self.tools = asyncio.run(self._get_tools())
        functions_map = asyncio.run(self._get_functions())
        self.executor = ToolExecutor(functions_map)
        self.storage = ChatStorage()
        
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
        print(f"{Colors.DIM}Type /help for commands{Colors.RESET}\n")

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
            
            if user_input == '/quit':
                print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                break
            
            if user_input == '/help':
                print(f"\n{Colors.BOLD}Commands:{Colors.RESET}")
                print(f"  /help              - Show this help")
                print(f"  /tools             - List all available tools")
                print(f"  /tools <name>      - Show details for a specific tool")
                print(f"  /save <name>       - Save current chat")
                print(f"  /load <name>       - Load saved chat")
                print(f"  /list-saved        - List all saved chats")
                print(f"  /delete <name>     - Delete a saved chat")
                print(f"  /clear-saved       - Delete all saved chats")
                print(f"  /clear             - Clear chat context")
                print(f"  /quit              - Exit the CLI")
                print(f"  !<command>         - Execute bash command\n")
                continue
            
            if user_input == '/tools':
                display_tool_list(self.tools)
                continue
            
            if user_input.startswith('/tools '):
                tool_name = user_input[7:].strip()
                display_tool_detail(self.tools, tool_name)
                continue
            
            if user_input.startswith('/save '):
                name = user_input[6:].strip()
                if name:
                    self.storage.save(name, self.messages)
                else:
                    print(f"\n{Colors.ERROR}Usage: /save <name>{Colors.RESET}\n")
                continue
            
            if user_input.startswith('/load '):
                name = user_input[6:].strip()
                if name:
                    if self.messages:
                        print(f"{Colors.WARNING}Current chat will be replaced. Continue? (y/n): {Colors.RESET}", end='')
                        confirm = input().strip().lower()
                        if confirm != 'y':
                            print(f"\n{Colors.DIM}Load cancelled{Colors.RESET}\n")
                            continue
                    messages = self.storage.load(name)
                    if messages is not None:
                        self.messages = messages
                else:
                    print(f"\n{Colors.ERROR}Usage: /load <name>{Colors.RESET}\n")
                continue
            
            if user_input == '/list-saved':
                self.storage.list_all()
                continue
            
            if user_input.startswith('/delete '):
                name = user_input[8:].strip()
                if name:
                    print(f"{Colors.WARNING}Delete chat '{name}'? (y/n): {Colors.RESET}", end='')
                    confirm = input().strip().lower()
                    if confirm == 'y':
                        self.storage.delete(name)
                    else:
                        print(f"\n{Colors.DIM}Delete cancelled{Colors.RESET}\n")
                else:
                    print(f"\n{Colors.ERROR}Usage: /delete <name>{Colors.RESET}\n")
                continue
            
            if user_input == '/clear-saved':
                print(f"{Colors.WARNING}Delete all saved chats? (y/n): {Colors.RESET}", end='')
                confirm = input().strip().lower()
                if confirm == 'y':
                    self.storage.clear_all()
                else:
                    print(f"\n{Colors.DIM}Clear cancelled{Colors.RESET}\n")
                continue
            
            if user_input == '/clear':
                self.messages = []
                print(f"\n{Colors.DIM}Chat context cleared{Colors.RESET}\n")
                continue
            
            if user_input.startswith('/'):
                print(f"\n{Colors.ERROR}Unknown command: {user_input}{Colors.RESET}")
                print(f"{Colors.DIM}Type /help for available commands{Colors.RESET}\n")
                continue
            
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
