from __future__ import annotations

from enum import Enum
from typing import Any, TypedDict


class TaskInfo(TypedDict):
    task_info: dict[str, Any]


class ArrowPosition(Enum):
    Middle: int = 0
    End: int = 1
