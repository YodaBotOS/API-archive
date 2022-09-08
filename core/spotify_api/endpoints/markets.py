class Market:
    def __init__(self, client):
        self._client = client

    async def markets(self) -> list:
        resp = await self._client.http.request("GET", "/markets")

        js = await resp.json()

        return list(js['markets'])