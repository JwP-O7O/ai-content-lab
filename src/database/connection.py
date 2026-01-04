from contextlib import contextmanager

@contextmanager
def get_db():
    yield None # Dummy session
