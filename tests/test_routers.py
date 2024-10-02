from py_aws_core import exceptions, router
from py_aws_core.testing import BaseTestFixture


class RouterTests(BaseTestFixture):
    def test_add_route(self):
        test_router = router.APIGatewayRouter()
        def doubler(x: int): return 2*x
        test_router._add_route(fn=doubler, http_method='GET', path='abc')

        with self.assertRaises(exceptions.RouteAlreadyExists):
            test_router._add_route(fn=doubler, http_method='GET', path='abc')

        test_router._add_route(fn=doubler, http_method='GET', path='xyz')
        self.assertEqual(2, len(test_router.routes['GET']))

    def test_route_decorator(self):
        test_router = router.APIGatewayRouter()

        @test_router.route(path='/abc', http_method='GET', extra_arg='an extra arg')
        def doubler(x: int): return 2*x

        with self.assertRaises(exceptions.RouteAlreadyExists):
            @test_router.route(path='/abc', http_method='GET', extra_arg='something else')
            def doubler_2(x: int): return 2 * x

        # Now adding new path "xyz"
        @test_router.route(path='/xyz', http_method='GET', extra_arg='something else')
        def doubler_2(x: int): return 2 * x

        self.assertEqual(2, len(test_router.routes['GET']))

    def test_handle_event(self):
        test_router = router.APIGatewayRouter()

        @test_router.route(path='/abc', http_method='GET', concat='cats')
        def doubler_and_concat(x: int, concat: str): return f'{2 * x} {concat}'

        @test_router.route(path='/xyz', http_method='GET', add_number=4000)
        def doubler_and_add(x: int, add_number: int): return (2 * x) + add_number

        val = test_router.handle_event(http_method='GET', path='/abc', x=7)
        self.assertEqual('14 cats', val)

        val = test_router.handle_event(http_method='GET', path='/xyz', x=50)
        self.assertEqual(4100, val)

        with self.assertRaises(exceptions.RouteNotFound):
            test_router.handle_event(http_method='POST', path='/badpath', x=7)

