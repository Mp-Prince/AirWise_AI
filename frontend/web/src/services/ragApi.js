import apiClient from './apiClient';

/**
 * RAG API module (Phase 4).
 * Provides access to RAG knowledge base endpoints.
 *
 * API Endpoints:
 * - POST /api/v1/rag/query       - RAG-powered query (retrieval)
 * - GET  /api/v1/rag/documents   - List knowledge documents
 * - GET  /api/v1/rag/stats       - RAG statistics
 */

export const ragApi = {
  /**
   * Query the RAG system for relevant documents.
   * Returns retrieved chunks with citations (Phase 4).
   * Phase 5 will add LLM answer generation.
   */
  async queryRAG(data) {
    const response = await apiClient.post('/rag/query', data);
    return response.data;
  },

  /**
   * Get list of knowledge documents in the RAG system.
   */
  async getKnowledgeDocuments() {
    const response = await apiClient.get('/rag/documents');
    return response.data;
  },

  /**
   * Get RAG knowledge base statistics.
   */
  async getRAGStats() {
    const response = await apiClient.get('/rag/stats');
    return response.data;
  },
};

export default ragApi;