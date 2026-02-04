import React, { useMemo, useState } from 'react';

const MAX_VISIBLE = 20;

export function FacetGroup({ title, items, selectedIds, onToggle }) {
  const [showAll, setShowAll] = useState(false);

  const sortedItems = useMemo(() => {
    return [...(items || [])].sort((a, b) => {
      if (b.count !== a.count) {
        return b.count - a.count;
      }
      return a.name.localeCompare(b.name);
    });
  }, [items]);

  const visibleItems = showAll ? sortedItems : sortedItems.slice(0, MAX_VISIBLE);

  if (!sortedItems.length) {
    return null;
  }

  return (
    <div className="facet-group">
      <h3>{title}</h3>
      <ul>
        {visibleItems.map((item) => (
          <li key={item.id}>
            <label>
              <input
                type="checkbox"
                checked={selectedIds.includes(String(item.id))}
                onChange={() => onToggle(String(item.id))}
              />
              <span className="facet-name">{item.name}</span>
              <span className="facet-count">{item.count}</span>
            </label>
          </li>
        ))}
      </ul>
      {sortedItems.length > MAX_VISIBLE && (
        <button
          type="button"
          className="link-button"
          onClick={() => setShowAll((prev) => !prev)}
        >
          {showAll ? 'Show less' : 'Show more'}
        </button>
      )}
    </div>
  );
}
