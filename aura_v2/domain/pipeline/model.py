from dataclasses import dataclass
from datetime import timedelta
from typing import List, Protocol, Any, Dict


@dataclass
class RetryPolicy:
    retries: int = 3
    delay: timedelta = timedelta(seconds=5)


class PipelineStage(Protocol):
    def execute(self, context: "PipelineContext") -> "PipelineResult": ...


@dataclass
class PipelineConfig:
    name: str
    version: str
    stages: List[PipelineStage]
    retry_policy: RetryPolicy


@dataclass
class PipelineContext:
    data: Any
    metadata: Dict[str, Any]


@dataclass
class PipelineResult:
    success: bool
    message: str
    data: Any
