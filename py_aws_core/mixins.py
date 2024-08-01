from py_aws_core.encoders import DBEncoder


class JsonMixin:
    @property
    def to_json(self):
        return DBEncoder().serialize_to_json(self)
