import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SourceBadge from './SourceBadge';
import VoiceControl from './VoiceControl';

export default function ChatWindow({
  messages,
  onSendMessage,
  isLoading,
  voiceStatus,
  onToggleVoice
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <main
      style={{
        flex: 1,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-primary)'
      }}
    >
      {/* Top Bar */}
      <header
        style={{
          padding: '16px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-color)',
          background: 'var(--bg-surface)'
        }}
      >
        <div>
          <h1 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)' }}>RAG Assistant</h1>
        </div>

        <VoiceControl voiceStatus={voiceStatus} onToggleVoice={onToggleVoice} />
      </header>

      {/* Messages Scroll Area */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}
      >
        {messages.length === 0 ? (
          <div
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              fontSize: '14px'
            }}
          >
            Ask a question about your documents
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '75%',
                gap: '4px'
              }}
            >
              <div
                style={{
                  fontSize: '11px',
                  fontWeight: '500',
                  color: 'var(--text-muted)',
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  padding: '0 2px'
                }}
              >
                {msg.role === 'user' ? 'You' : 'Assistant'}
              </div>

              <div
                className="markdown-content"
                style={{
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: msg.role === 'user' ? 'var(--bg-card)' : 'var(--bg-surface)',
                  border: '1px solid var(--border-color)',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  color: 'var(--text-primary)'
                }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', marginTop: '2px' }}>
                  {msg.sources.map((src, i) => (
                    <SourceBadge key={i} source={src.source} page={src.page} />
                  ))}
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignSelf: 'flex-start',
              maxWidth: '75%',
              gap: '4px'
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: '500', color: 'var(--text-muted)', padding: '0 2px' }}>
              Assistant
            </div>
            <div
              style={{
                padding: '10px 14px',
                borderRadius: '8px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                fontSize: '14px',
                color: 'var(--text-muted)'
              }}
            >
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form
        onSubmit={handleSubmit}
        style={{
          margin: '0 24px 20px',
          padding: '8px 12px 8px 16px',
          borderRadius: '8px',
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={isLoading}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--text-primary)',
            fontSize: '14px',
            fontFamily: 'inherit'
          }}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          style={{
            padding: '6px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border-color)',
            background: input.trim() && !isLoading ? 'var(--text-primary)' : 'var(--bg-card)',
            color: input.trim() && !isLoading ? 'var(--bg-primary)' : 'var(--text-muted)',
            fontWeight: '500',
            fontSize: '13px',
            cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
            transition: 'background 0.15s ease'
          }}
        >
          Send
        </button>
      </form>
    </main>
  );
}

