import React from 'react';

export function Pagination({ page, total, limit, onPageChange }) {
  const maxPage = Math.max(1, Math.ceil(total / limit));
  const canPrev = page > 1;
  const canNext = page < maxPage;

  return (
    <div className="pagination">
      <button type="button" disabled={!canPrev} onClick={() => onPageChange(page - 1)}>
        Prev
      </button>
      <span>
        Page {page} of {maxPage}
      </span>
      <button type="button" disabled={!canNext} onClick={() => onPageChange(page + 1)}>
        Next
      </button>
    </div>
  );
}
