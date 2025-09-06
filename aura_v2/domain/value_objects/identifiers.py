from typing import NewType
from uuid import UUID, uuid4

TrackID = NewType("TrackID", str)

def new_track_id() -> TrackID:
    return TrackID(str(uuid4()))

def ensure_track_id(value: str | UUID) -> TrackID:
    return TrackID(str(value))
