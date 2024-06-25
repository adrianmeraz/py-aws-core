import json


class DBEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif attrs := getattr(obj, '__dict__'):  # Omit any non-public attributes
            return {k: v for k, v in attrs.items() if '__' not in k}
        else:
            super().default(obj)

    @classmethod
    def serialize_to_json(cls, obj):
        return json.dumps(obj, cls=cls, separators=(',', ':'), ensure_ascii=False)
