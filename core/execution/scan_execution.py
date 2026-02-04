# core/execution/scan_execution.py




from core.engine.packet_sniffer import PacketSniffer
from core.telemetry.session import TelemetrySession
from core.telemetry.analyzer import TelemetryAnalyzer


class ScanExecution:
    """
    ScanExecution
    -------------
    - Orquesta la ejecución del engine
    - Controla lifecycle del packet sniffer
    - Adjunta telemetría al ScanResult (si está disponible)
    """

    def __init__(self, context, engine, profile):
        self.context = context
        self.engine = engine
        self.profile = profile

    def run(self):
        sniffer = PacketSniffer(
            target=self.context.target,
            iface=self.context.interface,
            mode=self.engine.name()
        )

        result = None
        telemetry_stats = None

        # --- Lifecycle seguro del sniffer ---
        sniffer.start()
        try:
            # Ejecutar engine (ffuf, nmap, etc.)
            result = self.engine.run(self.context, self.profile)

        finally:
            # El sniffer SIEMPRE debe detenerse
            sniffer.stop()

        # --- Telemetría: best-effort, nunca fatal ---
        try:
            telemetry = TelemetrySession(sniffer)
            telemetry_stats = TelemetryAnalyzer(telemetry).analyze()
        except Exception:
            # La telemetría NO puede romper el scan
            telemetry_stats = None

        # Adjuntar telemetría solo si existe
        if result is not None:
            result.traffic = telemetry_stats

        return result
