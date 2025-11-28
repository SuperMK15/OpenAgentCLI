import json
from pathlib import Path
from datetime import datetime
from openagentcli.ui import Colors


class ChatStorage:
    def __init__(self):
        self.chats_dir = Path.home() / ".openagentcli" / "chats"
        self.chats_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, name: str, messages: list) -> bool:
        """Save chat to file."""
        if not messages:
            print(f"\n{Colors.ERROR}No messages to save{Colors.RESET}\n")
            return False
        
        chat_file = self.chats_dir / f"{name}.json"
        if chat_file.exists():
            print(f"{Colors.WARNING}Chat '{name}' already exists. Overwrite? (y/n): {Colors.RESET}", end='')
            confirm = input().strip().lower()
            if confirm != 'y':
                print(f"\n{Colors.DIM}Save cancelled{Colors.RESET}\n")
                return False
        
        data = {
            "name": name,
            "saved_at": datetime.now().isoformat(),
            "messages": messages
        }
        chat_file.write_text(json.dumps(data, indent=2))
        print(f"\n{Colors.SUCCESS}✓ Saved chat to {chat_file}{Colors.RESET}\n")
        return True
    
    def load(self, name: str) -> list | None:
        """Load chat from file."""
        chat_file = self.chats_dir / f"{name}.json"
        if not chat_file.exists():
            print(f"\n{Colors.ERROR}Chat '{name}' not found{Colors.RESET}\n")
            return None
        
        data = json.loads(chat_file.read_text())
        messages = data["messages"]
        print(f"\n{Colors.SUCCESS}✓ Loaded chat '{name}' ({len(messages)} messages){Colors.RESET}\n")
        return messages
    
    def list_all(self):
        """List all saved chats."""
        chats = sorted(self.chats_dir.glob("*.json"))
        if not chats:
            print(f"\n{Colors.DIM}No saved chats{Colors.RESET}\n")
            return
        
        print(f"\n{Colors.BOLD}Saved Chats:{Colors.RESET}")
        for chat_file in chats:
            data = json.loads(chat_file.read_text())
            name = chat_file.stem
            saved_at = data.get("saved_at", "unknown")
            msg_count = len(data.get("messages", []))
            print(f"  {Colors.BOLD}{name}{Colors.RESET} {Colors.DIM}({msg_count} messages, {saved_at}){Colors.RESET}")
        print()
    
    def delete(self, name: str):
        """Delete a specific saved chat."""
        chat_file = self.chats_dir / f"{name}.json"
        if not chat_file.exists():
            print(f"\n{Colors.ERROR}Chat '{name}' not found{Colors.RESET}\n")
            return
        
        chat_file.unlink()
        print(f"\n{Colors.SUCCESS}✓ Deleted chat '{name}'{Colors.RESET}\n")
    
    def clear_all(self):
        """Delete all saved chats."""
        chats = list(self.chats_dir.glob("*.json"))
        if not chats:
            print(f"\n{Colors.DIM}No saved chats to clear{Colors.RESET}\n")
            return
        
        for chat_file in chats:
            chat_file.unlink()
        print(f"\n{Colors.SUCCESS}✓ Cleared {len(chats)} saved chat(s){Colors.RESET}\n")
