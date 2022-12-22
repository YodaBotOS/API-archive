import aiohttp

from .dataclass import QueryResult, Queries


class Database:
    QUERY_ENDPOINT = "http://{}/query"

    def __init__(self, host, key):
        self.host = host
        self.key = key

        self.query_endpoint = self.QUERY_ENDPOINT.format(self.host)

    @staticmethod
    def serialize(js) -> Queries:
        query = js["query"]
        parsed_query = js["parsedQuery"]
        results = js["results"]
        elapsed = js["elapsed"]

        return Queries(query=query, results=[
            QueryResult(query=parsed_query[index], result=result) for index, result in enumerate(results)
        ], elapsed=elapsed)

    async def query(self, query, *values) -> Queries:
        json = {
            "query": query,
            "values": list(values)
        }

        headers = {
            "Authorization": self.key,
        }

        async with aiohttp.ClientSession() as sess:
            async with sess.post(self.query_endpoint, json=json, headers=headers) as resp:
                js = await resp.json()

                queries = self.serialize(js)

                return queries
