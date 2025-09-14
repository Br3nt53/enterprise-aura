from typing import List

from pydantic import BaseModel, field_validator


class CovarianceMatrix(BaseModel):
    """3x3 covariance matrix for position uncertainty."""

    matrix: List[List[float]]

    @field_validator("matrix")
    @classmethod
    def _validate(cls, m: List[List[float]]):
        if len(m) != 3 or any(len(row) != 3 for row in m):
            raise ValueError("Covariance.matrix must be 3x3")
        # basic numeric check
        for row in m:
            for v in row:
                if not isinstance(v, (int, float)):
                    raise ValueError("Covariance entries must be numbers")
        return m
