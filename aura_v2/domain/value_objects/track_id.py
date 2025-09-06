from typing_extensions import Annotated
from pydantic import Field

# Non-negative integer ID for a track
TrackID = Annotated[int, Field(ge=0)]
