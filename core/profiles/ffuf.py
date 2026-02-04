#core/profiles/ffuf.py

from .base import ScanProfile

FFUF_PROFILE = ScanProfile(
    name="ffuf",
    window_size=5,
    mode="sustained",
    focus=[
        "http_rate",
        "status_codes",
        "response_size",
        "latency_shift"
    ]
)
