import { useEffect, useRef, useState } from "react";
import {
  Bot,
  Send,
  User,
  RefreshCw,
  Sparkles,
  Trash2,
  AlertCircle,
} from "lucide-react";

import api from "./services/api";

const suggestions = [
  "How many units are in stock altogether?",
  "Which products need reordering?",
  "Give me the cheapest products.",
  "What is the total inventory value?",
  "What is an ERP system?",
];

export default function AIAssistantPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your Mini ERP AI Assistant. I can help you understand your inventory, identify low-stock products, compare product prices, and answer general ERP questions.",
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  async function sendQuestion(value = question) {
    const text = value.trim();

    if (!text || loading) return;

    setError("");
    setQuestion("");

    setMessages((current) => [
      ...current,
      { role: "user", content: text },
    ]);

    setLoading(true);

    try {
      const response = await api.post("/ai/ask", {
        question: text,
      });

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            response.data?.answer ||
            "The assistant returned an empty response.",
        },
      ]);
    } catch (err) {
      const detail = err.response?.data?.detail;

      const message =
        typeof detail === "string"
          ? detail
          : err.response
            ? `The server returned status ${err.response.status}.`
            : "Cannot connect to the ERP backend. Check that the backend is running.";

      setError(message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendQuestion();
  }

  function clearConversation() {
    if (loading) return;

    setMessages([
      {
        role: "assistant",
        content:
          "Conversation cleared. What would you like to know about your business?",
      },
    ]);

    setError("");
    setQuestion("");
    inputRef.current?.focus();
  }

  return (
    <div className="ai-page">
      <div className="products-toolbar ai-toolbar">
        <div>
          <h2>AI Business Assistant</h2>
          <p>
            Ask questions about your inventory and get answers from
            your ERP data.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={clearConversation}
          disabled={loading}
        >
          <Trash2 size={16} />
          Clear chat
        </button>
      </div>

      <section className="ai-info-banner">
        <div className="ai-info-icon">
          <Sparkles size={21} />
        </div>

        <div>
          <strong>Powered by your local AI service</strong>
          <p>
            Inventory questions use database-backed tools. General
            questions are answered using your local Ollama model.
          </p>
        </div>
      </section>

      <section className="ai-chat-panel">
        <div className="ai-chat-header">
          <div className="ai-chat-avatar">
            <Bot size={21} />
          </div>

          <div>
            <h3>Mini ERP Assistant</h3>
            <p>
              <span className="ai-online-dot" />
              Ready to help
            </p>
          </div>
        </div>

        <div
          className="ai-messages"
          role="log"
          aria-live="polite"
          aria-label="Conversation"
        >
          {messages.map((message, index) => (
            <div
              className={`ai-message-row ${
                message.role === "user" ? "ai-user-row" : ""
              }`}
              key={`${index}-${message.role}`}
            >
              <div
                className={`ai-message-avatar ${
                  message.role === "user"
                    ? "ai-user-avatar"
                    : ""
                }`}
              >
                {message.role === "user" ? (
                  <User size={17} />
                ) : (
                  <Bot size={18} />
                )}
              </div>

              <div
                className={`ai-message-bubble ${
                  message.role === "user"
                    ? "ai-user-bubble"
                    : "ai-assistant-bubble"
                }`}
              >
                <span className="ai-message-label">
                  {message.role === "user" ? "You" : "Assistant"}
                </span>

                <p>{message.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="ai-message-row">
              <div className="ai-message-avatar">
                <Bot size={18} />
              </div>

              <div className="ai-message-bubble ai-assistant-bubble">
                <span className="ai-message-label">Assistant</span>

                <p className="ai-typing">
                  <RefreshCw size={15} className="spin" />
                  Thinking...
                </p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="ai-error" role="alert">
            <AlertCircle size={17} />
            <span>{error}</span>
          </div>
        )}

        <div className="ai-suggestions">
          <span>Try asking</span>

          <div className="ai-suggestion-list">
            {suggestions.map((suggestion) => (
              <button
                type="button"
                className="ai-suggestion"
                key={suggestion}
                onClick={() => sendQuestion(suggestion)}
                disabled={loading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        <form className="ai-input-form" onSubmit={handleSubmit}>
          <label className="ai-input-wrapper">
            <textarea
              ref={inputRef}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask about inventory, products, or your ERP..."
              rows={2}
              maxLength={2000}
              disabled={loading}
              aria-label="Ask the AI Assistant"
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey &&
                  !event.nativeEvent.isComposing
                ) {
                  event.preventDefault();
                  handleSubmit(event);
                }
              }}
            />
          </label>

          <button
            type="submit"
            className="primary-button ai-send-button"
            disabled={loading || !question.trim()}
          >
            {loading ? (
              <RefreshCw size={17} className="spin" />
            ) : (
              <Send size={17} />
            )}

            <span>{loading ? "Thinking..." : "Send"}</span>
          </button>
        </form>

        <p className="ai-disclaimer">
          Answers depend on the available ERP data and configured AI
          tools. Verify important business decisions before acting.
        </p>
      </section>
    </div>
  );
}