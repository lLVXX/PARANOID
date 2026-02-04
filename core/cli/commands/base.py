# core/cli/commands/base.py
from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def matches(self, cmd: str) -> bool:
        pass

    @abstractmethod
    def execute(self, cmd: str, session_mgr, scanner) -> bool:
        """
        Return False to exit CLI
        """
        pass
