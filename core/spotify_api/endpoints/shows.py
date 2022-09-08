import typing
from ..baseclass import SpotifyResult

class Shows:
    def __init__(self, client):
        self._client = client

    async def get_show(self, ids: typing.Union[list, str], *, market = 'US'):
        if isinstance(ids, list):
            resp = await self._client.http.request("GET", "/shows", params={"ids": ",".join(ids), "market": market})
        else:
            resp = await self._client.http.request("GET", f"/shows/{ids}", params={"market": market})

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_show_episodes(self, id: str, *, market = 'US', limit = 10, offset = 5):
        resp = await self._client.http.request("GET", f"/shows/{id}/episodes", params={"market": market, "limit": limit, "offset": offset})

        js = await resp.json()

        return SpotifyResult(**js)