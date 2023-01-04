import itertools
import logging
import time
from typing import Callable, Generator, Iterable, Type, TypeVar


R = TypeVar('R')
T = TypeVar('T')

logger = logging.getLogger("utils")


def retry(times: int, exceptions: Type[Exception]) -> Callable:
    """
    Decorator. Re-runs the function 'times' times if any of the exceptions given in 'esceptions' occured.

    :param times: times to retry the function
    :type times: int
    :param exceptions: exceptions to catch
    :type exceptions: Type[Exception]
    :return: Decorated function
    :rtype: Callable
    """

    def decorator(func: Callable[[R], T]) -> Callable[[R], T]:

        def inner(*args, **kwargs) -> T:
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logger.debug(f"Exception thrown when attempting to run {func.__name__}, attempt {attempt} of {times}")
                    attempt += 1
                    time.sleep(3)
            return func(*args, **kwargs)

        return inner

    return decorator


def split_into_chunks(iterable: Iterable[T], n: int) -> Generator[Iterable[T], None, None]:
    """
    Split the tierator into chunks of size n.

    :param iterable: iterable
    :type iterable: Iterable[T]
    :param n: chunk size
    :type n: int
    :yield: chunked iterable
    :rtype: Generator[Iterable[T], None, None]
    """

    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk
