import PageHeader from '../../components/common/PageHeader.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';

/**
 * AI assistant chat (page workflows doc, section 6).
 * Phase 0: conversation shell. RAG-backed answers with citations arrive
 * in Phase 5; answers will always show sources and never invent AQI.
 */
export default function AssistantPage() {
  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="AI Assistant"
        subtitle="Ask about air quality, health precautions and greener choices."
      />
      <div className="card shadow-sm">
        <div className="card-body">
          <EmptyState
            icon="bi-chat-dots"
            title="No conversations yet"
            message="Ask a question and answers will be grounded in trusted environmental documents, with citations shown under each reply."
          />
        </div>
      </div>
      <form className="card shadow-sm mt-3" onSubmit={(e) => e.preventDefault()}>
        <div className="card-body d-flex gap-2">
          <input
            type="text"
            className="form-control"
            placeholder="Ask AirWise…"
            aria-label="Ask the AI assistant"
            disabled
          />
          <button type="submit" className="btn btn-primary flex-shrink-0" disabled>
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
