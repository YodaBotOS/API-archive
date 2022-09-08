import typing
from ..baseclass import SpotifyResult

class Albums:
    def __init__(self, client):
        self._client = client
        self.get = self.get_album
        self.get_tracks = self.get_album_tracks

    async def get_album_tracks(self, id, *, market = 'US', limit = 10, offset = 5):
        resp = await self._client.http.request("GET", f"/albums/{id}/tracks", params={
            "market": market,
            "limit": limit,
            "offset": offset
        })

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_album(self, ids: typing.Union[str, list], *, market = 'US'):
        if isinstance(ids, list):
            resp = await self._client.http.request("GET", "/albums", params={
                "ids": ",".join(ids),
                "market": market
            })
        else:
            resp = await self._client.http.request("GET", f"/albums/{ids}", params={
                "market": market
            })

        js = await resp.json()

        return SpotifyResult(**js)