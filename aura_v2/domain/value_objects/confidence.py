from typing_extensions import Annotated
from pydantic import Field

# 0..1 probability-like confidence
Confidence = Annotated[float, Field(ge=0.0, le=1.0)]
