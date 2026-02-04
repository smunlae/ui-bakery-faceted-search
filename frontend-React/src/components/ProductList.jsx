import React from 'react';
import { ProductCard } from './ProductCard';

export function ProductList({ items }) {
  if (!items.length) {
    return <p className="muted">No products found.</p>;
  }

  return (
    <div className="product-grid">
      {items.map((item) => (
        <ProductCard key={item.id} item={item} />
      ))}
    </div>
  );
}
