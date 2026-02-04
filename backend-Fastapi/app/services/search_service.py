from __future__ import annotations

from typing import Optional, List, Any, Tuple
import asyncpg
import json
from app.utils.pagination import Page
from app.models.schemas import SearchResponse, ProductOut, BrandOut, FacetsOut, FacetValue


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
                "EXISTS (SELECT 1 FROM public.product_categories pc "
                " JOIN public.categories c ON c.id = pc.category_id "
                f" WHERE pc.product_id = p.id AND c.name = ANY(${idx}::text[]))"
            )
            params.append(category_names)
            idx += 1
        where_sql = ("WHERE "+ " AND ".join(parts)) if parts else ""
        return where_sql, params, idx

    async def _fetch_total(
        self,
        conn: asyncpg.Connection,
        q: Optional[str],
        brand_names: Optional[List[str]],
        category_names: Optional[List[str]],
    ) -> int:
        params: List[Any] = []
        where_sql, params, _ = self._where_clause(
            include_brand=True,
            include_category=True,
            q=q,
            brand_names=brand_names,
            category_names=category_names,
            params=params,
            start_index=1,
        )

        sql = f"""
        SELECT COUNT(*)::int AS total
        FROM public.products p
        LEFT JOIN public.brands b ON b.id = p.brand_id
        {where_sql}
        """
        row = await conn.fetchrow(sql, *params)
        return int(row["total"]) if row else 0

    async def _fetch_items(self, conn: asyncpg.connection.Connection, q: Optional[str],
                           brand_names: Optional[List[str]], category_names: Optional[List[str]],
                           page: Page) -> List[ProductOut]:
        params: List[Any] = []
        where_sql, params, idx = self._where_clause(include_brand=True, include_category=True, q=q,
                                                    brand_names=brand_names, category_names=category_names,
                                                    params=params, start_index=1)

        params.append(page.limit)
        limit_idx = idx
        idx += 1
        params.append(page.offset)
        offset_idx = idx

        sql = f"""
                WITH filtered AS (
                    SELECT p.id
                    FROM public.products p
                    LEFT JOIN public.brands b ON b.id = p.brand_id
                    {where_sql}
                    ORDER BY p.name ASC, p.id ASC
                    LIMIT ${limit_idx} OFFSET ${offset_idx}
                )
                SELECT
                    p.id,
                    p.name,
                    p.image,
                    p.created_at::text AS created_at,
                    b.id AS brand_id,
                    b.name AS brand_name,
                    COALESCE(
                        json_agg(DISTINCT c.name) FILTER (WHERE c.name IS NOT NULL),
                        '[]'::json
                    ) AS categories
                FROM filtered f
                JOIN public.products p ON p.id = f.id
                LEFT JOIN public.brands b ON b.id = p.brand_id
                LEFT JOIN public.product_categories pc ON pc.product_id = p.id
                LEFT JOIN public.categories c ON c.id = pc.category_id
                GROUP BY p.id, b.id, b.name
                ORDER BY p.name ASC, p.id ASC
                """

        rows = await conn.fetch(sql, *params)
        items: List[ProductOut] = []
        for r in rows:
            brand = None
            if r["brand_id"] is not None and r["brand_name"] is not None:
                brand = BrandOut(id=int(r["brand_id"]), name=str(r["brand_name"]))

            cats = r["categories"]
            if isinstance(cats, str):
                # should not happen (json), but be defensive
                cats_list = json.loads(cats)
            else:
                cats_list = cats

            items.append(
                ProductOut(
                    id=str(r["id"]),
                    name=str(r["name"]),
                    image=r["image"],
                    created_at=str(r["created_at"]),
                    brand=brand,
                    categories=[str(x) for x in (cats_list or [])],
                )
            )
        return items

    async def _fetch_facets(
        self,
        conn: asyncpg.Connection,
        q: Optional[str],
        brand_names: Optional[List[str]],
        category_names: Optional[List[str]],
    ) -> FacetsOut:
        brand_facet = await self._fetch_brand_facet(conn, q, category_names)
        category_facet = await self._fetch_category_facet(conn, q, brand_names)
        return FacetsOut(brands=brand_facet, categories=category_facet)

    async def _fetch_brand_facet(
        self,
        conn: asyncpg.Connection,
        q: Optional[str],
        category_names: Optional[List[str]],
    ) -> List[FacetValue]:
        params: List[Any] = []
        where_sql, params, _ = self._where_clause(
            include_brand=False,
            include_category=True,
            q=q,
            brand_names=None,
            category_names=category_names,
            params=params,
            start_index=1,
        )

        sql = f"""
        WITH base AS (
            SELECT p.id, p.brand_id
            FROM public.products p
            LEFT JOIN public.brands b ON b.id = p.brand_id
            {where_sql}
        )
        SELECT br.name AS value, COUNT(DISTINCT base.id)::int AS count
        FROM base
        JOIN public.brands br ON br.id = base.brand_id
        GROUP BY br.name
        HAVING COUNT(DISTINCT base.id) > 0
        ORDER BY count DESC, br.name ASC
        """
        rows = await conn.fetch(sql, *params)
        return [FacetValue(value=str(r["value"]), count=int(r["count"])) for r in rows]

    async def _fetch_category_facet(
        self,
        conn: asyncpg.Connection,
        q: Optional[str],
        brand_names: Optional[List[str]],
    ) -> List[FacetValue]:
        params: List[Any] = []
        where_sql, params, _ = self._where_clause(
            include_brand=True,
            include_category=False,
            q=q,
            brand_names=brand_names,
            category_names=None,
            params=params,
            start_index=1,
        )

        sql = f"""
        WITH base AS (
            SELECT p.id
            FROM public.products p
            LEFT JOIN public.brands b ON b.id = p.brand_id
            {where_sql}
        )
        SELECT c.name AS value, COUNT(DISTINCT pc.product_id)::int AS count
        FROM base
        JOIN public.product_categories pc ON pc.product_id = base.id
        JOIN public.categories c ON c.id = pc.category_id
        GROUP BY c.name
        HAVING COUNT(DISTINCT pc.product_id) > 0
        ORDER BY count DESC, c.name ASC
        """
        rows = await conn.fetch(sql, *params)
        return [FacetValue(value=str(r["value"]), count=int(r["count"])) for r in rows]