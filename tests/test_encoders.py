import json
from importlib.resources import as_file
from unittest import TestCase
from decimal import Decimal

from py_aws_core import encoders
from tests import const as test_const


class DBEncoderTests(TestCase):
    def test_serialize_to_json(self):
        source = test_const.TEST_DB_RESOURCES_PATH.joinpath('get_items.json')
        with as_file(source) as entities_json:
            to_json = encoders.DBEncoder().serialize_to_json(json.loads(entities_json.read_text(encoding='utf-8')))
            self.assertEqual(to_json, '[{"disabled":false,"group":null,"selected":false,"text":"BOGOTA D.C (BOG), AEROPUERTO EL DORADO","value":"1"},{"disabled":false,"group":null,"selected":false,"text":"CARTAGENA (CTG), AEROPUERTO RAFAEL NUÑEZ","value":"18"},{"disabled":false,"group":null,"selected":false,"text":"MEDELLIN (MDE), AEROPUERTO JOSE MARIA CORDOVA","value":"12"},{"disabled":false,"group":null,"selected":false,"text":"PEREIRA (PEI), AEROPUERTO MATECAÑA","value":"15"},{"disabled":false,"group":null,"selected":false,"text":"RIOHACHA (RCH), AEROPUERTO ALMIRANTE PADILLA","value":"76"},{"disabled":false,"group":null,"selected":false,"text":"SAN ANDRES (ADZ) AEROPUERTO GUSTAVO ROJAS PINILLA","value":"16"}]')

    def test_decimal_unserializable(self):
        val = Decimal(12.99)
        to_json = encoders.DBEncoder().serialize_to_json(val)
        self.assertEqual(to_json, "")
