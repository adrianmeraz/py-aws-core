from unittest import mock, TestCase

from src.secrets_manager import SecretsManager


class SecretsManagerTests(TestCase):
    pass
    # @mock.patch.object(dynamodb.DDBClient, 'get_table_name')
    # def test_table_name(self, mocked_get_secrets):
    #     mocked_get_secrets.return_value = 'test_table_123'
    #     val = SecretsManager.get_aws_dynamo_db_table_name()
    #     self.assertEqual(
    #         val,
    #         'test_table_123'
    #     )
    #
    #     self.assertEqual(mocked_get_secrets.call_count, 1)

    # @mock.patch.object(SecretsManager, 'get_aws_cognito_pool_id')
    # def test_get_aws_cognito_pool_id(self, mocked_get_secrets):
    #     mocked_get_secrets.return_value = 'us-west-2_Test123'
    #     val = SecretsManager.get_aws_cognito_pool_id()
    #     self.assertEqual(
    #         val,
    #         'us-west-2_Test123'
    #     )
    #
    #     self.assertEqual(mocked_get_secrets.call_count, 1)
