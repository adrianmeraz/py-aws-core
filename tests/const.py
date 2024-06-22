from importlib.resources import files

TEST_AUTH_TOKEN = 'eyJraWQiOiJzNndrcytDXC84WGxNOVF2OHNYeVhGczNjV1VsOVFwVzZsdE9rMGt5R2dDVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJjdXN0b206cm9sZXMiOiJTVVBFUlVTRVIsTUVNQkVSLFNUQUZGIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0N4VlFXNU1wVSIsImN1c3RvbTpncm91cCI6Indob2FkZXJlanIiLCJjb2duaXRvOnVzZXJuYW1lIjoiaGVsbG9tb3RvIiwib3JpZ2luX2p0aSI6IjZmMjA5YzgyLWMyNTgtNGIzMC1hMGIxLTBjYWYwMDRkMDRkNiIsImF1ZCI6IjdtdWR1dGdiZGViY2g2YWVoMjF1ZXEyaDFtIiwiZXZlbnRfaWQiOiJhMGNhODUwOS0xMTM0LTRmZWEtYTg5YS1kN2ZjYjRmOTg3ZTciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxMzY2NDMyMCwiZXhwIjoxNzEzNjY3OTIwLCJpYXQiOjE3MTM2NjQzMjAsImp0aSI6IjgzNGI3ZWYyLTBkN2EtNGM2My1hYjI1LWMxYjU1MTU5M2VhNiIsImVtYWlsIjoiYWRyaWFuQHJ5ZGVhcy5jb20ifQ.HrlCeTFFfY_lKtA8HFFrzWRdyCdWbNdaMRozDH65Uzyy9FaavZq2enU8lQSs_TOyEl9aj5mxdIOmN03bpsaiZeWFLD6Ph_oUHl6MQBlgMGPQjzamAO6homn2IH-Thn5jcFdUVWEHIA4GHrw2M_Rty5sCDBxVkdjqCqU4KchoxL2zwXCGdp4Fr-p22PkG8bAkrLQAtO_QE2HqrseJo0XkOm64GDNVvNbL4O4EJ3NUY3vkRck2L0g0GMYG_1x8GFgwr1MdFOg0BOXvL4Qu0ToEVK86mjL-Ua8MR9t9Z4VraKIU5RSncm3SWuWTW6K2uo1oeXAXNWWhrA01Q3BeTGVvJg'
TEST_RESOURCE_PATH = 'tests._resources'
TEST_COGNITO_POOL_CLIENT_ID = '7xxxxtgbdebch6fffffueq2h1m'
TEST_COGNITO_POOL_ID = 'us-west-2_CCCQW5ZZZ'
TEST_ACCESS_TOKEN = 'eifuhwseduivfavhwveci'

TEST_AUTH_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('cognito')
TEST_AUTH_ERROR_RESOURCES_PATH = TEST_AUTH_RESOURCES_PATH.joinpath('errors')

TEST_DB_RESOURCES_PATH = files(TEST_RESOURCE_PATH).joinpath('db')
TEST_DB_ERROR_RESOURCES_PATH = TEST_DB_RESOURCES_PATH.joinpath('errors')
