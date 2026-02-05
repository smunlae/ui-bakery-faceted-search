import React, { useEffect, useState } from 'react';

export function Pagination({ page, total, limit, onPageChange }) {
  const maxPage = Math.max(1, Math.ceil(total / limit));
  const canPrev = page > 1;
  const canNext = page < maxPage;
  const [pageInput, setPageInput] = useState(String(page));

  useEffect(() => {
    setPageInput(String(page));
  }, [page]);

  const submitPageInput = () => {
    const parsedPage = Number.parseInt(pageInput, 10);
    if (!Number.isFinite(parsedPage)) {
      setPageInput(String(page));
      return;
    }

    const nextPage = Math.min(maxPage, Math.max(1, parsedPage));
    onPageChange(nextPage);
  };

  return (
    <div className="pagination">
      <button type="button" disabled={!canPrev} onClick={() => onPageChange(page - 1)}>
        Prev
      </button>
      <span>
        Page {page} of {maxPage}
      </span>
      <label className="pagination-jump">
        Go to page
        <input
          type="number"
          min="1"
          max={maxPage}
          value={pageInput}
          onChange={(event) => setPageInput(event.target.value)}
          onBlur={submitPageInput}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              submitPageInput();
            }
          }}
        />
      </label>
      <button type="button" disabled={!canNext} onClick={() => onPageChange(page + 1)}>
        Next
      </button>
    </div>
  );
}
