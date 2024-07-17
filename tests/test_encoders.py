import json
from importlib.resources import as_file
from unittest import TestCase

from py_aws_core import encoders
from tests import const as test_const


class DBEncoderTests(TestCase):
    def test_serialize_to_json(self):
        source = test_const.TEST_DB_RESOURCES_PATH.joinpath('get_items.json')
        with as_file(source) as entities_json:
            val = encoders.DBEncoder().serialize_to_json(json.loads(entities_json.read_text()))
            self.assertEqual(val, 1062862408)
