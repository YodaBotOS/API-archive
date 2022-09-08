from ..baseclass import SpotifyResult

class Profile:
    def __init__(self, client):
        self._client = client

    async def me(self):
        resp = await self._client.http.request("GET", "/me")

        js = await resp.json()

        return SpotifyResult(**js)

    async def get_user(self, user_id: str):
        resp = await self._client.http.request("GET", f"/users/{user_id}")

        js = await resp.json()

        return SpotifyResult(**js)