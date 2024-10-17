from botocore.stub import Stubber

from py_aws_core.boto_clients import DynamoDBClientFactory
from py_aws_core.session_service import SessionService
from py_aws_core.testing import BaseTestFixture


class GetOrCreateSessionTests(BaseTestFixture):
    def test_get_or_create_session(self):
        session_json = self.get_resource_json('db#update_session.json', path=self.TEST_DB_RESOURCES_PATH)
        session_json['Attributes']['Base64Cookies']['B'] = self.to_utf8_bytes(
            session_json['Attributes']['Base64Cookies']['B'])

        boto_client = DynamoDBClientFactory.new_client()
        stubber = Stubber(boto_client)
        stubber.activate()
        stubber.add_response(method='update_item', service_response=session_json)

        session_service = SessionService(boto_client=boto_client, dynamodb_table_name='TEST_TABLE')
        r_get_item = session_service.get_or_create_session(
            session_id='10c7676f77a34605b5ed76c210369c66',
        )
        session = r_get_item.session
        self.assertEqual(len(session.Base64Cookies.value), 1241)
        self.assertEqual(session.SessionId, '10c7676f77a34605b5ed76c210369c66')

    def test_get_session_item(self):
        session_json = self.get_resource_json('db#get_session_item.json', path=self.TEST_DB_RESOURCES_PATH)
        session_json['Item']['Base64Cookies']['B'] = self.to_utf8_bytes(session_json['Item']['Base64Cookies']['B'])

        boto_client = DynamoDBClientFactory.new_client()
        stubber = Stubber(boto_client)
        stubber.activate()
        stubber.add_response(method='get_item', service_response=session_json)

        session_service = SessionService(boto_client=boto_client, dynamodb_table_name='TEST_TABLE')
        r_get_item = session_service.get_session_item(
            session_id='10c7676f77a34605b5ed76c210369c66'
        )
        self.assertEqual(len(r_get_item.session.Base64Cookies.value), 1241)

    def test_put_session_item(self):
        boto_client = DynamoDBClientFactory.new_client()
        stubber = Stubber(boto_client)
        stubber.activate()
        stubber.add_response(method='put_item', service_response=dict())

        session_service = SessionService(boto_client=boto_client, dynamodb_table_name='TEST_TABLE')
        r_put_item = session_service.put_session_item(
            session_id='10c7676f77a34605b5ed76c210369c66',
            b64_cookies=b"gASVigMAAAAAAABdlCiMDmh0dHAuY29va2llamFylIwGQ29va2lllJOUKYGUfZQojAd2ZXJzaW9u\nlEsAjARuYW1llIwISHR0cE9ubHmUjAV2YWx1ZZROjARwb3J0lE6MDnBvcnRfc3BlY2lmaWVklImM\nBmRvbWFpbpSMHWFwcHMubWlncmFjaW9uY29sb21iaWEuZ292LmNvlIwQZG9tYWluX3NwZWNpZmll\nZJSJjBJkb21haW5faW5pdGlhbF9kb3SUiYwEcGF0aJSMEC9wcmUtcmVnaXN0cm8vZXOUjA5wYXRo\nX3NwZWNpZmllZJSJjAZzZWN1cmWUiIwHZXhwaXJlc5ROjAdkaXNjYXJklIiMB2NvbW1lbnSUTowL\nY29tbWVudF91cmyUTowHcmZjMjEwOZSJjAVfcmVzdJR9lIwIU2FtZVNpdGWUjAZTdHJpY3SUc3Vi\naAMpgZR9lChoBksAaAeMFi5jaGVja21pZy5BbnRpZm9yZ2VyeS6UaAmMm0NmREo4Rl92WjdwbkRD\ncEFnRUdtTDFtSklUSVdld0Y4dXdtTDVaSE5uUTZLN1lDellPQmpEX21UUTZBY1l0YkNkRUFRcnRD\nUnVkNGM5cDFTNE1BUTFKWWdhRFZ0OEtFLWFJbFN3NjJxR21XWEFYcVBMcjZCay1HQVZ0djFjN0lO\nMk13M2ZKRFBmLWlnblZvdFBVNVVhd3JYZWFBlGgKTmgLiWgMjB1hcHBzLm1pZ3JhY2lvbmNvbG9t\nYmlhLmdvdi5jb5RoDoloD4loEIwNL3ByZS1yZWdpc3Ryb5RoEohoE4hoFEowwqVmaBWJaBZOaBdO\naBiJaBl9lCiMCHNhbWVzaXRllIwGc3RyaWN0lIwIaHR0cG9ubHmUTnV1YmgDKYGUfZQoaAZLAGgH\njAdST1VURUlElGgJjAYubm9kZTCUaApOaAuJaAyMHWFwcHMubWlncmFjaW9uY29sb21iaWEuZ292\nLmNvlGgOiWgPiWgQjAEvlGgSiGgTiGgUTmgViGgWTmgXTmgYiWgZfZSMCEh0dHBPbmx5lE5zdWJo\nAymBlH2UKGgGSwBoB4wNUk9VVEVJRFBSRVJFR5RoCYwGLm5vZGUwlGgKTmgLiWgMjB1hcHBzLm1p\nZ3JhY2lvbmNvbG9tYmlhLmdvdi5jb5RoDoloD4loEGgsaBKIaBOJaBROaBWIaBZOaBdOaBiJaBl9\nlHViZS4=\n"
        )
        self.assertEqual(r_put_item, dict())

    def test_update_session(self):
        session_json = self.get_resource_json('db#update_session.json', path=self.TEST_DB_RESOURCES_PATH)
        session_json['Attributes']['Base64Cookies']['B'] = self.to_utf8_bytes(
            session_json['Attributes']['Base64Cookies']['B'])

        boto_client = DynamoDBClientFactory.new_client()
        stubber = Stubber(boto_client)
        stubber.activate()
        stubber.add_response('update_item', session_json)

        session_service = SessionService(boto_client=boto_client, dynamodb_table_name='TEST_TABLE')
        r_get_item = session_service.update_session_cookies(
            session_id='10c7676f77a34605b5ed76c210369c66',
            b64_cookies=b"gASVigMAAAAAAABdlCiMDmh0dHAuY29va2llamFylIwGQ29va2lllJOUKYGUfZQojAd2ZXJzaW9u\nlEsAjARuYW1llIwISHR0cE9ubHmUjAV2YWx1ZZROjARwb3J0lE6MDnBvcnRfc3BlY2lmaWVklImM\nBmRvbWFpbpSMHWFwcHMubWlncmFjaW9uY29sb21iaWEuZ292LmNvlIwQZG9tYWluX3NwZWNpZmll\nZJSJjBJkb21haW5faW5pdGlhbF9kb3SUiYwEcGF0aJSMEC9wcmUtcmVnaXN0cm8vZXOUjA5wYXRo\nX3NwZWNpZmllZJSJjAZzZWN1cmWUiIwHZXhwaXJlc5ROjAdkaXNjYXJklIiMB2NvbW1lbnSUTowL\nY29tbWVudF91cmyUTowHcmZjMjEwOZSJjAVfcmVzdJR9lIwIU2FtZVNpdGWUjAZTdHJpY3SUc3Vi\naAMpgZR9lChoBksAaAeMFi5jaGVja21pZy5BbnRpZm9yZ2VyeS6UaAmMm0NmREo4Rl92WjdwbkRD\ncEFnRUdtTDFtSklUSVdld0Y4dXdtTDVaSE5uUTZLN1lDellPQmpEX21UUTZBY1l0YkNkRUFRcnRD\nUnVkNGM5cDFTNE1BUTFKWWdhRFZ0OEtFLWFJbFN3NjJxR21XWEFYcVBMcjZCay1HQVZ0djFjN0lO\nMk13M2ZKRFBmLWlnblZvdFBVNVVhd3JYZWFBlGgKTmgLiWgMjB1hcHBzLm1pZ3JhY2lvbmNvbG9t\nYmlhLmdvdi5jb5RoDoloD4loEIwNL3ByZS1yZWdpc3Ryb5RoEohoE4hoFEowwqVmaBWJaBZOaBdO\naBiJaBl9lCiMCHNhbWVzaXRllIwGc3RyaWN0lIwIaHR0cG9ubHmUTnV1YmgDKYGUfZQoaAZLAGgH\njAdST1VURUlElGgJjAYubm9kZTCUaApOaAuJaAyMHWFwcHMubWlncmFjaW9uY29sb21iaWEuZ292\nLmNvlGgOiWgPiWgQjAEvlGgSiGgTiGgUTmgViGgWTmgXTmgYiWgZfZSMCEh0dHBPbmx5lE5zdWJo\nAymBlH2UKGgGSwBoB4wNUk9VVEVJRFBSRVJFR5RoCYwGLm5vZGUwlGgKTmgLiWgMjB1hcHBzLm1p\nZ3JhY2lvbmNvbG9tYmlhLmdvdi5jb5RoDoloD4loEGgsaBKIaBOJaBROaBWIaBZOaBdOaBiJaBl9\nlHViZS4=\n"
        )
        session = r_get_item.session
        self.assertEqual(len(session.Base64Cookies.value), 1241)
        self.assertEqual(session.SessionId, '10c7676f77a34605b5ed76c210369c66')
