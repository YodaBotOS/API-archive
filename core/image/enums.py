from enum import Enum, IntEnum


class Size(IntEnum):
    """Enum for image size."""

    SMALL = 256
    MEDIUM = 512
    LARGE = 1024

    def get_size(self):
        return f"{self.value}x{self.value}"


class Alignment(Enum):
    """Enum for image alignment."""

    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"

    def get_alignment(self):
        return self.value
