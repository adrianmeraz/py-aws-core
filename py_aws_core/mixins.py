from dataclasses import asdict, dataclass

from py_aws_core.encoders import JsonEncoder


@dataclass
class AsDictMixin:
    def as_dict(self):
        return asdict(self)


class JsonMixin:
    @property
    def to_json(self):
        return JsonEncoder().serialize_to_json(self)
