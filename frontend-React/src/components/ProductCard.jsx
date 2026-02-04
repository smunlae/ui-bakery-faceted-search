import React from 'react';

export function ProductCard({ item }) {
  return (
    <article className="product-card">
      <div className="product-image">
        {item.image ? (
          <img src={item.image} alt={item.name} loading="lazy" />
        ) : (
          <div className="image-placeholder">No image</div>
        )}
      </div>
      <div className="product-info">
        <h4>{item.name}</h4>
        <p className="muted">Brand: {item.brand?.name || 'Unknown'}</p>
        <p className="muted">
          Categories:{' '}
          {item.categories?.length
            ? item.categories.map((category) => category.name).join(', ')
            : 'Uncategorized'}
        </p>
      </div>
    </article>
  );
}
