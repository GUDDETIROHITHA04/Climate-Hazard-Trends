from app.core.exceptions import ValidationFailed
from app.hazards.base import Hazard
from app.hazards.drought import DroughtHazard
from app.hazards.heatwave import HeatwaveHazard
from app.hazards.heavy_rainfall import HeavyRainfallHazard

HAZARDS: dict[str, Hazard] = {h.spec.key: h for h in (HeatwaveHazard(), HeavyRainfallHazard(), DroughtHazard())}


def get_hazard(key: str) -> Hazard:
    try:
        return HAZARDS[key]
    except KeyError:
        raise ValidationFailed(f"Unknown hazard '{key}'") from None
