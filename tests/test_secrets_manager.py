import json
from importlib.resources import as_file
from unittest import mock
from unittest.mock import PropertyMock

from botocore.stub import Stubber

from py_aws_core import utils
from py_aws_core.boto_clients import SecretManagerClientFactory
from py_aws_core.secrets_manager import SecretsManager
from py_aws_core.testing import BaseTestFixture


class SecretsManagerTests(BaseTestFixture):
    @mock.patch.object(utils, 'get_environment_variable')
    def test_get_secret_env_var(self, mocked_get_env_var):
        mocked_get_env_var.return_value = 'TEST_VAL_1'
        boto_client = SecretManagerClientFactory().new_client()

        stubber = Stubber(boto_client)
        stubber.activate()

        sm = SecretsManager(boto_client=boto_client)
        val = sm.get_secret(secret_name='TEST_KEY_1')
        self.assertEqual('TEST_VAL_1', val)
        stubber.assert_no_pending_responses()

    @mock.patch.object(SecretsManager, new_callable=PropertyMock, attribute='aws_secret_name')
    def test_get_secret_caching(self, mocked_aws_secret_name):
        mocked_aws_secret_name.return_value = 'TEST_VAL_2'
        boto_client = SecretManagerClientFactory().new_client()

        stubber = Stubber(boto_client)
        stubber.activate()

        sm = SecretsManager(boto_client=boto_client)
        source = self.TEST_SECRETS_MANAGER_RESOURCES_PATH.joinpath('get_secret_value.json')
        with as_file(source) as admin_create_user_json:
            stubber.add_response('get_secret_value', json.loads(admin_create_user_json.read_text(encoding='utf-8')))
            val = sm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)

        # Now checking cache
        val = sm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)
        stubber.assert_no_pending_responses()
