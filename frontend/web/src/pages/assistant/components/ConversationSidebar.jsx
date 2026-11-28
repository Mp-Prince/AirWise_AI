/**
 * Conversation sidebar showing previous chats and New Chat button (Phase 5).
 */
export default function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  loading,
}) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-header d-flex justify-content-between align-items-center">
        <span className="fw-semibold">Conversations</span>
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={onNewChat}
        >
          <i className="bi bi-plus-lg me-1" aria-hidden="true" />
          New Chat
        </button>
      </div>
      <div className="list-group list-group-flush" style={{ maxHeight: '480px', overflowY: 'auto' }}>
        {loading ? (
          <div className="p-3 text-center text-muted small">Loading history...</div>
        ) : conversations.length === 0 ? (
          <div className="p-3 text-center text-supporting small">
            No previous conversations yet.
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            return (
              <div
                key={conv.id}
                className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center gap-2 ${
                  isActive ? 'active' : ''
                }`}
              >
                <button
                  type="button"
                  className={`btn btn-link text-start text-decoration-none p-0 flex-grow-1 text-truncate ${
                    isActive ? 'text-white' : 'text-body'
                  }`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <i className="bi bi-chat-left-text me-2" aria-hidden="true" />
                  {conv.title || 'Untitled conversation'}
                </button>
                <button
                  type="button"
                  className={`btn btn-sm p-1 ${isActive ? 'text-white' : 'text-muted'}`}
                  aria-label="Delete conversation"
                  onClick={() => onDeleteConversation(conv.id)}
                >
                  <i className="bi bi-trash" aria-hidden="true" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
