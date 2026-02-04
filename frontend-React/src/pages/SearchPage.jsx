import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { fetchSearch } from '../api/searchApi';
import { SearchBar } from '../components/SearchBar';
import { FacetGroup } from '../components/FacetGroup';
import { ProductList } from '../components/ProductList';
import { Pagination } from '../components/Pagination';
import { useDebounce } from '../hooks/useDebounce';
import { buildSearchParams, parseSearchParams } from '../utils/urlState';

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlState = useMemo(() => parseSearchParams(searchParams), [searchParams]);
  const [queryInput, setQueryInput] = useState(urlState.q);
  const debouncedQuery = useDebounce(queryInput, 300);

  const [data, setData] = useState({ items: [], facets: { brands: [], categories: [] }, total: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setQueryInput(urlState.q);
  }, [urlState.q]);

  const updateUrl = useCallback(
    (updates) => {
      const nextState = {
        ...urlState,
        ...updates,
      };
      const params = buildSearchParams(nextState);
      setSearchParams(params, { replace: true });
    },
    [setSearchParams, urlState]
  );

  useEffect(() => {
    if (debouncedQuery !== urlState.q) {
      updateUrl({ q: debouncedQuery, page: 1 });
    }
  }, [debouncedQuery, updateUrl, urlState.q]);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setIsLoading(true);
      setError('');
      try {
        const response = await fetchSearch({
          q: urlState.q,
          brands: urlState.brands,
          categories: urlState.categories,
          page: urlState.page,
          limit: urlState.limit,
          signal: controller.signal,
        });

        setData(response);

        const maxPage = Math.max(1, Math.ceil(response.total / response.limit));
        if (urlState.page > maxPage) {
          updateUrl({ page: maxPage });
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError('Failed to load products. Please try again.');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    load();

    return () => controller.abort();
  }, [updateUrl, urlState]);

  const handleFacetToggle = useCallback(
    (type, id) => {
      const current = new Set(type === 'brands' ? urlState.brands : urlState.categories);
      if (current.has(id)) {
        current.delete(id);
      } else {
        current.add(id);
      }
      updateUrl({
        [type === 'brands' ? 'brands' : 'categories']: Array.from(current),
        page: 1,
      });
    },
    [updateUrl, urlState.brands, urlState.categories]
  );

  const handlePageChange = useCallback(
    (nextPage) => {
      updateUrl({ page: nextPage });
    },
    [updateUrl]
  );

  return (
    <div className="page">
      <header className="page-header">
        <h1>Faceted Search</h1>
        <SearchBar value={queryInput} onChange={setQueryInput} />
      </header>

      <div className="page-content">
        <aside className="sidebar">
          <FacetGroup
            title="Brand"
            items={data.facets?.brands || []}
            selectedIds={urlState.brands}
            onToggle={(id) => handleFacetToggle('brands', id)}
          />
          <FacetGroup
            title="Category"
            items={data.facets?.categories || []}
            selectedIds={urlState.categories}
            onToggle={(id) => handleFacetToggle('categories', id)}
          />
        </aside>

        <main className="results">
          <div className="results-header">
            <h2>Results</h2>
            <span className="muted">{data.total} items</span>
          </div>

          {isLoading && <p className="muted">Loading...</p>}
          {error && <p className="error">{error}</p>}

          {!isLoading && !error && <ProductList items={data.items || []} />}

          <Pagination
            page={urlState.page}
            total={data.total}
            limit={urlState.limit}
            onPageChange={handlePageChange}
          />
        </main>
      </div>
    </div>
  );
}
