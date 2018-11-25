import pytest
from aredis import StrictRedis

import blacklist

pytest_plugins = 'aiohttp.pytest_plugin'


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


CONFIG = AttrDict(REDIS_URL='redis://127.0.0.1:6666/0')


@pytest.fixture(autouse=True)
def clean_local_redis(loop):
    redis = StrictRedis.from_url(CONFIG.REDIS_URL)
    loop.run_until_complete(redis.flushall())


@pytest.fixture
def app():
    return blacklist.create_app(CONFIG)


@pytest.fixture
def cli(loop, aiohttp_client, app):
    return loop.run_until_complete(aiohttp_client(app))


async def test_add(app, cli):
    name = 'test'
    response = await cli.post(
        '/add',
        json={'name': name, 'entries': ['test1.domain.ru', 'test2.domain.ru']}
    )
    assert response.status == 200
    assert (await response.json())['result'] == 2


async def test_delete(cli):
    name = 'test'
    response = await cli.post(
        '/add',
        json={'name': name, 'entries': ['test.domain.ru']}
    )
    assert response.status == 200
    assert (await response.json())['result'] == 1

    response = await cli.post('/delete', json={'name': 'test', 'entries': ['test.domain.ru']})
    assert response.status == 200
    assert (await response.json())['result'] == 1


async def test_is_blacklisted(cli):
    name = 'test'
    response = await cli.post(
        '/add',
        json={'name': name, 'entries': ['test.domain.ru']}
    )
    assert response.status == 200
    assert (await response.json())['result'] == 1

    response = await cli.post('/is_blacklisted', json={'name': 'test', 'entry': 'test.domain.ru'})
    assert response.status == 200
    assert (await response.json())['result'] == True
