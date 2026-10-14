from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_region_service
from app.schemas.region import RegionKind, RegionOption
from app.services.region_service import RegionService

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("", response_model=list[RegionOption], summary="List selectable cities or states")
def list_regions(
    service: Annotated[RegionService, Depends(get_region_service)],
    type: Annotated[RegionKind, Query(description="city or state")] = "city",
    state: Annotated[Optional[str], Query(min_length=2, max_length=80)] = None,
):
    return service.list_regions(type, state)


@router.get("/search", response_model=list[RegionOption], summary="Search any place worldwide (geocoding)")
def search_places(
    service: Annotated[RegionService, Depends(get_region_service)],
    q: Annotated[str, Query(min_length=2, max_length=80)],
    state: Annotated[Optional[str], Query(min_length=2, max_length=80)] = None,
):
    return service.search_places(q, state)
