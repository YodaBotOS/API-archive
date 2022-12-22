import typing
from dataclasses import dataclass, field


@dataclass
class QueryResult:
    query: str
    result: typing.Any = field(default=None)


@dataclass
class Queries:
    query: str
    results: list[QueryResult] = field(default_factory=list)
    elapsed: float = 0.0
