import json
from .ui import Colors

def print_tool_info(tool_name: str, args: dict):
    """Print informative output about tool execution."""
    print(f"\n{Colors.TOOL}╭─ {tool_name}{Colors.RESET}", end="")
    
    if tool_name == "shell":
        print(f"\n{Colors.TOOL}│{Colors.RESET} {Colors.DIM}${Colors.RESET} {args.get('command', '')}")
    
    elif tool_name in ["create_file", "overwrite_file"]:
        path = args.get('path', '')
        print(f" {path}")
        
        from .diff_utils import generate_diff, colorize_diff
        diff = generate_diff(tool_name, **args)
        if diff:
            print(f"{Colors.TOOL}│{Colors.RESET}")
            for line in colorize_diff(diff).split('\n'):
                print(f"{Colors.TOOL}│{Colors.RESET} {line}")
    
    elif tool_name == "replace_exact_in_file":
        path = args.get('path', '')
        print(f" {path}")
        
        from .diff_utils import generate_diff, colorize_diff
        diff = generate_diff(tool_name, **args)
        if diff:
            print(f"{Colors.TOOL}│{Colors.RESET}")
            for line in colorize_diff(diff).split('\n'):
                print(f"{Colors.TOOL}│{Colors.RESET} {line}")
    
    else:
        if args:
            args_str = json.dumps(args, indent=2)
            if len(args_str) > 100:
                args_str = args_str[:100] + "..."
            indented = "\n".join(f"{Colors.TOOL}│{Colors.RESET} {Colors.DIM}{line}{Colors.RESET}" for line in args_str.split("\n"))
            print(f"\n{indented}")
    
    print(f"{Colors.TOOL}╰─{Colors.RESET}")
