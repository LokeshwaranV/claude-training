import React, { useState } from 'react';
import './InputArea.css';

function InputArea({ onSendMessage, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="input-area" onSubmit={handleSubmit}>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your clinical question or observation... (Shift+Enter for new line)"
        disabled={disabled}
        rows="3"
      />
      <div className="input-actions">
        <button type="submit" disabled={disabled || !input.trim()}>
          {disabled ? '⏳ Sending...' : '📤 Send Message'}
        </button>
      </div>
    </form>
  );
}

export default InputArea;
