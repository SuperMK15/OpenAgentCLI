import sys
import time
import threading

class Colors:
    USER = "\033[36m"
    ASSISTANT = "\033[35m"
    TOOL = "\033[33m"
    TOOL_OUTPUT = "\033[90m"
    SUCCESS = "\033[32m"
    ERROR = "\033[31m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    DIFF_ADD = "\033[32m"
    DIFF_REMOVE = "\033[31m"
    DIFF_HEADER = "\033[1m"
    DIFF_LOCATION = "\033[36m"

class Spinner:
    def __init__(self):
        self.spinning = False
        self.thread = None
    
    def start(self):
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
    
    def stop(self):
        self.spinning = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r \r')
        sys.stdout.flush()
    
    def _spin(self):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        while self.spinning:
            sys.stdout.write(f'\r{Colors.DIM}{chars[i % len(chars)]} Thinking...{Colors.RESET}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
