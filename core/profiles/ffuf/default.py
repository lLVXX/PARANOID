#core/profiles/ffuf/default.py


from core.profiles.ffuf.model import FFUFProfile

DEFAULT_FFUF_PROFILE = FFUFProfile(
    name="default",
    threads=40,
    timeout=10,
    match_codes=[200, 204, 301, 302, 307, 401, 403],
    filter_size=0,
)

