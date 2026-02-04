# core/telemetry/analyzer.py

class TelemetryAnalyzer:
    """
    TelemetryAnalyzer
    -----------------
    Aplica métricas derivadas sobre un snapshot ya saneado.
    """

    def __init__(self, session):
        self.session = session

    def analyze(self) -> dict:
        stats = self.session.snapshot()

        # Punto único de salida
        return stats
