import hashlib
from urllib.parse import urlparse

from aiohttp import web
from aredis import StrictRedis


class RedisBasedKeyValueStorage:
    def __init__(self):
        self._client = StrictRedis(host='redis', port=6379, db=0)

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
        md5 = request.match_info['md5']
        url = await self._storage.get(md5)
        rv = web.HTTPFound(url.decode())
        return rv

    async def post_url(self, request):
        data = await request.json()
        url = data['url']
        if not is_valid_url(url):
            return web.json_response(status=400)
        md5 = hashlib.md5(url.encode()).hexdigest()
        await self._storage.set(md5, url, ttl=self._ttl)
        return web.json_response(
            dict(path='/api/{}'.format(md5))
        )


def main():
    storage = RedisBasedKeyValueStorage()
    view = ShorterView(storage)
    app = web.Application()
    app.router.add_get('/api/{md5}', view.get_url)
    app.router.add_post('/', view.post_url)
    app.router.add_static('/', '.')
    web.run_app(app, host='0.0.0.0', port=80)


if __name__ == '__main__':
    main()

# TODO nginx
# TODO hash
# TODO tests
# TODO views
# TODO graphite
