class Tokens:
    """
    The base-class for tokens.

    Paramaters
    ----------
    genius: Optional[:class:`str`]
        The genius token used.
    musixmatch: Optional[:class:`str`]
        The musixmatch token used.
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)