from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response

from app.api.dependencies import get_analysis_service, get_region_service
from app.schemas.analysis import AnalysisQuery, AnalysisResponse
from app.services.analysis_service import AnalysisService
from app.services.export_service import rows_to_csv
from app.services.region_service import RegionService

router = APIRouter(prefix="/analysis", tags=["analysis"])


class ExportQuery(AnalysisQuery):
    kind: Literal["yearly", "events"] = "yearly"


def _run_analysis(query: AnalysisQuery, regions: RegionService, analysis: AnalysisService) -> dict:
    region = regions.resolve(query)
    result = analysis.analyze(query.hazard, region.lat, region.lon, query.start_year, query.end_year,
                              query.percentile, query.min_duration, query.method)
    return {**result, "region": region.to_dict()}


@router.get("", response_model=AnalysisResponse, summary="Analyse a hazard for a region and period")
def get_analysis(
    response: Response,
    query: Annotated[AnalysisQuery, Query()],
    regions: Annotated[RegionService, Depends(get_region_service)],
    analysis: Annotated[AnalysisService, Depends(get_analysis_service)],
):
    result = _run_analysis(query, regions, analysis)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return result


@router.get("/export", summary="Download yearly statistics or events as CSV")
def export_analysis(
    query: Annotated[ExportQuery, Query()],
    regions: Annotated[RegionService, Depends(get_region_service)],
    analysis: Annotated[AnalysisService, Depends(get_analysis_service)],
):
    result = _run_analysis(query, regions, analysis)
    rows = result["yearly"] if query.kind == "yearly" else result["events"]
    filename = f'{result["hazard"]}_{query.kind}.csv'
    return Response(rows_to_csv(rows), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
