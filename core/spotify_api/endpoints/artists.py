import typing
from ..baseclass import SpotifyResult

class Artists:
    def __init__(self, client):
        self._client = client
        self.get = self.get_artist
        self.get_albums = self.get_artist_albums
        self.get_related_artists = self.get_artist_related_artists
        self.get_top_tracks = self.get_artist_top_tracks
    
    async def get_artist(self, ids: typing.Union[str, list]):
        if isinstance(ids, list):
            resp = await self._client.http.request("GET", "/artists", params={
                "ids": ",".join(ids)
            })
        else:
            resp = await self._client.http.request("GET", f"/artists/{ids}")

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_artist_top_tracks(self, id, *, market = 'US'):
        resp = await self._client.http.request("GET", f"/artists/{id}/albums", params={
            "market": market
        })

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_artist_related_artists(self, id):
        resp = await self._client.http.request("GET", f"/artists/{id}/related-artists")

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_artist_albums(self, id, *, include_groups = None, market = 'US', limit = 10, offset = 5):
        prm = {
            "market": market,
            "limit": limit,
            "offset": offset
        }

        if include_groups:
            prm['include_groups'] = include_groups

        resp = await self._client.http.request("GET", f"/artists/{id}/albums")

        js = await resp.json()

        return SpotifyResult(**js)