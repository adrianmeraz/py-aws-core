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
        cookie[name]['expires'] = cls.get_expiry_timestamp(expires_in_seconds)
        return cookie.output(header="Set-Cookie:", sep="\015\012")

    @classmethod
    def get_expiry_timestamp(cls, expire_in_seconds: int) -> str:
        dt = utils.add_seconds_to_now_datetime(seconds=expire_in_seconds)
        return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
