import logging

from httpx import Client

from py_aws_core import decorators
from . import exceptions

logger = logging.getLogger(__name__)

ROOT_URL = 'http://api.proxyrack.net'


STATUS_ERRORS_MAP = {
    407: exceptions.ProxyNotAuthenticated,
    560: exceptions.GeoLocationNotFound,
    561: exceptions.ProxyUnreachable,
    562: exceptions.ProxyNotFound,
    564: exceptions.ProxyNotOnline
}


class GetActiveConnections:
    class Response:
        class Connection:
            def __init__(self, data):
                self.create_time = data['createTime']
                self.dest_addr = data['destAddr']
                self.source_addr = data['sourceAddr']

        def __init__(self, data):
            self.connections = [self.Connection(c) for c in data]

    @classmethod
    @decorators.wrap_exceptions(raise_as=exceptions.ProxyRackException)
    def call(cls, client: Client, *args, **kwargs):
        url = f'{ROOT_URL}/active_conns'
        r = client.get(url=url, *args, **kwargs)
        r.raise_for_status()
        return cls.Response(r.json())


class GetCities:
    class Response:
        def __init__(self, data):
            self.cities = data

    @classmethod
    @decorators.wrap_exceptions(raise_as=exceptions.ProxyRackException)
    def call(cls, client: Client, *args, **kwargs):
        url = f'{ROOT_URL}/cities'
        r = client.get(url=url, *args, **kwargs)
        r.raise_for_status()
        return cls.Response(r.json())


class GetCountries:
    class Response:
        def __init__(self, data):
            self.countries = data

    @classmethod
    @decorators.wrap_exceptions(raise_as=exceptions.ProxyRackException)
    def call(cls, client: Client, *args, **kwargs):
        url = f'{ROOT_URL}/countries'
        r = client.get(url=url, *args, **kwargs)
        r.raise_for_status()
        return cls.Response(r.json())


class GetISPs:
    class Response:
        def __init__(self, data):
            self.isps = data

    @classmethod
    @decorators.wrap_exceptions(raise_as=exceptions.ProxyRackException)
    def call(cls, client: Client, country: str, *args, **kwargs):
        url = f'{ROOT_URL}/countries/{country}/isps'
        r = client.get(url=url, *args, **kwargs)
        r.raise_for_status()
        return cls.Response(r.json())


class GetCountryIPCount:
    @classmethod
    @decorators.wrap_exceptions(raise_as=exceptions.ProxyRackException)
    def call(cls, client: Client, country: str, *args, **kwargs):
        url = f'{ROOT_URL}/countries/{country}/count'
        r = client.get(url=url, *args, **kwargs)
        r.raise_for_status()
        return r.text


class GetTempAPIKey:
    class Response:
        class Password:
            def __init__(self, data):
                self.expiration_seconds = data['expirationSeconds']
                self.password = data['password']

        def __init__(self, data):
            self.password = self.Password(data['password'])
            self.success = data['success']

        @property
        def api_key(self):
            return self.password.password

    @classmethod
    @decorators.wrap_exceptions(raise_as=exceptions.ProxyRackException)
    def call(cls, client: Client, expiration_seconds: int, *args, **kwargs):
        url = f'{ROOT_URL}/passwords'

        params = {
            'expirationSeconds': expiration_seconds,
        }

        r = client.post(url=url, params=params, *args, **kwargs)
        r.raise_for_status()
        return cls.Response(r.json())


class GetStats:
    class Response:
        class IPInfo:
            class Fingerprint:
                def __init__(self, data):
                    self.osName = data['osName']

            def __init__(self, data):
                self.city = data['city']
                self.country = data['country']
                self.fingerprint = self.Fingerprint(data['fingerprint'])
                self.ip = data['ip']
                self.isp = data['isp']
                self.online = data['online']
                self.proxyId = data.get('proxyId')

        def __init__(self, data):
            self.ipinfo = self.IPInfo(data['ipinfo'])
            self.thread_limit = data['threadLimit']

    @classmethod
    @decorators.wrap_exceptions(raise_as=exceptions.ProxyRackException)
    def call(cls, client: Client, *args, **kwargs):
        """
            Gets statistics of current proxy
            Note: An endpoint must be hit first, or data will be blank
            :param client:
            :param args:
            :param kwargs:
            :return:
        """

        url = f'{ROOT_URL}/stats'
        r = client.get(url=url, *args, **kwargs)
        r.raise_for_status()
        return cls.Response(r.json())
