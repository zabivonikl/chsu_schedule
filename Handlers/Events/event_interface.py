from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class Handler(ABC):
    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    async def handle_event(self, request) -> None:
        pass