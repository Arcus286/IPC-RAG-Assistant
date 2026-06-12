import MessageBubble from "./MessageBubble";
import "./ChatWindow.css";

export default function ChatWindow({ messages, loading }) {
  return (
    <div className="chat-window">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {loading && (
        <div className="thinking-row">
          <div className="thinking-dot" />
          <div className="thinking-dot" />
          <div className="thinking-dot" />
        </div>
      )}
    </div>
  );
}
