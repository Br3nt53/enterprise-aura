from fastapi import APIRouter, Depends

from aura_v2.api.auth import api_key_guard

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/active")
def list_active(_=None):
    if _ is None:
        _ = Depends(api_key_guard)
    # placeholder returns empty
    return {"tracks": []}
