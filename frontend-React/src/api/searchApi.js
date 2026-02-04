const API_BASE =
  import.meta.env.REACT_APP_API_BASE ||
  import.meta.env.VITE_API_BASE ||
  'http://127.0.0.1:8000';

export const DEFAULT_LIMIT = 20;

export async function fetchSearch({
  q,
  brands,
  categories,
  page,
  limit,
  signal,
}) {
  const params = new URLSearchParams();

  if (q) {
    params.set('q', q);
  }

  (brands || []).forEach((brandId) => {
    params.append('brand', brandId);
  });

  (categories || []).forEach((categoryId) => {
    params.append('category', categoryId);
  });

  params.set('page', String(page));
  params.set('limit', String(limit));

  const response = await fetch(`${API_BASE}/api/search?${params.toString()}`,
    { signal }
  );

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

    const data = await response.json();

    const normalizeFacetValues = (values) =>
        (values || []).map((value) => ({
            id: value.value ?? value.name ?? value.id ?? value,
            name: value.value ?? value.name ?? String(value),
            count: value.count ?? 0,
        }));

    return {
        ...data,
        items: (data.items || []).map((item) => ({
            ...item,
            categories: (item.categories || []).map((category) =>
                typeof category === 'string' ? { name: category } : category
            ),
        })),
        facets: {
            brands: normalizeFacetValues(data.facets?.brands),
            categories: normalizeFacetValues(data.facets?.categories),
        },
    };
}
