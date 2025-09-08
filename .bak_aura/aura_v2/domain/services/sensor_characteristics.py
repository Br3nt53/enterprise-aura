from dataclasses import dataclass
@dataclass(frozen=True)
class SensorCharacteristics:
    name: str = "generic"
