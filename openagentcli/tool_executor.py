import time
from typing import Set, Dict, Callable
from .ui import Colors
from .tool_display import print_tool_info
from .diff_utils import generate_diff, colorize_diff
from openagentcli.protocol import Message, ProtocolAdapter

class ToolExecutor:
    def __init__(self, functions_map: Dict[str, Callable], adapter: ProtocolAdapter):
        self.functions_map = functions_map
        self.adapter = adapter
        self.trusted_tools: Set[str] = {"read_file", "list_directory", "search_files_by_name", "search_files_by_content"}
    
    def confirm_tool(self, tool_name: str) -> bool:
        if tool_name in self.trusted_tools:
            print(f"{Colors.SUCCESS}{Colors.BOLD}[Trusted]{Colors.RESET}")
            return True
        
        print(f"{Colors.BOLD}[Confirm]{Colors.RESET} Execute {Colors.TOOL}{tool_name}{Colors.RESET}? {Colors.DIM}(y/n/t){Colors.RESET} ", end="")
        try:
            choice = input().strip().lower()
        except KeyboardInterrupt:
            print()
            return False
        
        if choice == 't':
            self.trusted_tools.add(tool_name)
            print(f"{Colors.SUCCESS}✓ Trusted {tool_name}{Colors.RESET}")
            return True
        return choice == 'y'
    
    def execute_tool(self, tool_name: str, args: dict, tool_call_id: str) -> Message:
        """Execute a tool and return the result message."""
        print_tool_info(tool_name, args)
        
        if not self.confirm_tool(tool_name):
            print(f"{Colors.ERROR}✗ Cancelled{Colors.RESET}\n")
            return self.adapter.to_tool_result(tool_call_id, {"error": "The user declined the use of this tool. Ask them why they did so."})
        
        print(f"{Colors.TOOL_RESULT}╭─ Result{Colors.RESET}")
        start_time = time.time()
        try:
            result = self.functions_map[tool_name](**args)
            elapsed = time.time() - start_time
            print(f"{Colors.TOOL_RESULT}╰─{Colors.RESET} {Colors.SUCCESS}✓{Colors.RESET} {Colors.DIM}{elapsed:.2f}s{Colors.RESET}\n")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"{Colors.TOOL_RESULT}╰─{Colors.RESET} {Colors.ERROR}✗ {str(e)}{Colors.RESET} {Colors.DIM}{elapsed:.2f}s{Colors.RESET}\n")
            result = {"error": str(e)}
        
        return self.adapter.to_tool_result(tool_call_id, result)
