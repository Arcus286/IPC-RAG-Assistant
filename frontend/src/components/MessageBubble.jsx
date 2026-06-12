import "./MessageBubble.css";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const isError = message.role === "error";

  return (
    <div className={`bubble-row ${isUser ? "bubble-row--user" : "bubble-row--assistant"}`}>
      {!isUser && (
        <div className={`bubble-avatar ${isError ? "bubble-avatar--error" : ""}`}>
          {isError ? "!" : "⚖"}
        </div>
      )}

      <div className={`bubble ${isUser ? "bubble--user" : isError ? "bubble--error" : "bubble--assistant"}`}>
        <p className="bubble-text">{message.text}</p>

        {message.sources && message.sources.length > 0 && (
          <div className="bubble-sources">
            <span className="sources-label">Sources</span>
            <div className="sources-list">
              {message.sources.map((src) => (
                <span key={src.section_num} className="source-chip" title={src.title}>
                  § {src.section_num}
                  <span className="source-title"> · {src.title}</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
