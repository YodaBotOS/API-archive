from ..baseclass import SpotifyResult

class Search:
    def __init__(self, client):
        self._client = client

    async def search(self, query, *, types="track,artist,album", market="US", limit=10, offset=5, **kwargs):
        params = {
            "q": str(query),
            "type": str(types),
            "market": str(market),
            "limit": limit,
            "offset": offset,
        }

        if 'incude_external' in kwargs:
            params['incude_external'] = str(kwargs.pop('incude_external')).lower()

        resp = await self._client.http.request("GET", "/search", params=params)

        js = await resp.json()

        return SpotifyResult(**js)