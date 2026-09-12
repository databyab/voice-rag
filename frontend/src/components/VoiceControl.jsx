import React from 'react';

export default function VoiceControl({ voiceStatus, onToggleVoice }) {
  const isListening = voiceStatus === 'Listening...';
  const isThinking = voiceStatus === 'Thinking...';
  const isSpeaking = voiceStatus === 'Speaking...';
  const isActive = isListening || isThinking || isSpeaking;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      {isActive && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            borderRadius: '4px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            fontSize: '12px',
            color: isListening ? '#f87171' : 'var(--text-muted)'
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: isListening ? '#ef4444' : '#a1a1aa'
            }}
          />
          <span>{voiceStatus}</span>
        </div>
      )}

      <button
        onClick={onToggleVoice}
        style={{
          padding: '6px 14px',
          borderRadius: '6px',
          border: '1px solid var(--border-color)',
          background: isActive ? '#2f2f2f' : 'var(--bg-card)',
          color: isActive ? '#f87171' : 'var(--text-primary)',
          fontWeight: '500',
          fontSize: '13px',
          cursor: 'pointer',
          transition: 'background 0.15s ease'
        }}
      >
        {isActive ? 'Stop' : 'Talk'}
      </button>
    </div>
  );
}

