from dataclasses import dataclass


@dataclass
class Task:
    id: int
    author_id: str
    performer_id: str
    name: str
    status: str
    category: str