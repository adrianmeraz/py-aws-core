import typing
from dataclasses import dataclass

from . import exceptions, logs

logger = logs.get_logger()


class APIGatewayRouter:
    """
    Small router for parsing API Gateway Events and calling the matching lambda
    Based on ideas from Tiny-Router
    https://kevinquinn.fun/blog/tiny-python-router-for-aws-lambda/
    """
    VALID_METHODS = ['GET', 'POST', 'PUT', 'DELETE']

    @dataclass
    class PathFuncs:
        fn: typing.Callable
        kwargs: typing.Dict

    def __init__(self):
        self._route_map = dict()

    @property
    def routes(self) -> dict:
        return self._route_map

    def route(self, path: str, http_method: str, **kwargs):
        """
        Decorator to add a route to a function
        :param path:
        :param http_method:
        :param kwargs:
        :return:
        """
        def decorator(fn):
            self.add_route(fn=fn, path=path, http_method=http_method, **kwargs)
            return fn

        return decorator

    def add_route(self, fn: typing.Callable, path: str, http_method: str, **kwargs):
        if http_method not in self.VALID_METHODS:
            raise exceptions.RouteMethodNotAllowed(http_method=http_method, valid_methods=self.VALID_METHODS)
        if http_method in self._route_map and path in self._route_map[http_method]:
            raise exceptions.RouteAlreadyExists(method=http_method, path=path)
        if http_method not in self._route_map:
            self._route_map[http_method] = dict()
        self._route_map[http_method][path] = self.PathFuncs(fn=fn, kwargs=kwargs)
        logger.info(f'Added route to router', http_method=http_method, path=path)

    def handle_event(self, aws_event, aws_context, **kwargs):
        path = aws_event['path']
        http_method = aws_event['httpMethod']
        logger.info(f'Routing event', path=path, http_method=http_method, aws_event=aws_event)
        try:
            path_funcs = self._route_map[http_method][path]
            return path_funcs.fn(aws_event, aws_context, **path_funcs.kwargs, **kwargs)
        except KeyError:
            raise exceptions.RouteNotFound(http_method=http_method, path=path)
