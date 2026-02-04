#core/profiles/ffuf/resolver.py

from core.profiles.ffuf.default import DEFAULT_FFUF_PROFILE
from core.profiles.ffuf.model import FFUFProfile

def resolve_ffuf_profile(profile):
    if profile is None:
        return DEFAULT_FFUF_PROFILE

    if isinstance(profile, FFUFProfile):
        return profile

    raise ValueError(f"Perfil FFUF inválido: {profile}")
