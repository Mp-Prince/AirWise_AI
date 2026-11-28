import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LoadingSpinner from '../../components/common/LoadingSpinner.jsx';
import ragApi from '../../services/ragApi.js';
import knowledgeApi from '../../services/knowledgeApi.js';
import KnowledgeStats from './components/KnowledgeStats.jsx';
import DocumentList from './components/DocumentList.jsx';
import DocumentIngestForm from './components/DocumentIngestForm.jsx';
import KnowledgeQueryPanel from './components/KnowledgeQueryPanel.jsx';

const INITIAL_INGEST_FORM = {
  title: '',
  source_type: 'manual',
  source_url: '',
  content: '',
  file: null,
  metadata_json: '{}',
};

/**
 * Knowledge Base management page (Phase 4).
 * Follows .md/06_Frontend_Structure.md by composing feature components and services.
 */
export default function KnowledgeBasePage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('browse');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [busyDocId, setBusyDocId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [stats, setStats] = useState(null);

  const [query, setQuery] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [ingestForm, setIngestForm] = useState(INITIAL_INGEST_FORM);

  const loadData = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const [docsRes, statsRes] = await Promise.all([
        ragApi.getKnowledgeDocuments(),
        ragApi.getRAGStats(),
      ]);
      setDocuments(docsRes);
      setStats(statsRes);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load knowledge base');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleIngestFieldChange = (field, value) => {
    setIngestForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleIngest = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    let parsedMetadata = {};
    try {
      parsedMetadata = ingestForm.metadata_json.trim()
        ? JSON.parse(ingestForm.metadata_json)
        : {};
    } catch {
      setError('Metadata must be valid JSON (e.g., {"author": "WHO", "year": 2021}).');
      return;
    }

    setIngesting(true);
    try {
      let result;
      if (ingestForm.source_type === 'pdf') {
        result = await knowledgeApi.ingestPDF(
          ingestForm.file,
          ingestForm.title,
          ingestForm.source_url || undefined,
          JSON.stringify(parsedMetadata),
        );
      } else if (ingestForm.source_type === 'web') {
        result = await knowledgeApi.ingestWeb(
          ingestForm.source_url,
          ingestForm.title,
          JSON.stringify(parsedMetadata),
        );
      } else {
        result = await knowledgeApi.ingestDocument({
          title: ingestForm.title,
          source_type: 'manual',
          content: ingestForm.content,
          metadata_json: parsedMetadata,
        });
      }

      if (result.status === 'duplicate') {
        setSuccess(result.message || 'Document was already ingested.');
      } else if (result.status === 'error') {
        setError(result.message || 'Failed to ingest document.');
      } else {
        setSuccess(`Document ingested successfully! Created ${result.chunks_created} chunks.`);
        setIngestForm(INITIAL_INGEST_FORM);
      }
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to ingest document');
    } finally {
      setIngesting(false);
    }
  };

  const handleToggleActive = async (doc) => {
    setBusyDocId(doc.id);
    setError(null);
    try {
      await knowledgeApi.updateDocument(doc.id, { is_active: !doc.is_active });
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update document status');
    } finally {
      setBusyDocId(null);
    }
  };

  const handleDelete = async (doc) => {
    if (!window.confirm(`Delete "${doc.title}" and its chunks?`)) return;
    setBusyDocId(doc.id);
    setError(null);
    try {
      await knowledgeApi.deleteDocument(doc.id);
      setSuccess(`Deleted "${doc.title}".`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete document');
    } finally {
      setBusyDocId(null);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setQuerying(true);
    setError(null);
    try {
      const result = await ragApi.queryRAG({ query, top_k: 5 });
      setQueryResults(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Query failed');
    } finally {
      setQuerying(false);
    }
  };

  if (loading) {
    return (
      <div className="container-fluid px-3 px-lg-4">
        <PageHeader title="Knowledge Base" subtitle="Manage RAG documents and test retrieval." />
        <div className="text-center py-5">
          <LoadingSpinner size="lg" />
          <p className="text-supporting mt-2">Loading knowledge base...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader title="Knowledge Base" subtitle="Manage RAG documents and test retrieval." />

      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
      {success && (
        <div className="alert alert-success alert-dismissible fade show mb-3" role="alert">
          <i className="bi bi-check-circle me-1" aria-hidden="true" />
          {success}
          <button type="button" className="btn-close" onClick={() => setSuccess(null)} aria-label="Close" />
        </div>
      )}

      <KnowledgeStats stats={stats} />

      <div className="card shadow-sm">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs" role="tablist">
            <li className="nav-item">
              <button
                className={'nav-link' + (activeTab === 'browse' ? ' active' : '')}
                type="button"
                role="tab"
                onClick={() => setActiveTab('browse')}
              >
                <i className="bi bi-folder2-open me-1" aria-hidden="true" />
                Browse
              </button>
            </li>
            <li className="nav-item">
              <button
                className={'nav-link' + (activeTab === 'ingest' ? ' active' : '')}
                type="button"
                role="tab"
                onClick={() => setActiveTab('ingest')}
              >
                <i className="bi bi-cloud-upload me-1" aria-hidden="true" />
                Ingest
              </button>
            </li>
            <li className="nav-item">
              <button
                className={'nav-link' + (activeTab === 'query' ? ' active' : '')}
                type="button"
                role="tab"
                onClick={() => setActiveTab('query')}
              >
                <i className="bi bi-search me-1" aria-hidden="true" />
                Query
              </button>
            </li>
          </ul>
        </div>
        <div className="card-body">
          {activeTab === 'browse' && (
            <DocumentList
              documents={documents}
              busyDocId={busyDocId}
              onToggleActive={handleToggleActive}
              onDelete={handleDelete}
            />
          )}

          {activeTab === 'ingest' && (
            <DocumentIngestForm
              form={ingestForm}
              onChange={handleIngestFieldChange}
              onSubmit={handleIngest}
              ingesting={ingesting}
            />
          )}

          {activeTab === 'query' && (
            <KnowledgeQueryPanel
              query={query}
              onQueryChange={setQuery}
              onSubmit={handleQuery}
              querying={querying}
              results={queryResults}
            />
          )}
        </div>
      </div>
    </div>
  );
}
