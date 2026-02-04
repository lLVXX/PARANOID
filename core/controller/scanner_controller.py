#core/controller/scanner_controller.py

from core.engine.scan_context import ScanContext
from core.registry.engines import get_engine
from core.session.manager import SessionManager
from core.execution.scan_execution import ScanExecution


class ScannerController:
    """
    ScannerController
    -----------------
    Orquestador de escaneos.

    RESPONSABILIDADES:
    - Construir ScanContext
    - Resolver engine adecuado
    - Orquestar ejecución (ScanExecution)
    - Delegar persistencia a SessionManager

    NO:
    - Guarda estado propio
    - Ejecuta lógica de engines
    - Maneja telemetría directamente
    """

    def __init__(self, session_manager: SessionManager | None = None):
        self.session_manager: SessionManager = (
            session_manager or SessionManager.get_global()
        )

    # --------------------------------------------------
    # INTERFAZ
    # --------------------------------------------------

    def set_interface(self, interface: str):
        """
        Define la interfaz activa en la sesión.
        """
        self.session_manager.set_interface(interface)

    # --------------------------------------------------
    # EJECUCIÓN
    # --------------------------------------------------

    def run_scan(self, target: str, scan_type: str, **kwargs):
        """
        Ejecuta un escaneo sobre un target.

        Flujo:
        1. Validar sesión activa
        2. Obtener interfaz desde sesión
        3. Construir ScanContext
        4. Resolver engine
        5. Ejecutar ScanExecution (telemetría + engine)
        6. Persistir resultado
        7. Retornar resultado
        """

        session = self.session_manager.current
        if not session:
            raise RuntimeError("No hay sesión activa")

        interface = session.interface

        # Registrar target en la sesión
        self.session_manager.register_target(target)

        # --------------------------------------------------
        # ❗ IMPORTANTE:
        # El controller NO decide protocolo.
        # HTTP/HTTPS será responsabilidad del engine
        # o de perfiles (futuro).
        # --------------------------------------------------

        # Construir ScanContext (MISMO CONTRATO)
        context = ScanContext(
            target=target,
            interface=interface,
            scan_type=scan_type,
            session=session.name,
            **kwargs
        )

        # Resolver engine
        engine = get_engine(scan_type)

        # Ejecutar ScanExecution (telemetría agnóstica)
        execution = ScanExecution(
            context=context,
            engine=engine,
            profile=scan_type  # compat temporal
        )

        result = execution.run()

        # Metadata mínima garantizada (MISMO OUTPUT)
        result.metadata.setdefault("target", target)
        result.metadata.setdefault("scan_type", scan_type)
        result.metadata.setdefault("interface", interface)
        result.metadata.setdefault("engine", engine.name())

        # Persistencia
        self.session_manager.save_result(result)

        return result
