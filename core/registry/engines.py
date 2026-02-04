#core/registry/engines.py

from core.engine.nmap_engine import NmapEngine
from core.engine.ffuf_engine import FFUFEngine 


ENGINES = [
    NmapEngine(),
    FFUFEngine(),
]

def get_engine(scan_type):
    for engine in ENGINES:
        if engine.supports(scan_type):
            return engine
    raise RuntimeError(f"No hay engine para '{scan_type}'")