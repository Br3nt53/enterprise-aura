from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

# domain/tracking/models.py
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

@dataclass
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

class Track:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    id: TrackID
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    trajectory: List[Detection]
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    confidence: float
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

class TrackingMetrics(Protocol):
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    def compute(self, predictions: TrackSet, ground_truth: TrackSet) -> Metrics:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        ...
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID


from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

# domain/tracking/services.py
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

class TrackingEvaluationService:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    def __init__(self, metrics_calculator: TrackingMetrics):
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        self.calculator = metrics_calculator
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    def evaluate(self, predictions: TrackSet, ground_truth: TrackSet) -> EvaluationResult:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        # Pure business logic, no I/O
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        return self.calculator.compute(predictions, ground_truth)
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID


from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

# infrastructure/repositories/jsonl_repository.py
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

class JSONLTrackRepository:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    def load_tracks(self, source: DataSource) -> TrackSet:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        # All I/O isolated here
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        ...
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID


from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

# application/use_cases/evaluate_tracking.py
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

class EvaluateTrackingUseCase:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    def __init__(self, 
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

                 track_repo: TrackRepository,
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

                 eval_service: TrackingEvaluationService,
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

                 result_repo: ResultRepository):
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        self.track_repo = track_repo
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        self.eval_service = eval_service
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        self.result_repo = result_repo
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

    def execute(self, command: EvaluateCommand) -> None:
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        predictions = self.track_repo.load_tracks(command.pred_source)
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        ground_truth = self.track_repo.load_tracks(command.gt_source)
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        result = self.eval_service.evaluate(predictions, ground_truth)
from dataclasses import dataclass
from typing import List, Protocol

from ..entities import Detection
from ..value_objects import TrackID

        self.result_repo.save(result, command.output_dest)
