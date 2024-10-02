import json
from importlib.resources import as_file
from unittest import mock, TestCase
from unittest.mock import PropertyMock

from botocore.stub import Stubber

from py_aws_core import utils
from py_aws_core.secrets_manager import SecretsManager
from tests import const as test_const


class SecretsManagerTests(TestCase):
    @mock.patch.object(utils, 'get_environment_variable')
    def test_get_secret_env_var(self, mocked_get_env_var):
        mocked_get_env_var.return_value = 'TEST_VAL_1'
        sm = SecretsManager()
        stubber = Stubber(sm.boto_client)
        stubber.activate()
        val = sm.get_secret(secret_name='TEST_KEY_1')
        self.assertEqual('TEST_VAL_1', val)

    @mock.patch.object(SecretsManager, new_callable=PropertyMock, attribute='get_aws_secret_id')
    def test_get_secret_caching(self, mock_get_aws_secret_id):
        mock_get_aws_secret_id.return_value = 'TEST_VAL_2'

        sm = SecretsManager()
        stubber = Stubber(sm.boto_client)
        stubber.activate()
        source = test_const.TEST_SECRETS_MANAGER_RESOURCES_PATH.joinpath('get_secret_value.json')
        with as_file(source) as admin_create_user_json:
            stubber.add_response('get_secret_value', json.loads(admin_create_user_json.read_text(encoding='utf-8')))
            val = sm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)

        # Now checking cache
        val = sm.get_secret(secret_name='test_key_1')
        self.assertEqual('test_val_1', val)
