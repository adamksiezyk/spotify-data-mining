from threading import Thread

from requests import get, post, put, patch, delete, options, head

request_methods = {
    'get': get,
    'post': post,
    'put': put,
    'patch': patch,
    'delete': delete,
    'options': options,
    'head': head,
}


def async_request(method, *args, callback=None, timeout=15, **kwargs) -> Thread:
    """Makes request on a different thread, and optionally passes response to a
    `callback` function when request returns.
    """
    method = request_methods[method.lower()]
    if callback:
        def callback_with_args(response, *args, **kwargs):
            callback(response)

        kwargs['hooks'] = {'response': callback_with_args}
    kwargs['timeout'] = timeout
    thread = Thread(target=method, args=args, kwargs=kwargs)
    thread.start()
    return thread
