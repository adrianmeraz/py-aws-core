from py_aws_core import exceptions, router
from py_aws_core.testing import BaseTestFixture


class RouterTests(BaseTestFixture):
    def test_add_route(self):
        test_router = router.APIGatewayRouter()
        def doubler(x: int): return 2*x
        test_router.add_route(fn=doubler, http_method='GET', path='abc')

        with self.assertRaises(exceptions.RouteAlreadyExists):
            test_router.add_route(fn=doubler, http_method='GET', path='abc')

        test_router.add_route(fn=doubler, http_method='GET', path='xyz')
        self.assertEqual(2, len(test_router.routes['GET']))

    def test_handle_event(self):
        test_router = router.APIGatewayRouter()
        def doubler(x: int): return 2*x

        test_router.add_route(fn=doubler, http_method='GET', path='abc')
        test_router.add_route(fn=doubler, http_method='GET', path='xyz')
        val = test_router.handle_event(http_method='GET', path='abc', x=7)
        self.assertEqual(14, val)

        with self.assertRaises(exceptions.RouteNotFound):
            test_router.handle_event(http_method='POST', path='badpath', x=7)

