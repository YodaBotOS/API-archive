import yarl, typing, aiohttp, asyncio
from .enums import RequestMethodType
from .error import *

class HTTPClient:
    def __init__(self, client):
        self._client = client

    async def request(self, method: typing.Union[RequestMethodType, str], url: str, *args, **kwargs):
        method = str(method)

        if self._client.access_token_did_expire:
            await self._client.perform_auth()

        return await self.send_request(method, url, *args, **kwargs)
        
    async def send_request(self, method, url: str, *args, **kwargs):
        headers = self._client.get_token_headers(bearer=True)

        hdrs = kwargs.pop('headers', None)

        if hdrs:
            headers.update(hdrs)

        without_uri = kwargs.pop('without_url', False)

        raw = kwargs.pop('raw', False)

        if without_uri:
            uri = yarl.URL(url)
        else:
            if url.startswith("/"):
                url = url[1:]

            uri = yarl.URL(self._client.base_url) / url

        async with aiohttp.ClientSession() as session:
            async with session.request(method, str(uri), *args, **kwargs, headers=headers) as resp:
                if resp.status == 404:
                    parse = await self._get_text_and_status_code(resp)
                    raise NotFound(resp, ("Not Found: Status Code: %s: %s" % parse))
                elif resp.status == 403:
                    parse = await self._get_text_and_status_code(resp)
                    raise Forbidden(resp, ("Forbidden: Status Code %s: %s" % parse))
                elif 300 > resp.status >= 200:
                    if raw:
                        return resp
                    else:
                        try:
                            js = await resp.json()
                        except:
                            js = await resp.json(content_type=None)

                        resp.json = asyncio.coroutine(lambda: js)

                        return resp
                else:
                    parse = await self._get_text_and_status_code(resp)
                    raise SpotifyApiException(resp, ("Status Code %s: %s" % parse))

    async def _get_text_and_status_code(self, response: aiohttp.ClientResponse):
        try:
            js = await response.json(content_type=None)
        except:
            return (await response.text(), response.status)
        else:
            error = js.get('error')

            if not error:
                code = response.status
                msg = await response.text()
            else:
                try:
                    code = error.get('status', response.status)
                except:
                    try:
                        code = js.get('status', response.status)
                    except:
                        code = response.status

                try:
                    msg = error.get('message', await response.text())
                except:
                    try:
                        msg = js.get('message', await response.text())
                    except:
                        msg = await response.text()

            return (code, msg)