import { useState, useRef, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import InputBar from "./components/InputBar";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: "assistant",
      text: "Ask me anything about the Indian Penal Code — a specific section, what a law means, or whether something is legal.",
      sources: [],
    },
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(question) {
    if (!question.trim() || loading) return;

    const userMsg = { id: Date.now(), role: "user", text: question, sources: [] };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 5 }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Something went wrong");
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "error",
          text: err.message || "Failed to reach the server. Is the backend running?",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <span className="header-badge">IPC</span>
          <div>
            <h1 className="header-title">LexQuery</h1>
            <p className="header-sub">Indian Penal Code · AI Research Assistant</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <ChatWindow messages={messages} loading={loading} />
        <div ref={bottomRef} />
      </main>

      <footer className="app-footer">
        <InputBar onSend={handleSend} loading={loading} />
        <p className="disclaimer">
          Informational only · Not legal advice · Consult a qualified lawyer for your situation
        </p>
      </footer>
    </div>
  );
}
