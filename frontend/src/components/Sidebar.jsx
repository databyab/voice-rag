import React, { useRef } from 'react';

export default function Sidebar({ documents, onUpload, isUploading, uploadStatus }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <aside
      style={{
        width: '280px',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid var(--border-color)',
        padding: '20px',
        gap: '20px',
        background: 'var(--bg-surface)'
      }}
    >
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)', letterSpacing: '-0.2px' }}>
          Knowledge Base
        </h2>
      </div>

      {/* Upload Action */}
      <div>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt,.md"
          style={{ display: 'none' }}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          style={{
            width: '100%',
            padding: '9px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            fontWeight: '500',
            fontSize: '13px',
            cursor: isUploading ? 'not-allowed' : 'pointer',
            transition: 'background 0.15s ease'
          }}
          onMouseOver={(e) => {
            if (!isUploading) e.currentTarget.style.background = '#2a2a2a';
          }}
          onMouseOut={(e) => {
            if (!isUploading) e.currentTarget.style.background = 'var(--bg-card)';
          }}
        >
          {isUploading ? 'Uploading...' : 'Upload document'}
        </button>

        {uploadStatus && (
          <div
            style={{
              marginTop: '10px',
              padding: '8px 10px',
              borderRadius: '6px',
              fontSize: '12px',
              background: uploadStatus.type === 'error' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(255, 255, 255, 0.05)',
              color: uploadStatus.type === 'error' ? '#fca5a5' : 'var(--text-primary)',
              border: '1px solid var(--border-color)'
            }}
          >
            {uploadStatus.message}
          </div>
        )}
      </div>

      {/* Document List Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.6px' }}>
          Documents ({documents.length})
        </span>
      </div>

      {/* Document List */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {documents.length === 0 ? (
          <div style={{ padding: '20px 4px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No documents uploaded yet.
          </div>
        ) : (
          documents.map((doc, idx) => (
            <div
              key={idx}
              style={{
                padding: '10px 12px',
                borderRadius: '6px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}
            >
              <div
                style={{
                  fontSize: '13px',
                  fontWeight: '500',
                  color: 'var(--text-primary)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
                title={doc.filename}
              >
                {doc.filename}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', gap: '6px' }}>
                <span>{doc.chunks_count} chunks</span>
                <span>·</span>
                <span>{doc.total_pages} {doc.total_pages === 1 ? 'page' : 'pages'}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

