from http.cookies import SimpleCookie

from . import utils


class CookieUtil:
    HEADER_NAME = 'Set-Cookie:'

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

        output = cookie.output(header=cls.HEADER_NAME, sep='\015\012')
        return output.split(cls.HEADER_NAME)[1].strip()

