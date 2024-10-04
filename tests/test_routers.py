from py_aws_core import exceptions, router
from py_aws_core.testing import BaseTestFixture


class RouterTests(BaseTestFixture):
    def test_add_route(self):
        test_router = router.APIGatewayRouter()
        def doubler(x: int): return 2*x
        test_router.add_route(fn=doubler, http_method='GET', path='/abc')

        with self.assertRaises(exceptions.RouteAlreadyExists):
            test_router.add_route(fn=doubler, http_method='GET', path='/abc')

        test_router.add_route(fn=doubler, http_method='GET', path='/xyz')
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

        @test_router.route(path='/abc', http_method='GET', x=7, concat='cats')
        def doubler_and_concat(*args, x: int, concat: str):
            return f'{2 * x} {concat}'

        @test_router.route(path='/xyz', http_method='GET', x=50, add_number=4000)
        def doubler_and_add(*args, x: int, add_number: int): return (2 * x) + add_number

        mock_event = {'path': '/abc', 'httpMethod': 'GET'}
        val = test_router.handle_event(aws_event=mock_event, aws_context=None)
        self.assertEqual('14 cats', val)

        mock_event = {'path': '/xyz', 'httpMethod': 'GET'}
        val = test_router.handle_event(aws_event=mock_event, aws_context=None)
        self.assertEqual(4100, val)

        with self.assertRaises(exceptions.RouteNotFound):
            mock_event = {'httpMethod': 'GET', 'path': '/badpath'}
            test_router.handle_event(aws_event=mock_event, aws_context=None)


