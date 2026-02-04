# ENGINEERING_NOTES

## 1. Key tradeoffs I made

### 1) Raw SQL in the backend vs using an ORM
I used raw SQL for the search and facet counts because faceted search requires non-trivial queries (EXISTS, COUNT(), exclude self-filter). Raw SQL made the logic explicit and easier to verify and optimize, at the cost of more manual query construction.

### 2) Search approach: ILIKE + trigram vs full-text search (tsvector)
I chose ILIKE for simplicity and because the requirement explicitly mentions partial matches. For performance on 10k rows I’d add trigram index. Full-text search (tsvector) would scale better for linguistic search (ranking), but it adds extra complexity.

### 3) Filtering facets by names vs IDs
I filtered using brand/category names because the UI can directly use facet values from the response and it keeps URLs readable. The tradeoff is that names must be unique and stable; IDs would be more robust long-term.

## 2. How I would scale this further

### 1) Reduce work per request (cache facets/results)
Cache responses keyed by (q, selected brands, selected categories, page, limit) with a short TTL (Redis). Facet results are especially cache-friendly because many users repeat popular queries/filters.

### 2) Indexing and query performance
I already added targeted Postgres indexes for the main access patterns: a B-tree index on products.brand_id, composite indexes on product_categories(category_id, product_id) and (product_id, category_id) to speed up the many-to-many category filter and joins, and a pg_trgm GIN index on products.name to accelerate substring search with ILIKE. For much larger datasets, I would consider moving text search to a dedicated search engine to support ranking and more advanced relevance.

### 3) Precompute or incrementally maintain aggregates
For very high traffic, precompute facet aggregates (materialized views). This can turn expensive GROUP BY queries into fast lookups.

## 3. One non-trivial edge case or technical decision

A non-trivial decision was implementing Amazon-like facet counts that exclude the currently active filter within the same facet group. If you compute facet counts on the fully filtered result set, the counts become misleading when some values are already selected (many options drop to zero). To match Amazon UX, I compute brand counts using (q + categories) while excluding the brand filter, and category counts using (q + brands) while excluding the category filter. This required carefully separating “base result sets” per facet and using COUNT(DISTINCT product_id) to avoid overcounting due to the many-to-many category mapping.

Here is the link to working project (hosted on Railway):
[Faceted-search-by-George-Shtivel](https://miraculous-endurance-production-5a7b.up.railway.app/)