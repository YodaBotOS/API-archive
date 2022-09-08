import typing
from ..baseclass import SpotifyResult

class Track:
    def __init__(self, client) -> None:
        self._client = client
        self.get = self.get_track

    async def get_audio_analysis(self, track_id: str):
        resp = await self._client.http.request("GET", f"/audio-analysis/{track_id}")

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_audio_features(self, track_ids: typing.Union[str, list]):
        if isinstance(track_ids, list):
            resp = await self._client.http.request("GET", "/audio-features", params={"ids": ",".join(track_ids)})
        else:
            resp = await self._client.http.request("GET", f"/audio-features/{track_ids}")

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_track(self, track_ids: typing.Union[str, list], *, market='US'):
        if isinstance(track_ids, list):
            resp = await self._client.http.request("GET", "/tracks", params={"ids": ",".join(track_ids), "market": market})
        else:
            resp = await self._client.http.request("GET", f"/tracks/{track_ids}", params={"market": market})

        js = await resp.json()
