from __future__ import annotations

import uuid
from abc import ABC
from datetime import datetime, timezone
from typing import Any


class BaseEntity(ABC):
    def __init__(self, id: uuid.UUID | None = None, **kwargs: Any) -> None:
        self.id = id or uuid.uuid4()
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
