#core/session/manager.py
import os
import json
import shutil
from datetime import datetime
from typing import Optional, List

from core.session.session import Session
from core.results.writer import ResultWriter


class SessionManager:
    """
    SessionManager
    ----------------
    - Mantiene la sesión activa
    - Garantiza sesión GLOBAL (por fecha)
    - Carga y persiste meta.json correctamente
    - Orquesta escritura de resultados
    """

    BASE_DIR = "results/SESSION"

    # --------------------------------------------------
    # INIT
    # --------------------------------------------------

    def __init__(self):
        self.writer = ResultWriter()
        self.current: Optional[Session] = None
        self.session_dir: Optional[str] = None

        self.ensure_global()

    # --------------------------------------------------
    # GLOBAL SESSION
    # --------------------------------------------------

    def ensure_global(self):
        """
        Garantiza sesión GLOBAL del día.
        CARGA meta.json si existe (NO reinicia estado).
        """
        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(self.BASE_DIR, "global", today)
        meta_path = os.path.join(path, "meta.json")

        os.makedirs(path, exist_ok=True)

        if os.path.isfile(meta_path):
            with open(meta_path, "r") as f:
                data = json.load(f)
            self.current = Session.from_dict(data)
        else:
            self.current = Session(name="global", is_global=True)

        self.session_dir = path
        self._write_meta()

    # --------------------------------------------------
    # SESSION CONTROL
    # --------------------------------------------------

    def create(self, name: str):
        self.current = Session(name=name, is_global=False)
        self.session_dir = os.path.join(self.BASE_DIR, name)

        os.makedirs(self.session_dir, exist_ok=True)
        self._write_meta()

    def activate(self, name: str):
        if name == "global":
            self.ensure_global()
            return

        path = os.path.join(self.BASE_DIR, name)
        meta_path = os.path.join(path, "meta.json")

        if not os.path.isdir(path):
            raise RuntimeError(f"La sesión '{name}' no existe")

        if os.path.isfile(meta_path):
            with open(meta_path, "r") as f:
                data = json.load(f)
            self.current = Session.from_dict(data)
        else:
            self.current = Session(name=name, is_global=False)

        self.session_dir = path
        self._write_meta()

    def close_current(self) -> bool:
        if not self.current:
            self.ensure_global()
            return True

        if self.current.is_protected():
            return False

        self.ensure_global()
        return True

    def close(self):
        return self.close_current()

    def delete(self, name: str) -> bool:
        if name == "global":
            return False

        path = os.path.join(self.BASE_DIR, name)
        if not os.path.isdir(path):
            return False

        if self.current and self.current.name == name:
            self.ensure_global()

        shutil.rmtree(path)
        return True

    # --------------------------------------------------
    # INFO
    # --------------------------------------------------

    def list_sessions(self) -> List[str]:
        if not os.path.isdir(self.BASE_DIR):
            return ["global"]

        sessions = [
            d for d in os.listdir(self.BASE_DIR)
            if os.path.isdir(os.path.join(self.BASE_DIR, d))
        ]

        if "global" not in sessions:
            sessions.append("global")

        return sorted(sessions)

    def get_active_name(self) -> str:
        return self.current.name if self.current else "global"

    def get_session_info(self) -> dict:
        if not self.current:
            return {}

        return self.current.to_dict()

    # --------------------------------------------------
    # METADATA
    # --------------------------------------------------

    def _write_meta(self):
        if not self.current or not self.session_dir:
            return

        meta_path = os.path.join(self.session_dir, "meta.json")
        with open(meta_path, "w") as f:
            json.dump(self.current.to_dict(), f, indent=4)

    # --------------------------------------------------
    # TARGET HANDLING
    # --------------------------------------------------

    def register_target(self, target: str):
        if not self.current:
            raise RuntimeError("No hay sesión activa")

        self.current.register_target(target)
        self._write_meta()

    # -------------------- NEW -------------------------

    def delete_target(self, target: str) -> bool:
        """
        Elimina un target de la sesión activa y
        borra todos sus resultados asociados.
        """
        if not self.current or not self.session_dir:
            return False

        if self.current.is_protected():
            return False

        removed = self.current.delete_target(target)
        if not removed:
            return False

        # borrar resultados en disco
        for item in os.listdir(self.session_dir):
            if item.startswith(f"{target}-"):
                shutil.rmtree(
                    os.path.join(self.session_dir, item),
                    ignore_errors=True
                )

        self._write_meta()
        return True

    # --------------------------------------------------
    # RESULT PERSISTENCE
    # --------------------------------------------------

    def save_result(self, scan_result):
        if not self.current or not self.session_dir:
            return

        meta = scan_result.metadata
        target = meta.get("target", "unknown")
        scan_type = meta.get("scan_type", "unknown")

        self.current.register_target(target)
        self.current.register_scan(target, scan_type)

        timestamp = datetime.now().strftime("%H%M%S")
        result_path = os.path.join(
            self.session_dir,
            f"{target}-{timestamp}"
        )

        os.makedirs(result_path, exist_ok=True)

        self.writer.write(
            scan_result=scan_result,
            output_dir=result_path
        )

        self._write_meta()

    # --------------------------------------------------
    # BACKWARD COMPATIBILITY
    # --------------------------------------------------

    @classmethod
    def get_global(cls):
        return cls()

