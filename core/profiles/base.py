#core/profiles/base.py

class ScanProfile:
    def __init__(
        self,
        name,
        window_size,
        mode,
        focus
    ):
        self.name = name
        self.window_size = window_size   # segundos
        self.mode = mode                 # burst | sustained
        self.focus = focus               # qué métricas interesan
