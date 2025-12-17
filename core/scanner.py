# core/scanner.py

import ipaddress

from core.scanner_discovery import DiscoveryScanner
from core.scanner_nmap import NmapScanner


class ScannerController:
    """
    Orquestador central de escaneo.
    NO escanea directamente.
    Decide qué scanner usar según el contexto.
    """

    def __init__(self):
        self.target = None
        self.interface = "tun0"

        self._nmap = NmapScanner()

    # ==================================================
    # CONTEXT SETTERS
    # ==================================================

    def set_target(self, target):
        self.target = target
        self._nmap.target = target

    def set_interface(self, interface):
        self.interface = interface
        self._nmap.interface = interface

    # ==================================================
    # CONTEXT HELPERS
    # ==================================================

    def _is_cidr(self):
        try:
            ipaddress.ip_network(self.target, strict=False)
            return True
        except Exception:
            return False

    def _is_lan_target(self):
        """
        Define si el target es potencialmente LAN
        (RFC1918 + CIDR)
        """
        try:
            net = ipaddress.ip_network(self.target, strict=False)
            return (
                net.is_private and
                "/" in self.target
            )
        except Exception:
            return False

    # ==================================================
    # DISCOVERY
    # ==================================================

    def discover(self):
        if not self.target:
            raise RuntimeError("No hay target definido")

        if not self._is_lan_target():
            raise RuntimeError(
                "Host discovery solo es válido para redes LAN (CIDR privado)"
            )

        scanner = DiscoveryScanner(
            target=self.target,
            interface=self.interface
        )

        return scanner.run()

    # ==================================================
    # NMAP SCANS (DELEGADOS)
    # ==================================================

    def scan_quick(self):
        self._require_target()
        self._nmap.quick_scan()

    def scan_full(self):
        self._require_target()
        self._nmap.full_scan()

    def scan_service(self):
        self._require_target()
        self._nmap.service_scan()

    def scan_stealth(self):
        self._require_target()
        self._nmap.stealth_scan()

    # ==================================================
    # VALIDATION
    # ==================================================

    def _require_target(self):
        if not self.target:
            raise RuntimeError("No hay target definido")
