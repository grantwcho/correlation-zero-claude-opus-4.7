from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResponseFormat(str, Enum):
    FREEFORM = "freeform"


@dataclass
class AgentQuery:
    query_id: str
    prompt: str
    response_format: str = ResponseFormat.FREEFORM.value
    context: dict[str, Any] = field(default_factory=dict)
    metrics: list[str] = field(default_factory=list)
