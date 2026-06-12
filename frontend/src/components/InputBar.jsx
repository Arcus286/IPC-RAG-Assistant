import { useState } from "react";
import "./InputBar.css";

const SUGGESTIONS = [
  "What is the punishment for theft?",
  "Is carrying pepper spray legal in India?",
  "What does Section 420 mean?",
  "Can a landlord forcibly evict a tenant?",
];

export default function InputBar({ onSend, loading }) {
  const [value, setValue] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(true);

  function handleSubmit() {
    if (!value.trim() || loading) return;
    setShowSuggestions(false);
    onSend(value.trim());
    setValue("");
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleSuggestion(text) {
    setShowSuggestions(false);
    onSend(text);
  }

  return (
    <div className="inputbar-wrapper">
      {showSuggestions && (
        <div className="suggestions">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              className="suggestion-chip"
              onClick={() => handleSuggestion(s)}
              disabled={loading}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="inputbar">
        <textarea
          className="inputbar-textarea"
          placeholder="Ask about a section, a law, or whether something is legal…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          rows={1}
          disabled={loading}
        />
        <button
          className={`inputbar-send ${loading ? "inputbar-send--loading" : ""}`}
          onClick={handleSubmit}
          disabled={loading || !value.trim()}
          aria-label="Send"
        >
          {loading ? (
            <span className="send-spinner" />
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
