import React, { useState, useRef, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import InputArea from './components/InputArea';
import PatientInfo from './components/PatientInfo';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [patientData, setPatientData] = useState(null);
  const [specialty, setSpecialty] = useState('general_practice');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState('dark');

  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = { role: 'user', content: message, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${apiUrl}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
          patient_context: patientData,
          specialty: specialty
        })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();

      if (!sessionId) setSessionId(data.session_id);

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(data.timestamp)
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        role: 'assistant',
        content: '⚠️ Error: Failed to get response. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateNote = async () => {
    if (!sessionId) {
      alert('Start a conversation first to generate a note');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/chat/generate-note`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          patient_id: patientData?.patient_id || 'unknown',
          encounter_type: 'office_visit',
          specialty: specialty
        })
      });

      if (!response.ok) throw new Error('Failed to generate note');

      const data = await response.json();

      const noteMessage = {
        role: 'assistant',
        content: `📋 **CLINICAL NOTE**\n\n${data.note_content}\n\n✅ Validation Score: ${(data.validation_score * 100).toFixed(1)}%`,
        timestamp: new Date(data.created_at)
      };
      setMessages(prev => [...prev, noteMessage]);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate note');
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = () => {
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div className={`app ${theme}`}>
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">⚕️</span>
            <h1>Elation Health</h1>
            <span className="subtitle">Chart Review Assistant</span>
          </div>
          <button
            className="theme-toggle"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            title="Toggle theme"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <div className="main-container">
        <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>

          {sidebarOpen && (
            <>
              <PatientInfo
                patientData={patientData}
                onPatientChange={setPatientData}
                specialty={specialty}
                onSpecialtyChange={setSpecialty}
              />

              <div className="controls">
                <button
                  className="btn btn-primary"
                  onClick={handleGenerateNote}
                  disabled={!sessionId || loading}
                >
                  📝 Generate Note
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={handleNewSession}
                >
                  ➕ New Session
                </button>
              </div>
            </>
          )}
        </aside>

        <main className="chat-area">
          <ChatWindow messages={messages} loading={loading} />
          <InputArea onSendMessage={handleSendMessage} disabled={loading} />
        </main>
      </div>
    </div>
  );
}

export default App;
