import logging
from functools import wraps

import boto3
from decouple import config


def _to_dict(s: str) -> dict:
    try:
        return (
            {kv[0]: kv[1] for kv in [kv.strip().split("=") for kv in s.split(",")]}
            if s
            else {}
        )
    except IndexError as e:
        raise Exception(f'Unable to cast "{s}" to dict.') from e


def with_endpoint_url(func):
    """Call boto3 with endpoint_url if set in the environment.

    resource/client generated by Session class in boto3/session.py#L28

    Args:
        func (function)
    """

    @wraps(func)
    def wrapper(service_name, *args, **kwargs):
        try:
            override = _to_dict(config("AWS_ENDPOINTS", default=None)).get(
                service_name, None
            )
            endpoint = kwargs.pop("endpoint_url", override)
            return getattr(boto3, func.__name__)(
                service_name, *args, endpoint_url=endpoint, **kwargs
            )
        except Exception as e:
            logging.getLogger().warning(
                f"Something went wrong when generating a boto3 {func.__name__}: {e.__class__.__name__} {e}"
            )
            return func(service_name, *args, **kwargs)

    return wrapper


@with_endpoint_url
def resource(*args, **kwargs):
    return boto3.resource(*args, **kwargs)


@with_endpoint_url
def client(*args, **kwargs):
    return boto3.client(*args, **kwargs)
