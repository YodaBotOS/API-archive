import json
from fastapi.responses import Response


class JSONResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")


class StringIntEncoder:
    @staticmethod
    def encode(s: str) -> int:
        b = s.encode()
        return int.from_bytes(b, byteorder='big')

    @staticmethod
    def decode(i: int) -> str:
        return i.to_bytes(((i.bit_length() + 7) // 8), byteorder='big').decode()
