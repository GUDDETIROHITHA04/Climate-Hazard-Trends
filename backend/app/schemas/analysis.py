"""Request and response models. They validate input and generate the OpenAPI docs."""
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

HazardKey = Literal["heatwave", "heavy_rainfall", "drought"]
ThresholdMethod = Literal["daily", "annual"]

PLACE_NAME_PATTERN = r"^[\w\s.,'\-]{2,80}$"
MAX_BOX_DEGREES = 5.0


class AnalysisQuery(BaseModel):
    """Query string of GET /analysis. Exactly one region mode must be used: city | lat+lon | box."""

    model_config = ConfigDict(extra="forbid")

    hazard: HazardKey = "heatwave"

    city: Optional[str] = Field(None, min_length=2, max_length=80, pattern=PLACE_NAME_PATTERN)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    south: Optional[float] = Field(None, ge=-90, le=90)
    west: Optional[float] = Field(None, ge=-180, le=180)
    north: Optional[float] = Field(None, ge=-90, le=90)
    east: Optional[float] = Field(None, ge=-180, le=180)
    label: Optional[str] = Field(None, max_length=80)

    start_year: int = Field(1991, ge=1950, le=2100)
    end_year: int = Field(2020, ge=1950, le=2100)
    percentile: float = Field(95.0, ge=80, le=99.5)
    min_duration: int = Field(3, ge=1, le=14, description="Days (heatwave, heavy rainfall) or months (drought)")
    method: ThresholdMethod = "daily"

    @property
    def region_mode(self) -> str:
        if self.city is not None:
            return "city"
        if self.lat is not None or self.lon is not None:
            return "point"
        return "box"

    @model_validator(mode="after")
    def validate_region_and_years(self) -> "AnalysisQuery":
        box = (self.south, self.west, self.north, self.east)
        modes = [self.city is not None, self.lat is not None or self.lon is not None, any(v is not None for v in box)]
        if sum(modes) != 1:
            raise ValueError("Provide exactly one of: city, lat+lon, or south+west+north+east")
        if modes[1] and (self.lat is None or self.lon is None):
            raise ValueError("Both lat and lon are required")
        if modes[2]:
            if any(v is None for v in box):
                raise ValueError("south, west, north and east are all required for a box")
            if not (self.south < self.north and self.west < self.east):
                raise ValueError("Box must satisfy south < north and west < east")
            if self.north - self.south > MAX_BOX_DEGREES or self.east - self.west > MAX_BOX_DEGREES:
                raise ValueError(f"Box too large: at most {MAX_BOX_DEGREES}° per side")
        if self.start_year >= self.end_year:
            raise ValueError("start_year must be before end_year")
        return self


class BoundingBox(BaseModel):
    south: float
    west: float
    north: float
    east: float


class RegionInfo(BaseModel):
    label: str
    lat: float
    lon: float
    type: Literal["city", "point", "box"]
    bbox: Optional[BoundingBox] = None


class EventColumnModel(BaseModel):
    key: str
    label: str


class HazardMeta(BaseModel):
    key: str
    name: str
    noun: str
    unit: str
    event_word: str
    primary_label: str
    events_label: str
    longest_label: str
    intensity_label: str
    intensity_short: str
    event_columns: list[EventColumnModel]


class TrendPoint(BaseModel):
    year: int
    value: float


class TrendResult(BaseModel):
    ok: bool
    n: int
    reason: Optional[str] = None
    direction: Optional[str] = None
    significant: Optional[bool] = None
    mk_tau: Optional[float] = None
    mk_p: Optional[float] = None
    sen_slope_per_decade: Optional[float] = None
    sen_ci_per_decade: Optional[list[float]] = None
    ols_slope_per_decade: Optional[float] = None
    ols_p: Optional[float] = None
    fitted_start: Optional[float] = None
    fitted_end: Optional[float] = None
    pct_change_fitted: Optional[float] = None
    first_period_mean: Optional[float] = None
    last_period_mean: Optional[float] = None
    period_len: Optional[int] = None
    line: Optional[list[TrendPoint]] = None


class YearlyRecord(BaseModel):
    year: int
    coverage: float
    reliable: bool
    primary: int
    events: int
    longest: int
    mean_duration: Optional[float] = None
    intensity: float
    rolling: Optional[float] = None


class Definition(BaseModel):
    text: str
    sanity: str


class DataQuality(BaseModel):
    days: int
    missing_raw: int
    outliers_removed: int
    interpolated_days: int
    missing_after_cleaning: int
    coverage_pct: float
    years_excluded: list[int]
    notes: list[str]


class Insights(BaseModel):
    headline: str
    bullets: list[str]
    caveats: list[str]


class AnalysisParams(BaseModel):
    start_year: int
    end_year: int
    percentile: float
    min_duration: int
    method: str
    baseline: list[int]


class ResponseMeta(BaseModel):
    source: str
    cache_hit: bool
    computed_at: str


class GridCell(BaseModel):
    lat: float
    lon: float


class AnalysisResponse(BaseModel):
    hazard: HazardKey
    hazard_meta: HazardMeta
    region: RegionInfo
    grid: GridCell
    params: AnalysisParams
    definition: Definition
    data_quality: DataQuality
    yearly: list[YearlyRecord]
    events: list[dict[str, Any]]
    trends: dict[str, TrendResult]
    insights: Insights
    meta: ResponseMeta
