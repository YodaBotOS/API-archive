import enum

class Enum(enum.Enum):
    def __str__(self) -> str:
        return self.name

class RequestMethodType(Enum):
    GET = 0
    POST = 1
    PATCH = 2
    DELETE = 3
    PUT = 4
    HEAD = 5
    CONNECT = 6
    OPTIONS = 7