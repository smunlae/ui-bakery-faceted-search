import { DEFAULT_LIMIT } from '../api/searchApi';

const DEFAULT_PAGE = 1;

const compareIds = (a, b) => {
  const numA = Number(a);
  const numB = Number(b);
  const hasNumA = Number.isFinite(numA);
  const hasNumB = Number.isFinite(numB);

  if (hasNumA && hasNumB) {
    return numA - numB;
  }

  return String(a).localeCompare(String(b));
};

export function parseSearchParams(searchParams) {
  const q = searchParams.get('q') || '';
  const brands = searchParams.getAll('brand');
  const categories = searchParams.getAll('category');
  const pageValue = Number(searchParams.get('page'));
  const limitValue = Number(searchParams.get('limit'));

  const page = Number.isFinite(pageValue) && pageValue >= 1 ? pageValue : DEFAULT_PAGE;
  const limit = Number.isFinite(limitValue) && limitValue >= 1 ? limitValue : DEFAULT_LIMIT;

  return {
    q,
    brands,
    categories,
    page,
    limit,
  };
}

export function buildSearchParams({ q, brands, categories, page, limit }) {
  const params = new URLSearchParams();

  if (q) {
    params.set('q', q);
  }

  (brands || [])
    .slice()
    .sort(compareIds)
    .forEach((brandId) => params.append('brand', brandId));

  (categories || [])
    .slice()
    .sort(compareIds)
    .forEach((categoryId) => params.append('category', categoryId));

  params.set('page', String(page || DEFAULT_PAGE));
  params.set('limit', String(limit || DEFAULT_LIMIT));

  return params;
}
