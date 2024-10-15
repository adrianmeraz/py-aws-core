import json
from importlib.resources import as_file
from unittest import mock, TestCase
from unittest.mock import PropertyMock

import boto3
from botocore.stub import Stubber

from py_aws_core import utils
from py_aws_core.ssm_parameter_store import SSMParameterStore
from tests import const as test_const


class SSMParameterStoreTests(TestCase):
    @mock.patch.object(utils, 'get_environment_variable')
    def test_get_secret_env_var(self, mocked_get_env_var):
        mocked_get_env_var.return_value = 'TEST_VAL_1'
        boto_client = boto3.client('ssm')

        stubber = Stubber(boto_client)
        stubber.activate()

        sm = SSMParameterStore(boto_client=boto_client)
        val = sm.get_secret(secret_name='TEST_KEY_1')
        self.assertEqual('TEST_VAL_1', val)

    @mock.patch.object(SSMParameterStore, new_callable=PropertyMock, attribute='aws_secret_id')
    def test_get_secret_caching(self, mocked_aws_secret_id):
        mocked_aws_secret_id.return_value = 'TEST_VAL_2'
        boto_client = boto3.client('ssm')

        stubber = Stubber(boto_client)
        stubber.activate()

        ssm = SSMParameterStore(boto_client=boto_client)
        source = test_const.TEST_SSM_RESOURCES_PATH.joinpath('get_parameter.json')
        with as_file(source) as parameter_json:
            stubber.add_response('get_parameter', json.loads(parameter_json.read_text(encoding='utf-8')))
            val = ssm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)

        # Now checking cache
        val = ssm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)
