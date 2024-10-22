import typing


class ErrorResponse:
    class Error:
        def __init__(self, data):
            self.Message = data['Message']
            self.Code = data['Code']

    class CancellationReason:
        def __init__(self, data):
            self.Code = data['Code']
            self.Message = data.get('Message')

    def __init__(self, data):
        self.Error = self.Error(data.get('Error', dict()))
        self.ResponseMetadata = ResponseMetadata(data.get('ResponseMetadata', dict()))
        self.Message = data.get('Message')
        self.CancellationReasons = [self.CancellationReason(r) for r in data.get('CancellationReasons', list())]

    def raise_for_cancellation_reasons(self, error_maps: list[dict[str, typing.Any]]):
        for reason, error_map in zip(self.CancellationReasons, error_maps):
            if exc := error_map.get(reason.Code):
                raise exc


class ItemResponse:
    def __init__(self, data):
        self.Item = data.get('Item')
        self.ResponseMetadata = ResponseMetadata(data.get('ResponseMetadata', dict()))


class QueryResponse:
    def __init__(self, data):
        self._items = data.get('Items') or list()
        self.count = data.get('Count')
        self.scanned_count = data.get('ScannedCount')
        self.response_metadata = ResponseMetadata(data['ResponseMetadata'])

    def get_by_type(self, _type: str) -> list:
        if self._items:
            return [i for i in self._items if i['Type']['S'] == _type]
        return list()


class UpdateItemResponse:
    def __init__(self, data: dict):
        self.attributes = data['Attributes']


class TransactionResponse:
    def __init__(self, data):
        self._data = data
        self.Responses = data.get('Responses')

    @property
    def data(self):
        return self._data


class ResponseMetadata:
    class HTTPHeaders:
        def __init__(self, data):
            self.server = data.get('server')
            self.date = data.get('date')

    def __init__(self, data):
        self.RequestId = data.get('RequestId')
        self.HTTPStatusCode = data.get('HTTPStatusCode')
        self.HTTPHeaders = self.HTTPHeaders(data.get('HTTPHeaders', dict()))
        self.RetryAttempts = data.get('RetryAttempts')
