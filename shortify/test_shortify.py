import pytest
import asyncio

import shortify

pytest_plugins = 'aiohttp.pytest_plugin'


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


CONFIG = AttrDict(
    MAIN_PAGE='qwe',
    REDIS_URL='redis://127.0.0.1:6666/0',
    RECORD_TTL=2,
)


async def async_result(result):
    return result


@pytest.fixture
def cli(loop, aiohttp_client):
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(
        aiohttp_client(shortify.create_app(CONFIG))
    )


@pytest.fixture()
def all_is_not_blacklisted(cli, mocker):
    mocker.patch(
        'shortify.is_blacklisted_domain',
        return_value=async_result(False),
    )


async def test_shotify_url(cli, all_is_not_blacklisted):
    response = await cli.post('/', json={'url': 'http://example.com/qwe'})
    assert response.status == 200
    assert (await response.json())['path'] == '/5086d044'


@pytest.fixture
def short_url(cli, loop, all_is_not_blacklisted):
    response = loop.run_until_complete(
        cli.post('/', json={'url': 'http://example.com/qwe'})
    )
    data = loop.run_until_complete(response.json())
    return data['path']


async def test_get_short(cli, short_url):
    response = await cli.get(short_url, allow_redirects=False)
    assert response.status == 302
    assert response.headers['Location'] == 'http://example.com/qwe'


async def test_get_main_page(cli):
    response = await cli.get('/')
    assert response.status == 200
    assert 'text/html' in response.headers['Content-Type']


async def test_invalid_url(cli):
    response = await cli.post('/', json={'url': 'ample.com/qwe'})
    assert response.status == 400
    assert await response.json() == {}


async def test_not_found(cli):
    response = await cli.get('/123456', allow_redirects=False)
    assert response.status == 404


async def test_ttl(cli, short_url):
    await asyncio.sleep(CONFIG.RECORD_TTL + 1)
    response = await cli.get(short_url, allow_redirects=False)
    assert response.status == 404
