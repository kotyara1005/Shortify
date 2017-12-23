import binascii
from urllib.parse import urlparse

from aiohttp import web
from aredis import StrictRedis


class RedisBasedKeyValueStorage:
    def __init__(self, host, ttl):
        self._client = StrictRedis(host=host, port=6379, db=0)
        self._ttl = ttl

    async def set(self, key, value):
        key = 'urls:' + key
        await self._client.set(key, value)
        await self._client.expire(key, self._ttl)

    async def get(self, key):
        return await self._client.get('urls:' + key)


def is_valid_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


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
        hash_ = hex(binascii.crc32(url.encode()))[2:]
        await self.request.app.storage.set(hash_, url)
        return web.json_response(
            dict(path='/{}'.format(hash_))
        )


def create_app(config):
    app = web.Application()
    app.config = config
    storage = RedisBasedKeyValueStorage(
        app.config.REDIS_HOST,
        app.config.RECORD_TTL
    )
    app.storage = storage
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

# TODO monitoring
