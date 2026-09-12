import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { fetchDocuments, uploadDocument, sendChatMessage } from './services/api';
import { VoiceSession } from './services/voice';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [voiceStatus, setVoiceStatus] = useState('Idle');

  const voiceSessionRef = useRef(null);

  const loadDocs = async () => {
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUpload = async (file) => {
    setIsUploading(true);
    setUploadStatus(null);
    try {
      const res = await uploadDocument(file);
      setUploadStatus({
        type: 'success',
        message: `Indexed ${res.chunks_created} chunks from ${res.filename}`
      });
      await loadDocs();
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.message || 'Upload failed'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(text);
      const botMsg = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err.message || 'Failed to get answer'}`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleVoice = () => {
    if (voiceStatus !== 'Idle') {
      voiceSessionRef.current?.stop();
      setVoiceStatus('Idle');
    } else {
      const session = new VoiceSession(
        (status) => setVoiceStatus(status),
        (transcript) => {
          setMessages((prev) => [...prev, { role: 'user', content: transcript }]);
        },
        (answer, sources) => {
          setMessages((prev) => [
            ...prev,
            { role: 'assistant', content: answer, sources: sources || [] }
          ]);
        },
        (errorMsg) => {
          console.error('Voice error:', errorMsg);
          setVoiceStatus('Idle');
        }
      );
      voiceSessionRef.current = session;
      session.start();
    }
  };

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <Sidebar
        documents={documents}
        onUpload={handleUpload}
        isUploading={isUploading}
        uploadStatus={uploadStatus}
      />
      <ChatWindow
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        voiceStatus={voiceStatus}
        onToggleVoice={handleToggleVoice}
      />
    </div>
  );
}
