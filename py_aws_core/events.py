import json
import typing


class LambdaEvent:
    class RequestContext:
        def __init__(self, data):
            self.resourceId = ['resourceId']
            self.resourcePath = ['resourcePath']
            self.httpMethod = ['httpMethod']
            self.requestTime = ['requestTime']
            self.path = ['path']
            self.domainName = ['domainName']

    def __init__(self, data):
        self.headers = data['headers'] or dict()
        self.httpMethod = data['httpMethod']
        self.path = data['path']
        self.queryStringParameters = data['queryStringParameters'] or dict()
        self._body = data['body']
        self.requestContext = self.RequestContext(data['requestContext'])

    @property
    def body(self):
        if self._body:
            return json.loads(self._body)
        return self._body

    @property
    def lower_headers(self) -> typing.Dict:
        return {k.lower(): v for k, v in self.headers.items()}
