import pytest
from unittest.mock import MagicMock, patch
from src.cache.redis_cache import RedisCache


@pytest.fixture
def redis_cache():
    cache = RedisCache()
    cache.client = MagicMock()
    return cache


def test_set_data_dict(redis_cache):
    redis_cache.set_data('test:key', {'foo': 'bar'}, ttl=100)
    redis_cache.client.setex.assert_called_with(name='test:key', value='{"foo":"bar"}', time=100)


def test_set_data_set(redis_cache):
    test_set = {'a', 'b'}
    redis_cache.set_data('test:set', test_set, ttl=100)

    # Verify sadd called correctly regardless of order
    redis_cache.client.sadd.assert_called_once()
    called_args = redis_cache.client.sadd.call_args
    assert called_args[0][0] == 'test:set'
    assert set(called_args[0][1:]) == test_set

    # Verify expire called correctly
    redis_cache.client.expire.assert_called_once_with('test:set', 100)


def test_get_data_dict(redis_cache):
    redis_cache.client.get.return_value = b'{"foo":"bar"}'
    result = redis_cache.get_data('test:key')
    assert result == {'foo': 'bar'}


def test_get_data_set(redis_cache):
    redis_cache.client.smembers.return_value = {b'a', b'b'}
    result = redis_cache.get_data('test:set', data_type=set)
    assert result == {'a', 'b'}


def test_get_or_set_data_cache_hit(redis_cache):
    redis_cache.client.get.return_value = b'{"cached":"data"}'
    fetch_fn = MagicMock(return_value={'new': 'data'})

    result = redis_cache.get_or_set_data('key', fetch_fn)

    assert result == {'cached': 'data'}
    fetch_fn.assert_not_called()


def test_get_or_set_data_cache_miss(redis_cache):
    redis_cache.client.get.return_value = None
    fetch_fn = MagicMock(return_value={'new': 'data'})

    result = redis_cache.get_or_set_data('key', fetch_fn, ttl=120)

    assert result == {'new': 'data'}
    fetch_fn.assert_called_once()
    redis_cache.client.setex.assert_called_with(name='key', value='{"new":"data"}', time=120)


def test_generate_cache_key(redis_cache):
    def sample_func(self, param1, param2='default', param3=3):
        pass

    key = redis_cache.generate_cache_key(sample_func, ('self', 'val1'), {'param3': 5}, ignore_params=['param2'])
    assert key == 'sample_func:param1=val1:param3=5'


def test_cache_result_decorator(redis_cache):
    @redis_cache.cache_result(expire_in_seconds=200, ignore_params=['skip'])
    def dummy_method(self, a, b=2, skip=False):
        return {'result': a + b}

    redis_cache.get_data = MagicMock(return_value=None)
    redis_cache.set_data = MagicMock()

    result = dummy_method('self', 1, b=3, skip=True)

    redis_cache.get_data.assert_called_with('dummy_method:a=1:b=3', dict)
    redis_cache.set_data.assert_called_with('dummy_method:a=1:b=3', {'result': 4}, 200)
    assert result == {'result': 4}


def test_query_keys_by_prefix(redis_cache):
    redis_cache.client.keys.return_value = [b'prefix:1', b'prefix:2']
    keys = redis_cache.query_keys_by_prefix('prefix')

    redis_cache.client.keys.assert_called_with('prefix*')
    assert keys == ['prefix:1', 'prefix:2']
