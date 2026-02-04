from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class BrandOut(BaseModel):
    id: int
    name: str

class ProductOut(BaseModel):
    id: str
    name: str
    image: Optional[str] = None
    created_at: str
    brand: Optional[BrandOut] = None
    categories: List[str] = Field(default_factory=list)

class FacetValue(BaseModel):
    value: str
    count: int

class FacetsOut(BaseModel):
    brands: List[FacetValue]
    categories: List[FacetValue]

class SearchResponse(BaseModel):
    items: List[ProductOut]
    page: int
    limit: int
    total: int
    facets: FacetsOut