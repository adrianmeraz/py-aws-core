from http.cookies import SimpleCookie

from . import utils


class CookieUtil:
    @classmethod
    def build_set_cookie_header(
        cls,
        name: str,
        domain: str,
        value: str,
        path: str,
        expires_in_seconds: int
    ) -> str:
        cookie = SimpleCookie()
        cookie[name] = value
        cookie[name]['domain'] = domain
        cookie[name]['path'] = path
        cookie[name]['expires'] = expires_in_seconds

        return cookie.output(header='', sep='\015\012').strip()
