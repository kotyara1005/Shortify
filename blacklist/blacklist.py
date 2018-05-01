from aiohttp import web
from aredis import StrictRedis
from webargs import fields
from webargs.aiohttpparser import use_kwargs


class BlacklistModel:
    def __init__(self, redis):
        self._redis = redis

    @staticmethod
    def _build_key(name):
        return 'blacklist:' + name

    async def add(self, name, entries):
        return await self._redis.sadd(self._build_key(name), *entries)

    async def delete(self, name, entries):
        return await self._redis.srem(self._build_key(name), *entries)

    async def is_blacklisted(self, name, entry):
        return bool(await self._redis.sismember(self._build_key(name), entry))


@use_kwargs({
    'name': fields.Str(required=True),
    'entries': fields.DelimitedList(fields.Str(), required=True),
})
async def add(request, name, entries):
    return web.json_response(
        dict(result=await request.app.model.add(name, entries))
    )


@use_kwargs({
    'name': fields.Str(required=True),
    'entries': fields.DelimitedList(fields.Str(), required=True),
})
async def delete(request, name, entries):
    return web.json_response(
        dict(result=await request.app.model.delete(name, entries))
    )


@use_kwargs({
    'name': fields.Str(required=True),
    'entry': fields.Str(required=True),
})
async def is_blacklisted(request, name, entry):
    return web.json_response(
        dict(result=await request.app.model.is_blacklisted(name, entry))
    )


def create_app(config):
    app = web.Application()
    app.config = config
    app.model = BlacklistModel(
        StrictRedis.from_url(app.config.REDIS_URL),
    )
    app.router.add_post('/add', add)
    app.router.add_post('/delete', delete)
    app.router.add_post('/is_blacklisted', is_blacklisted)
    return app


def main():  # pragma: no cover
    from . import config
    app = create_app(config)
    web.run_app(app, host='0.0.0.0', port=80)


if __name__ == '__main__':  # pragma: no cover
    main()
