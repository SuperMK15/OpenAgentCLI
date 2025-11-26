from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseModel(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any:
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any:
        pass
