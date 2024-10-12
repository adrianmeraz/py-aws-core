import json
from importlib.resources import as_file
from unittest import mock, TestCase
from unittest.mock import PropertyMock

from botocore.stub import Stubber

from py_aws_core import utils
from py_aws_core.ssm_parameter_store import SSMParameterStore
from tests import const as test_const


class SSMParameterStoreTests(TestCase):
    @mock.patch.object(utils, 'get_environment_variable')
    def test_get_secret_env_var(self, mocked_get_env_var):
        mocked_get_env_var.return_value = 'TEST_VAL_1'
        sm = SSMParameterStore()
        stubber = Stubber(sm.boto_client)
        stubber.activate()
        val = sm.get_secret(secret_name='TEST_KEY_1')
        self.assertEqual('TEST_VAL_1', val)

    @mock.patch.object(SSMParameterStore, new_callable=PropertyMock, attribute='get_aws_secret_name')
    def test_get_secret_caching(self, mock_get_aws_secret_name):
        mock_get_aws_secret_name.return_value = 'TEST_VAL_2'

        ssm = SSMParameterStore()
        stubber = Stubber(ssm.boto_client)
        stubber.activate()
        source = test_const.TEST_SSM_RESOURCES_PATH.joinpath('get_parameter.json')
        with as_file(source) as parameter_json:
            stubber.add_response('get_parameter', json.loads(parameter_json.read_text(encoding='utf-8')))
            val = ssm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)

        # Now checking cache
        val = ssm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)
