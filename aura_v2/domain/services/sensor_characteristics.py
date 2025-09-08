# aura_v2/domain/services/sensor_characteristics.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SensorCharacteristics:
    name: str = "generic"
    params: dict = field(default_factory=dict)

    def __init__(self, name: str = "generic", *_, **kwargs):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "params", kwargs or {})
