from py_aws_core.encoders import JsonEncoder


class JsonMixin:
    @property
    def to_json(self):
        return JsonEncoder().serialize_to_json(self)
