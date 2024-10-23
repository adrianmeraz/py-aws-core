
from py_aws_core.exceptions import CoreException
from py_aws_core.testing import BaseTestFixture


class ExceptionTests(BaseTestFixture):
    def test_exception_str(self):
        exc = CoreException()

        self.assertEqual(
            'A generic error has occurred',
            str(exc)
        )

    def test_exception_str_with_message(self):
        exc = CoreException(message="Exception message")

        self.assertEqual(
            'A generic error has occurred, Exception message',
            str(exc)
        )
