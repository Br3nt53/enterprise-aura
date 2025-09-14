# tests/architecture/test_container_contract.py
from aura_v2.application.use_cases.process_detections import ProcessDetectionsUseCase
from aura_v2.infrastructure.container import Container


def test_container_contract():
    c = Container()
    c.init_resources()
    pipeline = c.tracking_pipeline()
    assert isinstance(pipeline, ProcessDetectionsUseCase)
    assert hasattr(pipeline, "process")
