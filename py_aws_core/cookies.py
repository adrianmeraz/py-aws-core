from http.cookies import SimpleCookie


class CookieUtil:
    @classmethod
    def build_set_cookie_header(
        cls,
        name: str,
        domain: str,
        value: str,
        path: str,
        expires_in_seconds: int,
        is_secure: bool = True,
        is_httponly: bool = False,
    ) -> str:
        cookie = SimpleCookie()
        cookie[name] = value
        cookie[name]['domain'] = domain
        cookie[name]['path'] = path
        cookie[name]['expires'] = expires_in_seconds
        cookie[name]['secure'] = is_secure
        cookie[name]['httponly'] = is_httponly

        return cookie.output(header='', sep='\015\012').strip()
