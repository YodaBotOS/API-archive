class MetaClass:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        set_attributes = kwargs.get('set_attributes', False)
        
        if set_attributes:
            for k, v in kwargs.items():
                setattr(self, str(k), v)