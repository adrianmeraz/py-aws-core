from http.cookiejar import Cookie
from http.cookies import SimpleCookie

import datetime

from . import utils


def build_set_cookie_header_value(
    name: str,
    domain: str,
    value: str,
    path: str,
    expires: int
) -> str:
    return str(Cookie(
        version=None,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=domain.startswith('.'),
        path=path,
        path_specified=path is not None,
        secure=True,
        expires=expires,
        discard=False,
        comment=None,
        comment_url=None,
        rest=dict(),
        rfc2109=False,
    ))


def build_set_cookie_header_value_2(
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
    expires = utils.add_seconds_to_now_datetime
    # cookie['session']['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return cookie.output(header="Set-Cookie:", sep="\015\012")
