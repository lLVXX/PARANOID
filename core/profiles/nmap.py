#core/profiles/nmap.py

from .base import ScanProfile

NMAP_PROFILE = ScanProfile(
    name="nmap",
    window_size=2,
    mode="burst",
    focus=[
        "syn",
        "rst",
        "rtt",
        "port_response"
    ]
)
