import aiohttp
import asyncio
import base64
import datetime

from .endpoints.albums import Albums
from .endpoints.artists import Artists
from .endpoints.browse import Browse
from .endpoints.episodes import Episodes
from .endpoints.markets import Market
from .endpoints.profile import Profile
from .endpoints.search import Search
from .endpoints.shows import Shows
from .endpoints.tracks import Track
from .error import *
from .http_client import HTTPClient
from .meta import MetaClass


class Client(MetaClass):
    def __init__(self, client_id=None, client_secret=None, *args, **kwargs):
        # set_attr = kwargs.pop('set_attributes', False)
        super().__init__((), {}, set_attributes=False)

        self.client_id = str(client_id)
        self.client_secret = str(client_secret)

        self.base_url = kwargs.pop(
            'base_url', kwargs.pop(
                'base_uri', 'https://api.spotify.com/v1/'
            )
        )

        if not hasattr(self, 'loop'):
            self.loop = asyncio.get_event_loop()

        self.access_token = None
        self.access_token_expires = None
        self._searchJSON = {}
        self.token_url = "https://accounts.spotify.com/api/token"
        self.http = HTTPClient(self)
        self.jsonData = {
            "spotify": {
                "id": client_id,
                "secret": client_secret
            }
        }

    @property
    def track(self):
        return Track(self)

    @property
    def profile(self):
        return Profile(self)

    @property
    def shows(self):
        return Shows(self)

    @property
    def search(self):
        return Search(self)

    @property
    def market(self):
        return Market(self)

    @property
    def episode(self):
        return Episodes(self)

    @property
    def browse(self):
        return Browse(self)

    @property
    def artist(self):
        return Artists(self)

    @property
    def album(self):
        return Albums(self)

    def get_client_credentials(self) -> str:
        """
        Returns a base64 encoded string
        """

        client_id = self.jsonData["spotify"]["id"]
        client_secret = self.jsonData["spotify"]["secret"]

        if not client_secret or not client_id:
            raise SpotifyApiException("You must set both client_id and client_secret")

        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.urlsafe_b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self, *, bearer=False) -> dict:
        client_creds_b64 = self.get_client_credentials()
        if not bearer:
            return {
                "Authorization": f"Basic {client_creds_b64}",
            }
        else:
            return {
                "Authorization": f"Bearer {self.access_token}",
            }

    def get_token_data(self) -> dict:
        return {
            "grant_type": "client_credentials"
        }

    async def perform_auth(self) -> tuple:
        token_url = self.token_url
        token_data = self.get_token_data()
        client_creds_b64 = self.get_client_credentials()
        token_headers = {
            "client_id": f"{self.client_id}",
            "client_secret": f"{self.client_secret}"
            # "Accept": "application/json",
            # "Content-Type": "application/json"
        }
        token_data.update(token_headers)

        async with aiohttp.ClientSession() as session:
            async with session.request('POST', token_url, data=token_data) as resp:
                js = await resp.json()
                status = resp.status

        if status != 200:
            return False, js, "status_code={}".format(status)

        data = js
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)

        self.access_token = access_token
        self.access_token_expires = expires

        return True, js, "status_code={}".format(status)

    @property
    def access_token_did_expire(self):
        if not self.access_token_expires:
            return True

        return (self.access_token_expires <= datetime.datetime.utcnow()) or (
                    self.access_token_expires <= datetime.datetime.now())
