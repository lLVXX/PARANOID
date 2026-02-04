
#core/profiles/ffuf/model.py


from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class FFUFProfile:
    name: str
    threads: int
    timeout: int
    match_codes: List[int]
    filter_size: int
