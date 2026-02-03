from typing import Optional, List
import asyncpg
from app.utils.pagination import Page
from app.models.schemas import SearchResponse


def _normalize_list(values: Optional[List[str]]) -> Optional[List[str]]:
    if values is None:
        return None
    cleaned = [v.strip() for v in values if v and v.strip()]
    return cleaned or None

class SearchService:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

        async def search(self, q: Optional[str], brand_names: Optional[List[str]],
                         category_names: Optional[List[str]], page: Page) -> SearchResponse:
            q = q.strip() if q else None
            brand_names = _normalize_list(brand_names)
            category_names = _normalize_list(category_names)

            async with self.pool.acquire() as conn:
                items = await self._fetch_items(conn, q, brand_names, category_names, page)
                total = await self._fetch_total(conn, q, brand_names, category_names)
                facets = await self._fetch_facets(conn, q, brand_names, category_names)

                return SearchResponse(items=items, page=page.page, limit=page.limit, total=total, facets=facets)

            def _where_clause(self, include_brand: bool, include_category: bool, q: Optional[str],
                              brand_names: Optional[List[str]], category_names: Optional[List[str]],
                              params: List[Any], start_index: int = 1) -> Tuple[str, List[Any], int]:
                parts: List[str] = []
                idx = start_index

                if q:
                    parts.append(f"p.name ILIKE '%' || ${idx} || '%'")
                    params.append(q)
                    idx += 1

                if include_brand and brand_names:
                    parts.append(f"b.name = ANY(${idx}::text[])")
                    params.append(brand_names)
                    idx += 1

                if include_category and category_names:
                    parts.append(
                        "EXISTS (SELECT 1 FROM public.product_categories pc"
                        "JOIN public.categories c ON c.id = pc.category_id"
                        f"WHERE pc.product_id = p.id AND c.name = ANY(${idx}::text[])"
                    )
                    params.append(category_names)
                    idx += 1
                where_sql = ("WHERE "+ " AND ".join(parts)) if parts else ""
                return where_sql, params, idx