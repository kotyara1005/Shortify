import binascii
from urllib.parse import urlparse

from aiohttp import web
from aredis import StrictRedis

MAIN_PAGE = open('./index.html').read()
REDIS_HOST = 'redis'


class RedisBasedKeyValueStorage:
    def __init__(self, host):
        self._client = StrictRedis(host=host, port=6379, db=0)

    async def set(self, key, value, ttl=None):
        key = 'urls:' + key
        await self._client.set(key, value)
        if ttl is not None:
            await self._client.expire(key, ttl)

    async def get(self, key):
        return await self._client.get('urls:' + key)


def is_valid_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


class ShorterView:
    def __init__(self, storage, ttl=60):
        self._storage = storage
        self._ttl = ttl

    async def get_url(self, request):
        hash_ = request.match_info.get('hash')
        if hash_ is None:
            return web.Response(text=MAIN_PAGE, content_type='text/html')
        url = await self._storage.get(hash_)
        return web.HTTPFound(url.decode())

    async def post_url(self, request):
        data = await request.json()
        url = data['url']
        if not is_valid_url(url):
            return web.json_response(status=400)
        hash_ = hex(binascii.crc32(url.encode()))[2:]
        await self._storage.set(hash_, url, ttl=self._ttl)
        return web.json_response(
            dict(path='/{}'.format(hash_))
        )


def create_app(host):
    storage = RedisBasedKeyValueStorage(host)
    view = ShorterView(storage)
    app = web.Application()
    app.router.add_get('/{hash}', view.get_url)
    app.router.add_get('/', view.get_url)
    app.router.add_post('/', view.post_url)
    return app


def main():
    app = create_app(REDIS_HOST)
    web.run_app(app, host='0.0.0.0', port=80)


if __name__ == '__main__':
    main()

# TODO views
# TODO monitoring
