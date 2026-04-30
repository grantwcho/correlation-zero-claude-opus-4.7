from dataclasses import asdict, dataclass, field
from enum import Enum


class ResponseFormat(str, Enum):
    DAILY_FORECAST = "daily_forecast"
    SCENARIO = "scenario"
    BRIEF = "brief"
    FREEFORM = "freeform"


@dataclass
class CI:
    level: float
    low: float
    high: float


@dataclass
class Prediction:
    metric_id: str
    point_estimate: float
    unit: str
    confidence_intervals: list[CI] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    reasoning_summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

