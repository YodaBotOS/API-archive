class SpotifyResult:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict):
                setattr(self, str(k), SpotifyResult(**v))
            else:
                setattr(self, str(k), v)

        self.raw_dict = kwargs

    def _is_iterable(self, obj):
        try:
            _ = (i for i in obj)
        except TypeError:
            return False
        else:
            return True