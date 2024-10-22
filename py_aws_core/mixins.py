from py_aws_core.encoders import JsonEncoder


class AsDictMixin:
    """
    Converts
    """
    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class JsonMixin:
    @property
    def to_json(self):
        return JsonEncoder().serialize_to_json(self)
