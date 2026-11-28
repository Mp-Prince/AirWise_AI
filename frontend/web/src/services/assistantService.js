import apiClient from './apiClient';

/**
 * AI Assistant API service (Phase 5).
 * Matches .md/03_Page_Workflows.md section 6 and .md/06_Frontend_Structure.md.
 */
export const assistantService = {
  async sendMessage({ conversation_id = null, message, include_user_context = true }) {
    const response = await apiClient.post(
      '/assistant/chat',
      {
        conversation_id,
        message,
        include_user_context,
      },
      { timeout: 60000 },
    );
    return response.data;
  },

  async getConversations() {
    const response = await apiClient.get('/assistant/conversations');
    return response.data;
  },

  async getConversation(conversationId) {
    const response = await apiClient.get(`/assistant/conversations/${conversationId}`);
    return response.data;
  },

  async deleteConversation(conversationId) {
    await apiClient.delete(`/assistant/conversations/${conversationId}`);
  },

  async submitFeedback({ message_id, helpful, comment = null }) {
    const response = await apiClient.post('/assistant/feedback', {
      message_id,
      helpful,
      comment,
    });
    return response.data;
  },

  async getUsage() {
    const response = await apiClient.get('/assistant/usage');
    return response.data;
  },
};

export default assistantService;
