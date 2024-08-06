class SpoofingException(Exception):
    ERROR_MESSAGE = 'A generic spoofing error has occurred'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.ERROR_MESSAGE
