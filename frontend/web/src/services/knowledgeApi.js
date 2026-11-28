import apiClient from './apiClient';

/**
 * Knowledge Document API module (Phase 4).
 * Handles document ingestion and management.
 *
 * API Endpoints:
 * - GET    /api/v1/knowledge           - List knowledge documents
 * - GET    /api/v1/knowledge/{id}      - Get document by ID
 * - POST   /api/v1/knowledge           - Create document manually
 * - PATCH  /api/v1/knowledge/{id}      - Update document
 * - DELETE /api/v1/knowledge/{id}      - Delete document
 * - POST   /api/v1/knowledge/ingest    - Ingest document (PDF, web, manual)
 * - POST   /api/v1/knowledge/ingest/pdf - Ingest PDF file
 * - POST   /api/v1/knowledge/ingest/web - Ingest web URL
 */

export const knowledgeApi = {
  /**
   * List knowledge documents with pagination and filters.
   */
  async listDocuments(params = {}) {
    const response = await apiClient.get('/knowledge', { params });
    return response.data;
  },

  /**
   * Get a knowledge document by ID.
   */
  async getDocument(docId) {
    const response = await apiClient.get(`/knowledge/${docId}`);
    return response.data;
  },

  /**
   * Create a knowledge document manually.
   */
  async createDocument(data) {
    const response = await apiClient.post('/knowledge', data);
    return response.data;
  },

  /**
   * Update a knowledge document.
   */
  async updateDocument(docId, data) {
    const response = await apiClient.patch(`/knowledge/${docId}`, data);
    return response.data;
  },

  /**
   * Delete a knowledge document.
   */
  async deleteDocument(docId) {
    const response = await apiClient.delete(`/knowledge/${docId}`);
    return response.data;
  },

  /**
   * Ingest a document from various sources.
   */
  async ingestDocument(data) {
    const response = await apiClient.post('/knowledge/ingest', data);
    return response.data;
  },

  /**
   * Ingest a PDF file.
   */
  async ingestPDF(file, title, sourceUrl, metadataJson = '{}') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (sourceUrl) {
      formData.append('source_url', sourceUrl);
    }
    if (metadataJson) {
      formData.append('metadata_json', metadataJson);
    }

    const response = await apiClient.post('/knowledge/ingest/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /**
   * Ingest content from a web URL.
   */
  async ingestWeb(url, title, metadataJson = '{}') {
    const formData = new FormData();
    formData.append('url', url);
    formData.append('title', title);
    if (metadataJson) {
      formData.append('metadata_json', metadataJson);
    }

    const response = await apiClient.post('/knowledge/ingest/web', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

export default knowledgeApi;