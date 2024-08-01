import json
import typing

from py_aws_core import utils


class LambdaEvent:
    class MultiValueHeaders:
        def __init__(self, data: dict):
            self.accept = data['Accept'][0]
            self.accept_encoding = data['Accept-Encoding'][0]
            self._authorization = data.get('Authorization')
            self._cookies = data.get('Cookie')
            self.user_agent = data['User-Agent'][0]

        @property
        def authorization(self):
            if self._authorization:
                return self._authorization[0]
            return None

        @property
        def cookies(self) -> typing.Dict:
            if not self._cookies:
                return dict()
            val = dict()
            for part in self._cookies[0].split(';'):
                k, v = part.strip().split('=')
                val[k] = v
            return val

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
