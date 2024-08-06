class SpoofingException(Exception):
    ERROR_MESSAGE = 'A generic spoofing error has occurred'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.ERROR_MESSAGE


class TwoCaptchaException(SpoofingException):
    ERROR_MESSAGE = 'A 2Captcha Error has occurred'


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
