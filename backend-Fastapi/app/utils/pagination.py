from dataclasses import dataclass

@dataclass(frozen=True)
class Page:
    page: int
    limit: int

    @property
    def offset(self):
        return (self.page - 1) * self.limit

def clamp_limit(limit: int, max_limit: int) -> int:
    if limit <= 0:
        return 1
    return min(limit, max_limit)


def clamp_page(page: int) -> int:
    return page if page and page > 0 else 1