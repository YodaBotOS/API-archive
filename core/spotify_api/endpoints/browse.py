import typing, datetime
from ..baseclass import SpotifyResult

class Browse:
    def __init__(self, client):
        self._client = client

    async def get_available_genre_seeds(self):
        resp = await self._client.http.request("GET", "/recommendations/available-genre-seeds")

        js = await resp.json()

        return list(js['genres'])

    async def get_categories(self, country = 'SE', *, locale = "sv_SE", limit = 10, offset = 5):
        resp = await self._client.http.request("GET", "/browse/categories", params={
            "country": country,
            "locale": locale,
            "limit": limit,
            "offset": offset
        })

        js = await resp.json()

        return SpotifyResult(**js.get('categories', js))

    async def get_category(self, category_id, *, country = 'SE', locale = 'sv_SE'):
        resp = await self._client.http.request("GET", f"/browse/categories/{category_id}", params={
            "country": country,
            "locale": locale
        })

        js = await resp.json()

        return SpotifyResult(**js.get('categories', js))

    async def get_category_playlists(self, category_id, *, country = 'SE', limit = 10, offset = 5):
        resp = await self._client.http.request("GET", f"/browse/categories/{category_id}/playlists", params={
            "country": country,
            "limit": limit,
            "offset": offset
        })

        js = await resp.json()

        return SpotifyResult(**js.get('playlists', js))

    async def get_featured_playlists(self, country = 'SE', *, locale = 'sv_SE', timestamp = '2014-10-23T09:00:00.000Z', limit = 10, offset = 5):
        if isinstance(timestamp, datetime.datetime):
            timestamp = timestamp.isoformat()

        timestamp = str(timestamp)

        resp = await self._client.http.request('GET', '/browse/featured-playlists', params={
            "country": country,
            "locale": locale,
            "timestamp": timestamp,
            "limit": limit,
            "offset": offset
        })

        js = await resp.json()

        return SpotifyResult(**js)

    async def new_releases(self, country = 'SE', *, limit = 10, offset = 5):
        resp = await self._client.http.request('GET', '/browse/new-releases', params={
            "country": country,
            "limit": limit,
            "offset": offset
        })

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_recommendations(self, **kwargs): # https://developer.spotify.com/console/get-recommendations/
        resp = await self._client.http.request('GET', '/recommendations', params=kwargs)

        js = await resp.json()

        return SpotifyResult(**js)