import json
import time
from typing import Set, Dict, Callable
from .ui import Colors
from .tool_display import print_tool_info
from .diff_utils import generate_diff, colorize_diff

class ToolExecutor:
    def __init__(self, functions_map: Dict[str, Callable]):
        self.functions_map = functions_map
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
    
    def execute_tool(self, tool_name: str, args: dict, tool_call_id: str) -> dict:
        """Execute a tool and return the result message."""
        print_tool_info(tool_name, args)
        
        if tool_name == "write_file":
            diff = generate_diff(args.get('path', ''), args.get('command', 'create'), args.get('content', ''))
            if diff:
                print(f"\n{Colors.DIM}Diff:{Colors.RESET}")
                print(colorize_diff(diff))
                print()
        
        if not self.confirm_tool(tool_name):
            print(f"{Colors.ERROR}✗ Cancelled{Colors.RESET}\n")
            return {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": [{"type": "document", "document": {"data": json.dumps({"error": "User declined to execute this tool"})}}]
            }
        
        print(f"{Colors.TOOL_OUTPUT}╭─ Output{Colors.RESET}")
        start_time = time.time()
        try:
            result = self.functions_map[tool_name](**args)
            elapsed = time.time() - start_time
            print(f"{Colors.TOOL_OUTPUT}╰─{Colors.RESET} {Colors.SUCCESS}✓{Colors.RESET} {Colors.DIM}{elapsed:.2f}s{Colors.RESET}\n")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"{Colors.TOOL_OUTPUT}╰─{Colors.RESET} {Colors.ERROR}✗ {str(e)}{Colors.RESET} {Colors.DIM}{elapsed:.2f}s{Colors.RESET}\n")
            result = {"error": str(e)}
        
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": [{"type": "document", "document": {"data": json.dumps(result)}}]
        }
