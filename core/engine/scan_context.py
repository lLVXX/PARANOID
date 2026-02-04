# core/engine/scan_context.py

from datetime import datetime
from typing import Optional, Dict, Any


class ScanContext:
    """
    ScanContext
    -----------
    Describe UN escaneo.

    - Inmutable (por contrato, no forzado)
    - Efímero
    - Engine-agnostic
    - No persiste
    """

    def __init__(
        self,
        target: str,
        interface: str = "tun0",
        scan_type: Optional[str] = None,
        session: Optional[str] = None,

        # ---- execution params (engine-agnostic) ----
        protocol: Optional[str] = None,
        wordlist: Optional[str] = None,
        threads: Optional[int] = None,
        delay: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        extra: Optional[Dict[str, Any]] = None,

        # ---- HTTP / NETWORK CONTEXT (SAFE EXTENSIONS) ----
        hostname: Optional[str] = None,
        port: Optional[int] = None,
    ):
        # -----------------------------
        # Core identity
        # -----------------------------
        self.target = target
        self.interface = interface
        self.scan_type = scan_type
        self.session = session

        # -----------------------------
        # Execution parameters
        # -----------------------------
        self.protocol = protocol
        self.wordlist = wordlist
        self.threads = threads
        self.delay = delay
        self.headers = headers or {}
        self.extra = extra or {}

        # -----------------------------
        # HTTP / Network context
        # -----------------------------
        self.hostname = hostname
        self.port = port  # 👈 CRÍTICO para FFUF / HTTP engines

        # -----------------------------
        # Metadata
        # -----------------------------
        self.created_at = datetime.utcnow().isoformat()

    # --------------------------------------------------
    # Serialization (debug / logging / future persistence)
    # --------------------------------------------------

    def to_dict(self) -> dict:
        return {
            # Core
            "target": self.target,
            "interface": self.interface,
            "scan_type": self.scan_type,
            "session": self.session,

            # Execution
            "protocol": self.protocol,
            "wordlist": self.wordlist,
            "threads": self.threads,
            "delay": self.delay,
            "headers": self.headers,
            "extra": self.extra,

            # HTTP / Network (optional)
            "hostname": self.hostname,
            "port": self.port,

            # Metadata
            "created_at": self.created_at,
        }
