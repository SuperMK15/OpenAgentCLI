import json
from .ui import Colors

def display_tool_list(tools: list):
    """Display a list of all available tools."""
    print(f"\n{Colors.BOLD}Available Tools:{Colors.RESET}\n")
    for tool in tools:
        name = tool["function"]["name"]
        desc = tool["function"]["description"].split('\n')[0][:80]
        print(f"  {Colors.TOOL}{name}{Colors.RESET}")
        if desc:
            print(f"    {Colors.DIM}{desc}{Colors.RESET}")
    print()

def display_tool_detail(tools: list, tool_name: str):
    """Display detailed information about a specific tool."""
    tool = next((t for t in tools if t["function"]["name"] == tool_name), None)
    if not tool:
        print(f"\n{Colors.DIM}Tool '{tool_name}' not found{Colors.RESET}\n")
        return
    
    func = tool["function"]
    print(f"\n{Colors.BOLD}{func['name']}{Colors.RESET}")
    if func.get("description"):
        print(f"\n{func['description']}")
    
    params = func.get("parameters", {}).get("properties", {})
    required = func.get("parameters", {}).get("required", [])
    
    if params:
        print(f"\n{Colors.BOLD}Parameters:{Colors.RESET}")
        for param, schema in params.items():
            req = " (required)" if param in required else ""
            print(f"  {Colors.TOOL}{param}{Colors.RESET}{req}")
            if schema.get("description"):
                print(f"    {Colors.DIM}{schema['description']}{Colors.RESET}")
    print()

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
