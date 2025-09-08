# aura_v2/domain/value_objects/identifiers.py
from typing import NewType
from uuid import UUID, uuid4

TrackID = NewType("TrackID", str)
SensorID = NewType("SensorID", str)
SourceID = NewType("SourceID", str)


def new_track_id() -> TrackID:
    """Creates a new, unique TrackID."""
    return TrackID(str(uuid4()))


def ensure_track_id(value: str | UUID) -> TrackID:
    """Ensures a value is a valid TrackID."""
    return TrackID(str(value))
