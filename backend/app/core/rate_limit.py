from fastapi import Request
from slowapi import Limiter

from app.core.config import get_settings


def client_ip(request: Request) -> str:
    """Behind Render / Cloud Run the real client is the first X-Forwarded-For entry."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=client_ip, default_limits=[get_settings().rate_limit])
