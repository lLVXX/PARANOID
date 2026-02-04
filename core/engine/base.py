# core/engine/base.py

from abc import ABC, abstractmethod


class ScanEngine(ABC):
    """
    ScanEngine
    ----------
    Contrato base para todos los engines de escaneo.
    """

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def supports(self, scan_type: str) -> bool:
        pass

    @abstractmethod
    def run(self, context):
        pass


# Alias para compatibilidad semántica
BaseEngine = ScanEngine
