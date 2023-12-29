from pydantic import HttpUrl
import aiohttp


async def send_get_request(url: HttpUrl, headers: dict | None = None, params: dict | None = None):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url, params=params) as response:          
            data = await response.json()
            return response.status, data


async def send_post_request(url: HttpUrl, body: dict | None = None, headers: dict | None = None):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url=url, json=body) as response:
            data = await response.json()
            return response.status, data
