from pathlib import Path
from difflib import unified_diff
from .ui import Colors

def colorize_diff(diff: str) -> str:
    """Add ANSI colors to diff output."""
    lines = []
    for line in diff.split('\n'):
        if line.startswith('+++') or line.startswith('---'):
            lines.append(f"{Colors.DIFF_HEADER}{line}{Colors.RESET}")
        elif line.startswith('+'):
            lines.append(f"{Colors.DIFF_ADD}{line}{Colors.RESET}")
        elif line.startswith('-'):
            lines.append(f"{Colors.DIFF_REMOVE}{line}{Colors.RESET}")
        elif line.startswith('@@'):
            lines.append(f"{Colors.DIFF_LOCATION}{line}{Colors.RESET}")
        else:
            lines.append(f"{Colors.DIM}{line}{Colors.RESET}")
    return '\n'.join(lines)

def generate_diff(tool_name: str, path: str, **kwargs) -> str:
    """Generate unified diff for file operations."""
    p = Path(path)
    
    if tool_name == "create_file":
        if p.exists():
            old_lines = p.read_text().splitlines(keepends=True)
            new_lines = kwargs['content'].splitlines(keepends=True)
            return ''.join(unified_diff(old_lines, new_lines, fromfile=f"a/{path}", tofile=f"b/{path}"))
        else:
            new_lines = kwargs['content'].splitlines(keepends=True)
            return ''.join(unified_diff([], new_lines, fromfile="/dev/null", tofile=f"b/{path}"))
    
    if not p.exists():
        return ""
    
    old_content = p.read_text()
    old_lines = old_content.splitlines(keepends=True)
    
    if tool_name == "overwrite_file":
        new_lines = kwargs['content'].splitlines(keepends=True)
    elif tool_name == "replace_exact_in_file":
        new_lines = old_content.replace(kwargs['old_str'], kwargs['new_str'], 1).splitlines(keepends=True)
    else:
        raise ValueError(f"Unknown tool_name: {tool_name}")
    
    return ''.join(unified_diff(old_lines, new_lines, fromfile=f"a/{path}", tofile=f"b/{path}"))
