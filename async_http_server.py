from aiohttp import web
from aiohttp import ClientSession
from functools import cache
app = web.Application()
routes = web.RouteTableDef()
cache = {}


async def fetch_from_origin(path):
    if path in cache: 
        return cache[path]
    repsonse = None
    async with ClientSession() as session:
        async with session.get(
                f"http://cs5700cdnorigin.ccs.neu.edu:8080/{path}") as resp:
            response =  await resp.text()
    cache[path] = response
    return response


@routes.get("/{path:.*}")
async def respond(request):
    resp = await fetch_from_origin(request.match_info["path"])
    return web.Response(text=resp, content_type="text/html")


app.add_routes(routes)
web.run_app(app)
