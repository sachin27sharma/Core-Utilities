import redis
import json
import functools
import inspect
from typing import Any, Optional, Callable, Union, List


class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0, default_ttl=3600):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.default_ttl = default_ttl

    def set_data(self, key: str, data: Any, ttl: Optional[int] = None):
        if isinstance(data, (dict, list)):
            serialized_data = json.dumps(data, separators=(',', ':'))
            self.client.setex(name=key, value=serialized_data, time=ttl or self.default_ttl)
        elif isinstance(data, set):
            self.client.sadd(key, *data)
            if ttl:
                self.client.expire(key, ttl)
        elif isinstance(data, (int, float, str)):
            self.client.setex(name=key, value=data, time=ttl or self.default_ttl)
        else:
            raise TypeError("Unsupported data type for caching")

    def get_data(self, key: str, data_type: type = dict) -> Any:
        if data_type == set:
            cached_data = self.client.smembers(key)
            return set(item.decode('utf-8') for item in cached_data)
        cached_data = self.client.get(name=key)
        if cached_data is None:
            return None
        if data_type in (dict, list):
            return json.loads(cached_data.decode('utf-8'))
        return data_type(cached_data.decode('utf-8'))

    def get_or_set_data(self, key: str, fetch_fn: Callable, override: bool = False, ttl: Optional[int] = None, data_type: type = dict) -> Any:
        if not override:
            cached_data = self.get_data(key, data_type)
            if cached_data is not None:
                return cached_data

        data = fetch_fn()
        self.set_data(key, data, ttl)
        return data

    def generate_cache_key(self, func: Callable, args: tuple, kwargs: dict, ignore_params: List[str]) -> str:
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        key_parts = [func.__name__]

        for name, value in bound_args.arguments.items():
            if name != 'self' and name not in ignore_params:
                key_parts.append(f"{name}={value}")

        return ":".join(key_parts)

    def cache_result(self, expire_in_seconds: Optional[int] = None, data_type: type = dict, ignore_params: Optional[List[str]] = None):
        ignore_params = ignore_params or []

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = self.generate_cache_key(func, args, kwargs, ignore_params)

                cached_result = self.get_data(key, data_type)
                if cached_result is not None:
                    return cached_result

                result = func(*args, **kwargs)
                self.set_data(key, result, expire_in_seconds)
                return result
            return wrapper
        return decorator

    def query_keys_by_prefix(self, prefix: str):
        pattern = f"{prefix}*"
        return [key.decode('utf-8') for key in self.client.keys(pattern)]


# Usage Example
if __name__ == '__main__':
    cache = RedisCache(host='localhost', port=6379, db=0, default_ttl=600)

    class DataFetcher:
        @cache.cache_result(expire_in_seconds=300, data_type=dict, ignore_params=['verbose'])
        def fetch_user(self, user_id, verbose=False):
            data = {'user_id': user_id, 'name': f'User{user_id}'}
            if verbose:
                data['details'] = 'Additional user details.'
            return data

    fetcher = DataFetcher()
    user_data = fetcher.fetch_user(123, verbose=True)
    print(user_data)

    keys = cache.query_keys_by_prefix('fetch_user')
    print(keys)