from aiohttp import web, client

MAIN_PAGE = open('./html/index.html').read()
LOGIN_PAGE = open('./html/login.html').read()

# TODO blacklist api
# TODO add login required


class BlackListApi:
    def __init__(self, base_url):
        self.base_url = base_url
        self._session = client.ClientSession()
        self.data = []

    async def get(self):
        return self.data

    async def add(self, domain):
        self.data.append(domain)
        return

    async def delete(self, domain):
        self.data.remove(domain)
        return


class BlacklistView(web.View):
    async def get(self):
        return web.json_response(
            dict(result=await self.request.app.black_list.get())
        )


class BlacklistDeleteView(web.View):
    async def post(self):
        data = await self.request.post()
        await self.request.app.black_list.delete(data['domain'])
        return web.HTTPFound('/')


class IndexView(web.View):
    async def get(self):
        return web.Response(
            text=MAIN_PAGE,
            content_type='text/html'
        )

    async def post(self):
        data = await self.request.post()
        await self.request.app.black_list.add(data['domain'])
        return web.HTTPFound('/')


class LoginView(web.View):
    async def get(self):
        return web.Response(
            text=LOGIN_PAGE,
            content_type='text/html'
        )

    async def post(self):
        data = await self.request.json()
        return web.HTTPFound('/')


def create_app():
    app = web.Application()
    app.black_list = BlackListApi(
        base_url='http://black_list/',
    )
    app.router.add_view('/', IndexView)
    app.router.add_view('/login', LoginView)
    app.router.add_view('/blacklist', BlacklistView)
    app.router.add_view('/blacklist/delete', BlacklistDeleteView)
    return app


def main():
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8090)


if __name__ == '__main__':
    main()
