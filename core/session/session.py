#core/session/session.py

from datetime import datetime
from typing import List, Dict, Set, Optional


class Session:
    """
    Session
    -------
    Representa una sesión de trabajo.

    REGLAS:
    - NO ejecuta scans
    - NO escribe en disco
    - NO conoce engines
    - NO conoce ScanContext

    Mantiene:
    - targets
    - target activo (por índice)
    - historial de scans
    - hostnames HTTP inferidos / confirmados
    """

    def __init__(
        self,
        name: str,
        is_global: bool = False,
        interface: str = "tun0"
    ):
        self.name: str = name
        self.is_global: bool = is_global
        self.interface: str = interface or "tun0"
        self.created_at: str = datetime.utcnow().isoformat()

        # Targets
        self.targets: List[str] = []
        self.active_target_index: Optional[int] = None

        # Historial de scans
        self.scans: List[Dict[str, str]] = []

        # HTTP intelligence
        # {
        #   target: {
        #       "confirmed": set(),
        #       "inferred": set()
        #   }
        # }
        self.http_hosts: Dict[str, Dict[str, Set[str]]] = {}

    # --------------------------------------------------
    # INTERFACE
    # --------------------------------------------------

    def set_interface(self, interface: str):
        if interface:
            self.interface = interface

    # --------------------------------------------------
    # TARGETS
    # --------------------------------------------------

    def register_target(self, target: str):
        if target not in self.targets:
            self.targets.append(target)
            self.http_hosts.setdefault(
                target,
                {"confirmed": set(), "inferred": set()}
            )

            # Primer target pasa a ser activo automáticamente
            if self.active_target_index is None:
                self.active_target_index = 0

    def remove_target(self, target: str) -> bool:
        """
        Elimina completamente un target de la sesión:
        - target
        - scans asociados
        - hostnames HTTP asociados
        """
        if target not in self.targets:
            return False

        idx = self.targets.index(target)

        self.targets.remove(target)
        self.http_hosts.pop(target, None)

        self.scans = [
            s for s in self.scans
            if s.get("target") != target
        ]

        # Ajustar target activo
        if self.active_target_index is not None:
            if idx == self.active_target_index:
                self.active_target_index = 0 if self.targets else None
            elif idx < self.active_target_index:
                self.active_target_index -= 1

        return True

    def get_active_target(self) -> Optional[str]:
        if self.active_target_index is None:
            return None
        if self.active_target_index >= len(self.targets):
            return None
        return self.targets[self.active_target_index]

    def set_active_target(self, index: int) -> bool:
        if index < 0 or index >= len(self.targets):
            return False
        self.active_target_index = index
        return True

    # --------------------------------------------------
    # SCANS
    # --------------------------------------------------

    def register_scan(self, target: str, scan_type: str):
        self.register_target(target)

        self.scans.append({
            "target": target,
            "scan_type": scan_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # --------------------------------------------------
    # HTTP HOSTNAMES
    # --------------------------------------------------

    def add_http_hostnames(
        self,
        target: str,
        hostnames: List[str],
        confirmed: bool = False
    ):
        """
        Registra hostnames HTTP descubiertos o inferidos.
        """
        self.register_target(target)

        bucket = "confirmed" if confirmed else "inferred"
        self.http_hosts[target][bucket].update(hostnames)

    def get_http_hostnames(self, target: str) -> List[str]:
        data = self.http_hosts.get(target)
        if not data:
            return []

        return sorted(data["confirmed"]) + sorted(data["inferred"])

    def has_http_hostnames(self, target: str) -> bool:
        data = self.http_hosts.get(target)
        if not data:
            return False
        return bool(data["confirmed"] or data["inferred"])

    # --------------------------------------------------
    # SERIALIZACIÓN
    # --------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "session": self.name,
            "global": self.is_global,
            "interface": self.interface,
            "created_at": self.created_at,
            "targets": self.targets,
            "active_target_index": self.active_target_index,
            "scans": self.scans,
            "http_hosts": {
                t: {
                    "confirmed": list(v["confirmed"]),
                    "inferred": list(v["inferred"])
                }
                for t, v in self.http_hosts.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        s = cls(
            name=data.get("session", "unknown"),
            is_global=data.get("global", False),
            interface=data.get("interface", "tun0")
        )

        s.created_at = data.get("created_at", s.created_at)
        s.targets = data.get("targets", [])
        s.scans = data.get("scans", [])
        s.active_target_index = data.get("active_target_index")

        http_hosts = {}
        for target, info in data.get("http_hosts", {}).items():
            http_hosts[target] = {
                "confirmed": set(info.get("confirmed", [])),
                "inferred": set(info.get("inferred", []))
            }

        s.http_hosts = http_hosts

        return s


    # --------------------------------------------------
    # PROTECCIÓN
    # --------------------------------------------------

    def is_protected(self) -> bool:
        return self.is_global
