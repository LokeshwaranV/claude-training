import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './ChatWindow.css';

function ChatWindow({ messages, loading }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>👋 Welcome to Elation Health Chat Bot</h2>
            <p>Start a conversation with your clinical assistant</p>
            <ul>
              <li>✅ Draft clinical notes</li>
              <li>✅ Summarize patient records</li>
              <li>✅ Generate documentation</li>
              <li>✅ Validate clinical content</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`message message-${msg.role}`}
            >
              <div className="message-header">
                <span className="role">
                  {msg.role === 'user' ? '👤 You' : '🤖 Assistant'}
                </span>
                <span className="time">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message message-assistant loading">
            <div className="message-header">
              <span className="role">🤖 Assistant</span>
            </div>
            <div className="loading-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ChatWindow;
