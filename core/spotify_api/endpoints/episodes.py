import typing
from ..baseclass import SpotifyResult

class Episodes:
    def __init__(self, client):
        self._client = client
        self.get = self.get_episode

    async def get_episode(self, ids: typing.Union[str, list], *, market = 'US'):
        if isinstance(ids, list):
            resp = await self._client.http.request("GET", "/episodes", params={"ids": ids, "market": market})
        else:
            resp = await self._client.http.request("GET", f"/episodes/{ids}", params={"market": market})

        js = await resp.json()

        return SpotifyResult(**js)