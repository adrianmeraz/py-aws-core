import json
from . import logs

logger = logs.logger


class DBEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif attrs := getattr(obj, '__dict__', None):  # Omit any non-public attributes
            return {k: v for k, v in attrs.items() if '__' not in k}
        else:
            try:
                super().default(obj)
            except TypeError:
                logger.exception(f'"{obj}" is not JSON serializable')
                raise

    @classmethod
    def serialize_to_json(cls, obj):
        return json.dumps(obj, cls=cls, separators=(',', ':'), ensure_ascii=False)
