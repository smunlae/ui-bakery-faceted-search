import React from 'react';

export function SearchBar({ value, onChange }) {
  return (
    <div className="search-bar">
      <label htmlFor="search-input">Search</label>
      <input
        id="search-input"
        type="text"
        placeholder="Search products"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}
