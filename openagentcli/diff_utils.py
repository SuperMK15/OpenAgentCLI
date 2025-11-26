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

def generate_diff(path: str, command: str, content: str) -> str:
    """Generate unified diff for write_file operations."""
    p = Path(path)
    
    if command == "create":
        if p.exists():
            old_lines = p.read_text().splitlines(keepends=True)
            new_lines = content.splitlines(keepends=True)
            return ''.join(unified_diff(old_lines, new_lines, fromfile=f"a/{path}", tofile=f"b/{path}"))
        else:
            new_lines = content.splitlines(keepends=True)
            return ''.join(unified_diff([], new_lines, fromfile="/dev/null", tofile=f"b/{path}"))
    
    if not p.exists():
        return ""
    
    old_content = p.read_text()
    old_lines = old_content.splitlines(keepends=True)
    
    if command == "append":
        new_lines = (old_content + content).splitlines(keepends=True)
    elif command == "str_replace":
        parts = content.split("|||", 1)
        if len(parts) == 2:
            new_lines = old_content.replace(parts[0], parts[1], 1).splitlines(keepends=True)
        else:
            return ""
    elif command == "insert":
        parts = content.split("|||", 1)
        if len(parts) == 2:
            lines = old_content.split('\n')
            lines.insert(int(parts[0]), parts[1])
            new_lines = '\n'.join(lines).splitlines(keepends=True)
        else:
            return ""
    else:
        return ""
    
    return ''.join(unified_diff(old_lines, new_lines, fromfile=f"a/{path}", tofile=f"b/{path}"))
