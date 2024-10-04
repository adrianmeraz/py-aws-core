import json
import typing

from . import cookies, exceptions, logs, utils

logger = logs.get_logger()


class LambdaEvent:
    class MultiValueHeaders:
        def __init__(self, data: dict):
            self.accept = self.get_first_element(data, 'Accept')
            self.accept_encoding = self.get_first_element(data, 'Accept-Encoding')
            self.authorization = self.get_first_element(data, 'Authorization')
            self._cookies = data.get('Cookie')
            self.user_agent = self.get_first_element(data, 'User-Agent')

        @property
        def cookies(self) -> typing.Dict:
            if not self._cookies:
                return dict()
            val = dict()
            for part in self._cookies[0].split(';'):
                k, v = part.strip().split('=')
                val[k] = v
            return val

        @staticmethod
        def get_first_element(items: dict, key: str) -> typing.AnyStr | None:
            if vals := items.get(key):
                return vals[0]
            return None

    class RequestContext:
        def __init__(self, data):
            self.resource_id = data['resourceId']
            self.resource_path = data['resourcePath']
            self.http_method = data['httpMethod']
            self.request_time = data['requestTime']
            self.path = data['path']
            self.domain_name = data['domainName']

    def __init__(self, data):
        self._body = data['body']
        self.headers = data['headers'] or dict()
        self.http_method = data['httpMethod']
        self.multi_value_headers = self.MultiValueHeaders(data['multiValueHeaders'])
        self.multi_value_query_string_parameters = data['multiValueQueryStringParameters']
        self.path = data['path']
        self.query_string_parameters = data['queryStringParameters'] or dict()
        self.request_context = self.RequestContext(data['requestContext'])

    @property
    def body(self):
        if self._body:
            return json.loads(utils.remove_whitespace(self._body))
        return self._body

    @property
    def cookies(self) -> typing.Dict:
        return self.multi_value_headers.cookies

    @property
    def lower_headers(self) -> typing.Dict:
        return {k.lower(): v for k, v in self.headers.items()}

    def get_cookie(self, cookie_name: str):
        if cookie := self.cookies.get(cookie_name):
            logger.info(f'Cookie "{cookie_name}" found', cookie=cookie)
            return cookie
        raise exceptions.MissingCookieException(missing_cookie=cookie_name)

    def generate_cookie_header(self, name: str, value: str, expires_in_seconds: int) -> str:
        return cookies.CookieUtil.build_set_cookie_header(
            name=name,
            domain=self.request_context.domain_name,
            value=value,
            path='/',
            expires_in_seconds=expires_in_seconds
        )
