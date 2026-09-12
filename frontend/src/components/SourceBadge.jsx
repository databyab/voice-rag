import React from 'react';

export default function SourceBadge({ source, page }) {
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '4px',
        padding: '3px 8px',
        fontSize: '11px',
        color: 'var(--text-muted)',
        marginRight: '6px',
        marginTop: '4px'
      }}
    >
      <span style={{ color: 'var(--text-primary)' }}>{source}</span>
      <span>·</span>
      <span>p. {page}</span>
    </div>
  );
}

