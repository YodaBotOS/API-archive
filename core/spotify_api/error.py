class SpotifyApiException(Exception):
    """The main exception of the Spotify API. Every other exception inherts from this class."""
    def __init__(self, response, *args, **kwargs):
        self.response = response
        super().__init__(*args, **kwargs)

class NotFound(SpotifyApiException):
    """The Exception when a endpoint is not found."""

class Forbidden(SpotifyApiException):
    """The Exception when the API returns a 403 status code."""
    def __init__(self, response, txt):
        super().__init__(response, txt)