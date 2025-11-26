import json
from .ui import Colors

def print_tool_info(tool_name: str, args: dict):
    """Print informative output about tool execution."""
    print(f"\n{Colors.TOOL}╭─ {tool_name}{Colors.RESET}", end="")
    
    if tool_name == "shell":
        print(f"\n{Colors.TOOL}│{Colors.RESET} {Colors.DIM}${Colors.RESET} {args.get('command', '')}")
    
    elif tool_name == "write_file":
        path = args.get('path', '')
        command = args.get('command', 'create')
        content = args.get('content', '')
        
        print(f" {Colors.DIM}{command}{Colors.RESET} {path}")
        
        if command == "create":
            print(f"{Colors.TOOL}│{Colors.RESET}")
            for i, line in enumerate(content.split('\n')[:8]):
                print(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIFF_ADD}+{Colors.RESET} {line}")
            if len(content.split('\n')) > 8:
                remaining = len(content.split('\n')) - 8
                print(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIM}... {remaining} more lines{Colors.RESET}")
        
        elif command == "str_replace":
            parts = content.split("|||", 1)
            if len(parts) == 2:
                old, new = parts
                print(f"{Colors.TOOL}│{Colors.RESET}")
                for line in old.split('\n')[:3]:
                    print(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIFF_REMOVE}-{Colors.RESET} {line}")
                for line in new.split('\n')[:3]:
                    print(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIFF_ADD}+{Colors.RESET} {line}")
        
        elif command == "append":
            print(f"{Colors.TOOL}│{Colors.RESET}")
            for line in content.split('\n')[:5]:
                print(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIFF_ADD}+{Colors.RESET} {line}")
            if len(content.split('\n')) > 5:
                remaining = len(content.split('\n')) - 5
                print(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIM}... {remaining} more lines{Colors.RESET}")
    
    else:
        if args:
            args_str = json.dumps(args, indent=2)
            if len(args_str) > 100:
                args_str = args_str[:100] + "..."
            indented = "\n".join(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIM}{line}{Colors.RESET}" for line in args_str.split("\n"))
            print(f"\n{indented}")
    
    print(f"{Colors.TOOL}╰─{Colors.RESET}")
