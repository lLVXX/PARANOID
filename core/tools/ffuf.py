#core/tools/ffuf.py
from .base import ToolAdapter
from core.profiles.ffuf import FFUF_PROFILE

class FfufTool(ToolAdapter):
    def __init__(self, cmd):
        super().__init__(cmd, FFUF_PROFILE)
