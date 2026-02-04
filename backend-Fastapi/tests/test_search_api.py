import pytest

pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import FacetValue, FacetsOut, ProductOut, SearchResponse
from app.utils.pagination import Page


class FakeSearchService:
    def __init__(self) -> None:
        self.calls = []

    async def search(self, q, brand_names, category_names, page: Page) -> SearchResponse:
        self.calls.append({
            "q": q,
            "brand_names": brand_names,
            "category_names": category_names,
            "page": page,
        })
        items = [
            ProductOut(
                id=str(idx),
                name=f"Item {idx}",
                image=None,
                created_at="2024-01-01T00:00:00Z",
                brand=None,
                categories=[],
            )
            for idx in range(page.limit)
        ]
        return SearchResponse(
            items=items,
            page=page.page,
            limit=page.limit,
            total=len(items),
            facets=FacetsOut(brands=[FacetValue(value="Any", count=1)], categories=[]),
        )


def _client_with_service(service: FakeSearchService) -> TestClient:
    async def override_get_service():
        return service

    from app.api.routes import search as search_routes

    app.dependency_overrides[search_routes.get_service] = override_get_service
    return TestClient(app)


def test_search_response_contract_and_limit_respected():
    service = FakeSearchService()
    client = _client_with_service(service)
    response = client.get("/api/search", params={"limit": 2})

    assert response.status_code == 200
    payload = response.json()

    assert set(payload.keys()) >= {"items", "total", "facets"}
    assert isinstance(payload["items"], list)
    assert len(payload["items"]) <= 2
    assert "brands" in payload["facets"]
    assert "categories" in payload["facets"]

    app.dependency_overrides.clear()


def test_page_out_of_range_does_not_error():
    service = FakeSearchService()
    client = _client_with_service(service)

    response = client.get("/api/search", params={"page": 9999, "limit": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == [{
        "id": "0",
        "name": "Item 0",
        "image": None,
        "created_at": "2024-01-01T00:00:00Z",
        "brand": None,
        "categories": [],
    }]

    app.dependency_overrides.clear()