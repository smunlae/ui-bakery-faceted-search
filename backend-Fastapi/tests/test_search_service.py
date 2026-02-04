from app.services.search_service import SearchService


class RecordingConnection:
    def __init__(self) -> None:
        self.calls = []

    async def fetch(self, sql: str, *params):
        self.calls.append({"sql": sql, "params": params})
        return []


def test_brand_multi_select_or_semantics():
    service = SearchService(pool=None)
    where_sql, params, _ = service._where_clause(
        include_brand=True,
        include_category=False,
        q=None,
        brand_names=["Apple", "Samsung"],
        category_names=None,
        params=[],
        start_index=1,
    )

    assert "b.name = ANY" in where_sql
    assert where_sql.count("b.name = ANY") == 1
    assert params == [["Apple", "Samsung"]]


def test_category_multi_select_or_semantics():
    service = SearchService(pool=None)
    where_sql, params, _ = service._where_clause(
        include_brand=False,
        include_category=True,
        q=None,
        brand_names=None,
        category_names=["Phones", "Electronics"],
        params=[],
        start_index=1,
    )

    assert "EXISTS" in where_sql
    assert "c.name = ANY" in where_sql
    assert where_sql.count("c.name = ANY") == 1
    assert params == [["Phones", "Electronics"]]


def test_brand_facet_excludes_brand_filter():
    service = SearchService(pool=None)
    conn = RecordingConnection()

    import asyncio

    asyncio.run(
        service._fetch_facets(
            conn,
            q="phone",
            brand_names=["Apple"],
            category_names=["Electronics"],
        )
    )

    brand_sql = conn.calls[0]["sql"]
    category_sql = conn.calls[1]["sql"]

    assert "b.name = ANY" not in brand_sql
    assert "c.name = ANY" in brand_sql
    assert "b.name = ANY" in category_sql


def test_category_facet_excludes_category_filter():
    service = SearchService(pool=None)
    conn = RecordingConnection()

    import asyncio

    asyncio.run(
        service._fetch_facets(
            conn,
            q="phone",
            brand_names=["Apple"],
            category_names=["Electronics"],
        )
    )

    category_sql = conn.calls[1]["sql"]

    assert "c.name = ANY" not in category_sql
    assert "EXISTS" not in category_sql