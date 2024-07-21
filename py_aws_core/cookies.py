from http.cookiejar import Cookie
from http.cookies import SimpleCookie

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
    expires_unix: int
) -> str:
    c = SimpleCookie()
    c['name'] = name
    # c['domain'] = domain
    c['value'] = value
    # c['path'] = path
    # c['expires'] = utils.unix_timestamp_to_iso8601(expires_unix)
    return c.output(header="Set-Cookie:", sep="\015\012")
