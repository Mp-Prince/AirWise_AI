import EmptyState from '../../../components/common/EmptyState.jsx';
import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';
import ChatMessage from './ChatMessage.jsx';

/**
 * Scrollable conversation message window (Phase 5).
 */
export default function ChatWindow({ messages, loading, sending, onFeedback }) {
  if (loading) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center py-5">
          <LoadingSpinner size="lg" />
          <p className="text-supporting mt-2 mb-0">Loading conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card shadow-sm">
      <div className="card-body" style={{ minHeight: '360px', maxHeight: '540px', overflowY: 'auto' }}>
        {messages.length === 0 ? (
          <EmptyState
            icon="bi-chat-dots"
            title="Start a grounded conversation"
            message="Ask about your local AQI, health precautions, or lower-emission choices. Answers cite retrieved documents and never invent readings."
          />
        ) : (
          messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} onFeedback={onFeedback} />
          ))
        )}

        {sending && (
          <div className="d-flex align-items-center gap-2 text-supporting small mt-2">
            <LoadingSpinner size="sm" />
            <span>Retrieving evidence and generating response...</span>
          </div>
        )}
      </div>
    </div>
  );
}
