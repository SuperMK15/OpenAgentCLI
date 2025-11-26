import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("openagentcli")

def validate_path(path: str, must_exist: bool = False) -> str:
    """Validate path and return error message if invalid."""
    if not path or not isinstance(path, str):
        return "Error: path must be a non-empty string"
    
    try:
        p = Path(path)
        if must_exist and not p.exists():
            return f"Error: path '{path}' does not exist"
        if must_exist and not p.is_file():
            return f"Error: path '{path}' is not a file"
    except Exception as e:
        return f"Error: invalid path '{path}': {str(e)}"
    
    return ""

@mcp.tool()
def read_file(path: str) -> str:
    """Read contents of a file."""
    err = validate_path(path, must_exist=True)
    if err:
        raise ValueError(err)
    return Path(path).read_text()

@mcp.tool()
def write_file(path: str, content: str, command: str = "create") -> str:
    """Write content to a file. Commands: create, str_replace, insert, append."""
    err = validate_path(path)
    if err:
        raise ValueError(err)
    
    if command not in ["create", "str_replace", "insert", "append"]:
        raise ValueError(f"invalid command '{command}'. Must be one of: create, str_replace, insert, append")
    
    p = Path(path)
    
    if command == "create":
        p.write_text(content)
        return f"Created {path}"
    
    if not p.exists():
        raise FileNotFoundError(f"{path} does not exist")
    
    existing = p.read_text()
    
    if command == "append":
        p.write_text(existing + content)
        return f"Appended to {path}"
    
    if command == "str_replace":
        parts = content.split("|||", 1)
        if len(parts) != 2:
            raise ValueError("str_replace requires content in format 'old_str|||new_str'")
        old_str, new_str = parts
        if old_str not in existing:
            raise ValueError(f"old_str not found in {path}. Make sure the old_str exactly matches the text in the file")
        p.write_text(existing.replace(old_str, new_str, 1))
        return f"Replaced in {path}"
    
    if command == "insert":
        parts = content.split("|||", 1)
        if len(parts) != 2:
            raise ValueError("insert requires content in format 'line_number|||new_str'")
        try:
            line_num = int(parts[0])
        except ValueError:
            raise ValueError(f"line_number must be an integer, got '{parts[0]}'")
        new_str = parts[1]
        lines = existing.split('\n')
        if line_num < 0 or line_num > len(lines):
            raise ValueError(f"line_number {line_num} out of range (file has {len(lines)} lines)")
        lines.insert(line_num, new_str)
        p.write_text('\n'.join(lines))
        return f"Inserted at line {line_num} in {path}"
    
    raise ValueError(f"Unknown command {command}")

@mcp.tool()
def list_directory(path: str = ".", depth: int = 0) -> str:
    """List contents of a directory. depth=0 for current only, depth>0 for recursive."""
    err = validate_path(path)
    if err:
        raise ValueError(err)
    
    base = Path(path)
    if not base.exists():
        raise FileNotFoundError(f"directory '{path}' does not exist")
    if not base.is_dir():
        raise ValueError(f"'{path}' is not a directory")
    
    if depth == 0:
        return "\n".join(str(p) for p in base.iterdir())
    
    results = []
    def walk(p: Path, current_depth: int):
        try:
            for item in p.iterdir():
                results.append(str(item))
                if item.is_dir() and current_depth < depth:
                    walk(item, current_depth + 1)
        except PermissionError:
            pass
    
    walk(base, 0)
    return "\n".join(results)

@mcp.tool()
def search_files_by_name(pattern: str, path: str = ".") -> str:
    """Search for files by name using regex pattern."""
    if not pattern:
        raise ValueError("pattern must be a non-empty string")
    
    err = validate_path(path)
    if err:
        raise ValueError(err)
    
    base = Path(path)
    if not base.exists():
        raise FileNotFoundError(f"directory '{path}' does not exist")
    
    import re
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise ValueError(f"invalid regex pattern: {e}")
    
    results = []
    for p in base.rglob("*"):
        if p.is_file() and regex.search(p.name):
            results.append(str(p.relative_to(base)))
    
    return "\n".join(results) if results else f"No files matching pattern '{pattern}' found in {path}"

@mcp.tool()
def search_files_by_content(pattern: str, path: str = ".") -> str:
    """Search for files by content using regex pattern."""
    if not pattern:
        raise ValueError("pattern must be a non-empty string")
    
    err = validate_path(path)
    if err:
        raise ValueError(err)
    
    base = Path(path)
    if not base.exists():
        raise FileNotFoundError(f"directory '{path}' does not exist")
    
    import re
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise ValueError(f"invalid regex pattern: {e}")
    
    results = []
    for p in base.rglob("*"):
        if p.is_file():
            try:
                content = p.read_text()
                if regex.search(content):
                    results.append(str(p.relative_to(base)))
            except:
                pass
    
    return "\n".join(results) if results else f"No files with content matching pattern '{pattern}' found in {path}"

@mcp.tool()
def shell(command: str) -> Dict[str, Any]:
    """Execute a bash command and return output."""
    if not command or not isinstance(command, str):
        return {"error": "Error: command must be a non-empty string", "returncode": 1}
    
    import sys
    
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )
    
    stdout_lines = []
    stderr_lines = []
    
    for line in process.stdout:
        print(line, end='', flush=True)
        stdout_lines.append(line)
    
    for line in process.stderr:
        print(line, end='', file=sys.stderr, flush=True)
        stderr_lines.append(line)
    
    process.wait()
    
    return {
        "stdout": ''.join(stdout_lines),
        "stderr": ''.join(stderr_lines),
        "returncode": process.returncode
    }

def create_server():
    """Create and return the MCP server instance."""
    return mcp

def get_tools_schema() -> List[Dict[str, Any]]:
    """Get schema of all available tools."""
    tools = []
    for tool_name, tool_func in mcp._tool_manager._tools.items():
        tools.append({
            "name": tool_name,
            "description": tool_func.__doc__ or "",
            "parameters": tool_func.__annotations__
        })
    return tools
