import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import assistantService from '../../services/assistantService.js';
import ConversationSidebar from './components/ConversationSidebar.jsx';
import ChatWindow from './components/ChatWindow.jsx';
import SuggestedPrompts from './components/SuggestedPrompts.jsx';
import ChatComposer from './components/ChatComposer.jsx';

/**
 * AI assistant chat page (Phase 5).
 * Composes conversation sidebar, grounded message history, citations, and composer.
 */
export default function AssistantPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [includeContext, setIncludeContext] = useState(true);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [usage, setUsage] = useState(null);

  const loadConversations = useCallback(async () => {
    if (!user) return;
    setLoadingList(true);
    try {
      const [convRes, usageRes] = await Promise.all([
        assistantService.getConversations(),
        assistantService.getUsage(),
      ]);
      setConversations(convRes.conversations || []);
      setUsage(usageRes);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load conversations');
    } finally {
      setLoadingList(false);
    }
  }, [user]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleSelectConversation = async (conversationId) => {
    setActiveConversationId(conversationId);
    setLoadingMessages(true);
    setError(null);
    try {
      const detail = await assistantService.getConversation(conversationId);
      setMessages(detail.messages || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load conversation history');
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setError(null);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await assistantService.deleteConversation(conversationId);
      if (conversationId === activeConversationId) {
        handleNewChat();
      }
      await loadConversations();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete conversation');
    }
  };

  const submitMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || sending) return;

    setError(null);
    setSending(true);
    const optimisticUserMsg = {
      id: `local-${Date.now()}`,
      role: 'user',
      content: trimmed,
      created_at: new Date().toISOString(),
      isLocalOnly: true,
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);
    setInput('');

    try {
      const res = await assistantService.sendMessage({
        conversation_id: activeConversationId,
        message: trimmed,
        include_user_context: includeContext,
      });

      setActiveConversationId(res.conversation_id);
      setUsage(res.usage);

      const assistantMsg = {
        id: res.message_id,
        role: 'assistant',
        content: res.answer,
        recommendations: res.recommendations,
        sources: res.sources,
        data_context: res.data_context,
        limitations: res.limitations,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      await loadConversations();
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== optimisticUserMsg.id));
      setInput(trimmed);
      setError(err.response?.data?.detail || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    submitMessage(input);
  };

  const handleFeedback = async (messageId, helpful) => {
    try {
      await assistantService.submitFeedback({ message_id: messageId, helpful });
    } catch {
      // Non-blocking feedback error
    }
  };

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="AI Assistant"
        subtitle="Ask about air quality, health precautions and greener choices."
        actions={
          usage && (
            <span className="badge text-bg-light border">
              {usage.calls_in_window}/{usage.rate_limit_per_minute} req/min
            </span>
          )
        }
      />

      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

      <div className="row g-3 g-lg-4">
        <div className="col-12 col-lg-4 col-xl-3">
          <ConversationSidebar
            conversations={conversations}
            activeConversationId={activeConversationId}
            onSelectConversation={handleSelectConversation}
            onNewChat={handleNewChat}
            onDeleteConversation={handleDeleteConversation}
            loading={loadingList}
          />
        </div>

        <div className="col-12 col-lg-8 col-xl-9">
          <ChatWindow
            messages={messages}
            loading={loadingMessages}
            sending={sending}
            onFeedback={handleFeedback}
          />
          <SuggestedPrompts onSelectPrompt={submitMessage} disabled={sending} />
          <ChatComposer
            value={input}
            onChange={setInput}
            includeContext={includeContext}
            onToggleContext={setIncludeContext}
            onSubmit={handleSubmit}
            disabled={sending}
          />
        </div>
      </div>
    </div>
  );
}
