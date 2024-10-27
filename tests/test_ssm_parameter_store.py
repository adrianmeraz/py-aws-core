import json
from importlib.resources import as_file
from unittest import mock
from unittest.mock import PropertyMock

from botocore.stub import Stubber

from py_aws_core import utils
from py_aws_core.boto_clients import SSMClient
from py_aws_core.ssm_parameter_store import SSMParameterStore
from py_aws_core.testing import BaseTestFixture


class SSMParameterStoreTests(BaseTestFixture):
    @mock.patch.object(utils, 'get_environment_variable')
    def test_get_secret_env_var(self, mocked_get_env_var):
        mocked_get_env_var.return_value = 'TEST_VAL_1'
        boto_client = SSMClient().boto_client

        stubber = Stubber(boto_client)
        stubber.activate()

        sm = SSMParameterStore(boto_client=boto_client)
        val = sm.get_secret(secret_name='TEST_KEY_1')
        self.assertEqual('TEST_VAL_1', val)
        stubber.assert_no_pending_responses()

    @mock.patch.object(SSMParameterStore, new_callable=PropertyMock, attribute='aws_secret_id')
    def test_get_secret_caching(self, mocked_aws_secret_id):
        mocked_aws_secret_id.return_value = 'TEST_VAL_2'
        boto_client = SSMClient().boto_client

        stubber = Stubber(boto_client)
        parameter_json = self.get_resource_json('get_parameter.json', path=self.TEST_SSM_RESOURCES_PATH)
        stubber.add_response(method='get_parameter', service_response=parameter_json)
        stubber.activate()

        ssm = SSMParameterStore(boto_client=boto_client)

        val = ssm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)

        # Now checking cache
        val = ssm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)

        stubber.assert_no_pending_responses()
