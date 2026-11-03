from ninja.pagination import PaginationBase
from pydantic import BaseModel


class CursorPage(BaseModel):
    next_cursor: str | None = None
    results: list


class CursorPagination(PaginationBase):
    """Cursor pagination accepting `?cursor=<opaque>&limit=<n>`.

    The cursor is the base64 of the last seen pk. Models must be ordered by pk
    for stable pages; callers that need another order pass a `?cursor` built
    from the same field.
    """

    class Input(BaseModel):
        cursor: str | None = None
        limit: int = 20

    def paginate_queryset(self, queryset, pagination: Input, **params):
        limit = max(1, min(pagination.limit, 100))
        qs = queryset
        if pagination.cursor:
            qs = qs.filter(pk__gt=int(pagination.cursor))
        rows = list(qs[: limit + 1])
        has_more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = str(rows[-1].pk) if has_more and rows else None
        return {"next_cursor": next_cursor, "results": rows}
