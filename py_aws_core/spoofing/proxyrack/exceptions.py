from py_aws_core.spoofing.exceptions import SpoofingException


class ProxyRackException(SpoofingException):
    ERROR_MESSAGE = 'A ProxyRack Error has occurred'


class ProxyNotAuthenticated(ProxyRackException):
    ERROR_MESSAGE = 'ProxyRack Proxy Not Authenticated'


class GeoLocationNotFound(ProxyRackException):
    ERROR_MESSAGE = 'ProxyRack Geolocation Not Found'


class ProxyUnreachable(ProxyRackException):
    ERROR_MESSAGE = 'ProxyRack Proxy Unreachable'


class ProxyNotFound(ProxyRackException):
    ERROR_MESSAGE = 'ProxyRack Proxy Not Found'


class ProxyNotOnline(ProxyRackException):
    ERROR_MESSAGE = 'ProxyRack Proxy Not Online'
