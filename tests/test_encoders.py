import json
from decimal import Decimal
from importlib.resources import as_file

from py_aws_core import encoders
from py_aws_core.testing import BaseTestFixture


class JsonEncoderTests(BaseTestFixture):
    def test_serialize_to_json(self):
        source = self.TEST_DB_RESOURCES_PATH.joinpath('db#get_items.json')
        with as_file(source) as entities_json:
            to_json = encoders.JsonEncoder().serialize_to_json(json.loads(entities_json.read_text(encoding='utf-8')))
            self.assertEqual(to_json, '[{"disabled":false,"group":null,"selected":false,"text":"BOGOTA D.C (BOG), AEROPUERTO EL DORADO","value":"1"},{"disabled":false,"group":null,"selected":false,"text":"CARTAGENA (CTG), AEROPUERTO RAFAEL NUÑEZ","value":"18"},{"disabled":false,"group":null,"selected":false,"text":"MEDELLIN (MDE), AEROPUERTO JOSE MARIA CORDOVA","value":"12"},{"disabled":false,"group":null,"selected":false,"text":"PEREIRA (PEI), AEROPUERTO MATECAÑA","value":"15"},{"disabled":false,"group":null,"selected":false,"text":"RIOHACHA (RCH), AEROPUERTO ALMIRANTE PADILLA","value":"76"},{"disabled":false,"group":null,"selected":false,"text":"SAN ANDRES (ADZ) AEROPUERTO GUSTAVO ROJAS PINILLA","value":"16"}]')

    def test_serialize_set(self):
        val = {890}
        to_json = encoders.JsonEncoder().serialize_to_json(val)
        self.assertEqual(to_json, '[890]')

    def test_serialize_Decimal(self):
        val = Decimal(12.99)
        to_json = encoders.JsonEncoder().serialize_to_json(val)
        self.assertEqual(to_json, '12.99')
