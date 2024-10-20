import json
from importlib.resources import as_file

from botocore.stub import Stubber
from botocore.exceptions import ClientError

from py_aws_core import cognito_api
from py_aws_core.boto_clients import CognitoClientFactory
from py_aws_core.testing import BaseTestFixture


class AdminCreateUserTests(BaseTestFixture):
    def test_ok(self):
        source = self.TEST_COGNITO_RESOURCES_PATH.joinpath('cognito#admin_create_user.json')
        with as_file(source) as admin_create_user_json:
            boto_client = CognitoClientFactory.new_client()
            stubber = Stubber(boto_client)
            stubber.add_response('admin_create_user', json.loads(admin_create_user_json.read_text(encoding='utf-8')))
            stubber.activate()

        r_call = cognito_api.AdminCreateUser.call(
            boto_client=boto_client,
            cognito_pool_id=self.TEST_COGNITO_POOL_ID,
            username='thecreator44',
            user_attributes=[
                {
                    'Name': 'name1',
                    'Value': 'val1'
                },
                {
                    'Name': 'name2',
                    'Value': 'val2'
                },
            ],
            desired_delivery_mediums=[
                'EMAIL',
            ],
        )
        stubber.deactivate()

        self.assertEqual(r_call.User.Username, 'string')
        stubber.assert_no_pending_responses()


class UserPasswordAuthTests(BaseTestFixture):
    def test_ok(self):
        source = self.TEST_COGNITO_RESOURCES_PATH.joinpath('cognito#initiate_auth.json')
        with as_file(source) as initiate_auth_json:
            boto_client = CognitoClientFactory.new_client()
            stubber = Stubber(boto_client)
            stubber.add_response('initiate_auth', json.loads(initiate_auth_json.read_text(encoding='utf-8')))
            stubber.activate()

        r_call = cognito_api.UserPasswordAuth.call(
            boto_client=boto_client,
            cognito_pool_client_id=self.TEST_COGNITO_POOL_CLIENT_ID,
            username='thecreator44',
            password='pw123'
        )

        self.assertEqual(r_call.AuthenticationResult.AccessToken, 'eyJraWQiOiJzbVUyd3lwQ2QyQ1lhYVhCbW04OUZHU3pkZXBxZ1wvVFlsZUdQS3ZKQ1NWTT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9DeFZRVzVNcFUiLCJjbGllbnRfaWQiOiI3bXVkdXRnYmRlYmNoNmFlaDIxdWVxMmgxbSIsIm9yaWdpbl9qdGkiOiIwMjk5ZjdlNi1kYjdiLTQ3M2YtODZiOC05M2FkY2EyMGQ1MGUiLCJldmVudF9pZCI6IjExNjQxNmE0LTAxN2EtNGMyYi1iOTNhLWNmZGRiYWUyYzYyNyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3MTU3ODUzNDgsImV4cCI6MTcxNTc4ODk0OCwiaWF0IjoxNzE1Nzg1MzQ4LCJqdGkiOiI1MTQ2YjgwMS1kZGM4LTQ0MzUtYmQ3NC0zNjU4MjQ0OGRkYjUiLCJ1c2VybmFtZSI6ImhlbGxvbW90byJ9.EWjr8Fcf_a6cg_VVvXNVqjkndd33qN2cLeJg16rqwLvF4qzJAQK3Qjt4QgjTm8pOjyL1qoz2U1HJP2kSqJIuujSJi3aTcyE-1N7O7SWe3yqhAAuJ15FaGA55tyJ7hC6jhkotXGufxo6-SolHqcDMtNGDBtC5XH4b8ea9RJdnbSZhG43AnlbsfSrCz7GOpQiasyhArSieTEeiZysDKgObLK9U35fzV5cjss4UWEaf3jG1NFuUtA8GsamvWMVxKVDIv72kmfU9nlUWry4UrLkT7nX9QlenPL3LC1KiO6ar_iRwUP_tEBjcg62TBeyfhOn0lTUjvV-vySR2ZkEt-oJItQ')
        self.assertEqual(r_call.AuthenticationResult.IdToken, 'eyJraWQiOiJzNndrcytDXC84WGxNOVF2OHNYeVhGczNjV1VsOVFwVzZsdE9rMGt5R2dDVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJjdXN0b206cm9sZXMiOiJTVVBFUlVTRVIsTUVNQkVSLFNUQUZGIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0N4VlFXNU1wVSIsImN1c3RvbTpncm91cCI6Indob2FkZXJlanIiLCJjb2duaXRvOnVzZXJuYW1lIjoiaGVsbG9tb3RvIiwib3JpZ2luX2p0aSI6IjAyOTlmN2U2LWRiN2ItNDczZi04NmI4LTkzYWRjYTIwZDUwZSIsImF1ZCI6IjdtdWR1dGdiZGViY2g2YWVoMjF1ZXEyaDFtIiwiZXZlbnRfaWQiOiIxMTY0MTZhNC0wMTdhLTRjMmItYjkzYS1jZmRkYmFlMmM2MjciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxNTc4NTM0OCwiZXhwIjoxNzE1Nzg4OTQ4LCJpYXQiOjE3MTU3ODUzNDgsImp0aSI6IjhiMTJmMGQ2LTIyN2UtNDg2Mi1hMGY2LTIxMzEwNjFlMjg4NSIsImVtYWlsIjoiYWRyaWFuQHJ5ZGVhcy5jb20ifQ.fnMRLUYuzVe2cFPnDSrZXhT34bV8SY6SpXqmCtMbwXcFep13JleLdgQ52HNlR8d0OSF26yw612jCXg8DIHV6IxP7miazovAESF1nBrBpYXV70oXeXmi_6UJ6cYxr9XT4cG6iigsJufrc6LvEl_9iOGnvstotrSD_N0hsfpZG0QTeMY8odZIz71_eGFsJqtsIQFZMrAOqRfOxGf1Xnj0AhM9zf5amGAyWpmxKnRVDl2RFi-ZFhellzFZMcQMjawz-CBFQz5lXac-pukiWJgjTjx4macQl7d-7_kDnQWf_aIgsW27SEQKtc9Z885zubAkEXokbbpk1QUEKUtl5TR2EPQ')
        stubber.assert_no_pending_responses()


class RefreshTokenAuthTests(BaseTestFixture):
    def test_ok(self):
        source = self.TEST_COGNITO_RESOURCES_PATH.joinpath('cognito#initiate_auth.json')
        with as_file(source) as initiate_auth_json:
            boto_client = CognitoClientFactory.new_client()
            stubber = Stubber(boto_client)
            stubber.add_response('initiate_auth', json.loads(initiate_auth_json.read_text(encoding='utf-8')))
            stubber.activate()

        r_call = cognito_api.RefreshTokenAuth.call(
            boto_client=boto_client,
            cognito_pool_client_id=self.TEST_COGNITO_POOL_CLIENT_ID,
            refresh_token='eifuhwseduivfavhwveci',
        )

        self.assertEqual(r_call.AuthenticationResult.AccessToken, 'eyJraWQiOiJzbVUyd3lwQ2QyQ1lhYVhCbW04OUZHU3pkZXBxZ1wvVFlsZUdQS3ZKQ1NWTT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9DeFZRVzVNcFUiLCJjbGllbnRfaWQiOiI3bXVkdXRnYmRlYmNoNmFlaDIxdWVxMmgxbSIsIm9yaWdpbl9qdGkiOiIwMjk5ZjdlNi1kYjdiLTQ3M2YtODZiOC05M2FkY2EyMGQ1MGUiLCJldmVudF9pZCI6IjExNjQxNmE0LTAxN2EtNGMyYi1iOTNhLWNmZGRiYWUyYzYyNyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3MTU3ODUzNDgsImV4cCI6MTcxNTc4ODk0OCwiaWF0IjoxNzE1Nzg1MzQ4LCJqdGkiOiI1MTQ2YjgwMS1kZGM4LTQ0MzUtYmQ3NC0zNjU4MjQ0OGRkYjUiLCJ1c2VybmFtZSI6ImhlbGxvbW90byJ9.EWjr8Fcf_a6cg_VVvXNVqjkndd33qN2cLeJg16rqwLvF4qzJAQK3Qjt4QgjTm8pOjyL1qoz2U1HJP2kSqJIuujSJi3aTcyE-1N7O7SWe3yqhAAuJ15FaGA55tyJ7hC6jhkotXGufxo6-SolHqcDMtNGDBtC5XH4b8ea9RJdnbSZhG43AnlbsfSrCz7GOpQiasyhArSieTEeiZysDKgObLK9U35fzV5cjss4UWEaf3jG1NFuUtA8GsamvWMVxKVDIv72kmfU9nlUWry4UrLkT7nX9QlenPL3LC1KiO6ar_iRwUP_tEBjcg62TBeyfhOn0lTUjvV-vySR2ZkEt-oJItQ')
        self.assertEqual(r_call.AuthenticationResult.IdToken, 'eyJraWQiOiJzNndrcytDXC84WGxNOVF2OHNYeVhGczNjV1VsOVFwVzZsdE9rMGt5R2dDVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJjdXN0b206cm9sZXMiOiJTVVBFUlVTRVIsTUVNQkVSLFNUQUZGIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0N4VlFXNU1wVSIsImN1c3RvbTpncm91cCI6Indob2FkZXJlanIiLCJjb2duaXRvOnVzZXJuYW1lIjoiaGVsbG9tb3RvIiwib3JpZ2luX2p0aSI6IjAyOTlmN2U2LWRiN2ItNDczZi04NmI4LTkzYWRjYTIwZDUwZSIsImF1ZCI6IjdtdWR1dGdiZGViY2g2YWVoMjF1ZXEyaDFtIiwiZXZlbnRfaWQiOiIxMTY0MTZhNC0wMTdhLTRjMmItYjkzYS1jZmRkYmFlMmM2MjciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxNTc4NTM0OCwiZXhwIjoxNzE1Nzg4OTQ4LCJpYXQiOjE3MTU3ODUzNDgsImp0aSI6IjhiMTJmMGQ2LTIyN2UtNDg2Mi1hMGY2LTIxMzEwNjFlMjg4NSIsImVtYWlsIjoiYWRyaWFuQHJ5ZGVhcy5jb20ifQ.fnMRLUYuzVe2cFPnDSrZXhT34bV8SY6SpXqmCtMbwXcFep13JleLdgQ52HNlR8d0OSF26yw612jCXg8DIHV6IxP7miazovAESF1nBrBpYXV70oXeXmi_6UJ6cYxr9XT4cG6iigsJufrc6LvEl_9iOGnvstotrSD_N0hsfpZG0QTeMY8odZIz71_eGFsJqtsIQFZMrAOqRfOxGf1Xnj0AhM9zf5amGAyWpmxKnRVDl2RFi-ZFhellzFZMcQMjawz-CBFQz5lXac-pukiWJgjTjx4macQl7d-7_kDnQWf_aIgsW27SEQKtc9Z885zubAkEXokbbpk1QUEKUtl5TR2EPQ')
        stubber.assert_no_pending_responses()

    def test_invalid_refresh_token(self):
        boto_client = CognitoClientFactory.new_client()
        stubber = Stubber(boto_client)
        stubber.add_client_error(method='initiate_auth', service_error_code='NotAuthorizedException')
        stubber.activate()
        with self.assertRaises(ClientError) as e:
            cognito_api.RefreshTokenAuth.call(
                boto_client=boto_client,
                cognito_pool_client_id=self.TEST_COGNITO_POOL_CLIENT_ID,
                refresh_token='eifuhwseduivfavhwveci',
            )

        self.assertEqual(
            'NotAuthorizedException',
            str(e.exception.response['Error']['Code'])
        )
        stubber.assert_no_pending_responses()
