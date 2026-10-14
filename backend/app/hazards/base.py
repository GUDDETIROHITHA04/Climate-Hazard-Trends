"""Common contract for every hazard (strategy pattern).

Adding a new hazard = one new module with a `Hazard` subclass + one line in registry.py.
Nothing in the service or API layers has to change.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace

import pandas as pd


@dataclass(frozen=True)
class EventColumn:
    key: str
    label: str


@dataclass(frozen=True)
class HazardSpec:
    """Static description of a hazard: what to fetch and how to label results."""

    key: str
    name: str
    variable: str  # Open-Meteo daily variable
    noun: str  # "heatwave days"
    unit: str  # "days" | "months"
    event_word: str
    primary_label: str
    events_label: str
    longest_label: str
    intensity_label: str
    intensity_short: str
    event_columns: tuple[EventColumn, ...]
    caveats: tuple[str, ...]
    lookback_years: int = 0  # extra years of data needed before the first analysed year


@dataclass(frozen=True)
class DetectionParams:
    start_year: int
    end_year: int
    percentile: float
    min_duration: int
    method: str
    baseline_start: int
    baseline_end: int

    def with_changes(self, **changes) -> "DetectionParams":
        return replace(self, **changes)


@dataclass
class DetectionResult:
    events: list[dict] = field(default_factory=list)
    yearly: list[dict] = field(default_factory=list)
    definition: dict = field(default_factory=dict)


class Hazard(ABC):
    spec: HazardSpec

    @abstractmethod
    def normalise(self, params: DetectionParams) -> DetectionParams:
        """Validate parameters and reset the ones that do not apply (so equal requests share one cache entry)."""

    @abstractmethod
    def clean(self, dates, values) -> tuple[pd.Series, dict]:
        """Turn raw provider values into a clean daily series + a data-quality report."""

    @abstractmethod
    def detect(self, series: pd.Series, params: DetectionParams) -> DetectionResult:
        """Detect events and aggregate them per year."""
