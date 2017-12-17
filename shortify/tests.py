import pytest

import shortify

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
def cli(loop, test_client):
    return loop.run_until_complete(test_client(shortify.create_app('127.0.0.1')))

async def test_shotify_url(cli):
    resp = await cli.post('/', json={'url': 'http://example.com/qwe'})
    assert resp.status == 200
    assert (await resp.json())['path'] == '/26d1ddaeeed3c38337e00a34d95b98af'


@pytest.fixture
def short_url(cli, loop):
    resp = loop.run_until_complete(cli.post('/', json={'url': 'http://example.com/qwe'}))
    data = loop.run_until_complete(resp.json())
    return data['path']


async def test_get_short(cli, short_url):
    resp = await cli.get(short_url, allow_redirects=False)
    assert resp.status == 302
    assert resp.headers['Location'] == 'http://example.com/qwe'
