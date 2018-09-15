import asyncio

import aiohttp
from aiohttp import web
from aredis import StrictRedis

# class BlackListFetcher:
#     def __init__(self, url, line_start):
#         self.url = url
#         self.line_start = line_start
#         self._response = None
#
#     async def fetch(self):
#         async with aiohttp.ClientSession() as session:
#             response = await session.get(self.url)
#             response.raise_for_status()
#             self._response = response
#         return self
#
#     async def __aiter__(self):
#         return await self.fetch()
#
#     async def __anext__(self):
#         if self._response is None:
#             raise Exception('Blacklist is not fetched')
#         async for line in self._response.content:
#             line = line.decode()
#             if line.startswith(self.line_start):
#                 return line.replace(self.line_start, '').strip()
#         raise StopIteration


class BlacklistModel:
    def __init__(self, redis, blacklist_key):
        self._redis = redis
        self._blacklist_key = blacklist_key

    async def add(self, domains):
        return await self._redis.sadd(self._blacklist_key, *domains)

    async def remove(self, domains):
        return await self._redis.srem(self._blacklist_key, *domains)

    async def is_blacklisted(self, domain):
        return bool(await self._redis.sismember(self._blacklist_key, domain))


async def download_blacklisted_domains(url, line_start):
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        response.raise_for_status()
        return [
            line.replace(line_start, '').strip()
            for line in (await response.text()).splitlines()
            if line.startswith(line_start)
        ]


async def refresh_blacklist(config):
    redis = StrictRedis.from_url(config.REDIS_URL)
    await redis.set('test', b'test')
    blacklist = BlacklistModel(
        redis,
        config.BLACKLIST_KEY
    )
    await blacklist.add(
        await download_blacklisted_domains(
            config.BLACKLIST_URL,
            config.LINE_START
        )
    )

# @use_kwargs({
#     'domain': fields.Str(required=True),
# })
# async def is_blacklisted(request, domain):
#     return web.json_response(
#         dict(result=request.app.model.is_blacklisted(domain))
#     )


# def create_app(config):
#     app = web.Application()
#     app.config = config
#     app.model = BlacklistModel(
#         StrictRedis.from_url(config.REDIS_URL),
#         config.BLACKLIST_KEY
#     )
#     app.router.add_post('/is_blacklisted/', is_blacklisted)
#     return app


def main():
    from . import config
    loop = asyncio.get_event_loop()
    loop.run_until_complete(refresh_blacklist(config))


if __name__ == '__main__':
    main()
