from typing import Literal, Optional

from pydantic import BaseModel

RegionKind = Literal["city", "state"]


class RegionOption(BaseModel):
    id: str
    name: str
    state: Optional[str] = None
    lat: float
    lon: float
