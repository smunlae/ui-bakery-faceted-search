from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.core.config import settings
from app.db.pool import get_pool
from app.services.search_service import SearchService
from app.utils.pagination import Page, clamp_limit, clamp_page
from app.models.schemas import SearchResponse

router = APIRouter(prefix="/api", tags=["search"])


async def get_service():
    pool = await get_pool()
    return SearchService(pool)


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: Optional[str] = Query(default=None, description="Search query (partial match)"),
    brand: Optional[List[str]] = Query(default=None, description="Brand names (multi-select)"),
    category: Optional[List[str]] = Query(default=None, description="Category names (multi-select)"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=settings.default_limit, ge=1),
    service: SearchService = Depends(get_service),
) -> SearchResponse:
    page = clamp_page(page)
    limit = clamp_limit(limit, settings.max_limit)
    return await service.search(q=q, brand_names=brand, category_names=category, page=Page(page=page, limit=limit))
