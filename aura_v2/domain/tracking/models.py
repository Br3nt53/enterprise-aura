# domain/tracking/models.py
@dataclass
class Track:
    id: TrackID
    trajectory: List[Detection]
    confidence: float
    
class TrackingMetrics(Protocol):
    def compute(self, predictions: TrackSet, ground_truth: TrackSet) -> Metrics:
        ...

# domain/tracking/services.py
class TrackingEvaluationService:
    def __init__(self, metrics_calculator: TrackingMetrics):
        self.calculator = metrics_calculator
    
    def evaluate(self, predictions: TrackSet, ground_truth: TrackSet) -> EvaluationResult:
        # Pure business logic, no I/O
        return self.calculator.compute(predictions, ground_truth)

# infrastructure/repositories/jsonl_repository.py
class JSONLTrackRepository:
    def load_tracks(self, source: DataSource) -> TrackSet:
        # All I/O isolated here
        ...

# application/use_cases/evaluate_tracking.py
class EvaluateTrackingUseCase:
    def __init__(self, 
                 track_repo: TrackRepository,
                 eval_service: TrackingEvaluationService,
                 result_repo: ResultRepository):
        self.track_repo = track_repo
        self.eval_service = eval_service
        self.result_repo = result_repo
    
    def execute(self, command: EvaluateCommand) -> None:
        predictions = self.track_repo.load_tracks(command.pred_source)
        ground_truth = self.track_repo.load_tracks(command.gt_source)
        result = self.eval_service.evaluate(predictions, ground_truth)
        self.result_repo.save(result, command.output_dest)