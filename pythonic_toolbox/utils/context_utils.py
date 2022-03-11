import sys


class SkipContext:
    class SkipContentException(Exception):
        pass

    def __init__(self, skip: bool):
        self.skip = skip

    def __enter__(self):
        if self.skip:
            sys.settrace(lambda *args, **keys: None)
            frame = sys._getframe(1)
            frame.f_trace = self.trace

    def trace(self, frame, event, arg):
        raise self.SkipContentException()

    def __exit__(self, type, value, traceback):
        if type is None:
            return  # No exception
        if issubclass(type, self.SkipContentException):
            return True  # Suppress special SkipWithBlockException
