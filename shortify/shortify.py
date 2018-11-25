import binascii
from urllib.parse import urlparse, urljoin

from aiohttp import web, client
from aredis import StrictRedis


class RedisBasedKeyValueStorage:
    def __init__(self, url, ttl):
        self._client = StrictRedis.from_url(url)
        self._ttl = ttl

    async def set(self, key, value):
        key = 'urls:' + key
        await self._client.set(key, value)
        await self._client.expire(key, self._ttl)

    async def get(self, key):
        return await self._client.get('urls:' + key)


class LazySession:
    """
    aiohttp warning sad that create session out of loop context is a bad idea
    """
    def __init__(self):
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        setattr(instance, self.name, client.ClientSession())


class BlackListApi:
    _session = LazySession()

    def __init__(self, base_url):
        self.base_url = base_url

    async def is_blacklisted(self, name, entry):
        url = urljoin(self.base_url, '/is_blacklisted')
        data = {'name': name, 'entry': entry}
        async with self._session.post(url, json=data) as response:
            return (await response.json())['result']


def is_valid_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


async def is_blacklisted_domain(api, url):
    parsed_url = urlparse(url)
    # TODO
    rv = await api.is_blacklisted('domain', parsed_url.netloc)
    return rv


class ShorterView(web.View):
    async def get(self):
        hash_ = self.request.match_info.get('hash')
        if hash_ is None:
            return web.Response(
                text=self.request.app.config.MAIN_PAGE,
                content_type='text/html'
            )
        url = await self.request.app.storage.get(hash_)
        if url is None:
            return web.HTTPNotFound()
        return web.HTTPFound(url.decode())

    async def post(self):
        data = await self.request.json()
        url = data['url']

        if not is_valid_url(url):
            return web.json_response({}, status=400)
        if await is_blacklisted_domain(self.request.app.black_list, url):
            return web.HTTPFound(self.request.app.config.BLACKLIST_URL)

        hash_ = hex(binascii.crc32(url.encode()))[2:]
        await self.request.app.storage.set(hash_, url)
        return web.json_response(
            dict(path='/{}'.format(hash_))
        )


def create_app(config):
    app = web.Application()
    app.config = config
    app.storage = RedisBasedKeyValueStorage(
        app.config.REDIS_URL,
        app.config.RECORD_TTL
    )
    app.black_list = BlackListApi(
        base_url='http://black_list/',
    )
    app.router.add_get('/{hash}', ShorterView)
    app.router.add_get('/', ShorterView)
    app.router.add_post('/', ShorterView)
    return app


def main():
    from . import config
    app = create_app(config)
    web.run_app(app, host='0.0.0.0', port=80)


if __name__ == '__main__':
    main()

# TODO backoffice
