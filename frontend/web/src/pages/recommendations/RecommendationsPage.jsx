import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LoadingSpinner from '../../components/common/LoadingSpinner.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import recommendationService from '../../services/recommendationService.js';
import RecommendationFilters from './components/RecommendationFilters.jsx';
import RecommendationCard from './components/RecommendationCard.jsx';
import RecommendationDetailsModal from './components/RecommendationDetailsModal.jsx';

/**
 * Recommendations feed (page workflows doc, section 7): deterministic
 * safety rules + sustainable actions with accept, dismiss, and add-to-planner.
 */
export default function RecommendationsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [aqiContext, setAqiContext] = useState(null);
  const [category, setCategory] = useState('');
  const [statusFilter, setStatusFilter] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [selectedRec, setSelectedRec] = useState(null);

  const loadRecommendations = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (category) params.category = category;
      if (statusFilter) params.status = statusFilter;

      const res = await recommendationService.listRecommendations(params);
      setRecommendations(res.recommendations || []);
      setAqiContext(
        res.aqi_value !== null && res.aqi_value !== undefined
          ? { value: res.aqi_value, standard: res.aqi_standard }
          : null,
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  }, [user, category, statusFilter]);

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    setSuccess(null);
    try {
      const created = await recommendationService.generateRecommendations();
      setSuccess(
        created.length > 0
          ? `Generated ${created.length} new recommendation(s).`
          : 'Your recommendations are already up to date.',
      );
      await loadRecommendations();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to refresh recommendations');
    } finally {
      setGenerating(false);
    }
  };

  const handleAccept = async (rec) => {
    setBusyId(rec.id);
    setError(null);
    try {
      await recommendationService.acceptRecommendation(rec.id);
      setSuccess(`Marked "${rec.title}" as done.`);
      await loadRecommendations();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept recommendation');
    } finally {
      setBusyId(null);
    }
  };

  const handleDismiss = async (rec) => {
    setBusyId(rec.id);
    setError(null);
    try {
      await recommendationService.dismissRecommendation(rec.id);
      await loadRecommendations();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to dismiss recommendation');
    } finally {
      setBusyId(null);
    }
  };

  const handleAddToPlanner = async (rec) => {
    setBusyId(rec.id);
    setError(null);
    try {
      const today = new Date().toISOString().slice(0, 10);
      const routineType =
        rec.category === 'eco'
          ? 'commute'
          : rec.category === 'lifestyle'
          ? 'indoor_air'
          : 'exercise';
      await recommendationService.addToPlanner(rec.id, {
        routine_date: today,
        start_time: '08:00:00',
        end_time: '08:30:00',
        routine_type: routineType,
        reminder_minutes: 15,
      });
      setSuccess(`Added "${rec.title}" to today's Daily Planner.`);
      await loadRecommendations();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add to planner');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Recommendations"
        subtitle="Personalised, evidence-backed suggestions for cleaner air days."
        actions={
          aqiContext ? (
            <span className="badge text-bg-light border">
              Local AQI: {aqiContext.value} ({aqiContext.standard})
            </span>
          ) : (
            <span className="badge text-bg-secondary">AQI unavailable</span>
          )
        }
      />

      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
      {success && (
        <div className="alert alert-success alert-dismissible fade show mb-3" role="alert">
          {success}{' '}
          <button
            type="button"
            className="btn btn-link btn-sm p-0 ms-2"
            onClick={() => navigate('/planner')}
          >
            Open Planner
          </button>
          <button
            type="button"
            className="btn-close"
            onClick={() => setSuccess(null)}
            aria-label="Close"
          />
        </div>
      )}

      <RecommendationFilters
        category={category}
        status={statusFilter}
        onCategoryChange={setCategory}
        onStatusChange={setStatusFilter}
        onGenerate={handleGenerate}
        generating={generating}
      />

      {loading ? (
        <div className="text-center py-5">
          <LoadingSpinner size="lg" />
          <p className="text-supporting mt-2 mb-0">Loading recommendations...</p>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="card shadow-sm">
          <div className="card-body">
            <EmptyState
              icon="bi-lightbulb"
              title="No matching recommendations"
              message="Try changing your filters or click Refresh Suggestions to generate personalized health and eco actions."
              action={
                <button type="button" className="btn btn-outline-primary" onClick={handleGenerate}>
                  Refresh Suggestions
                </button>
              }
            />
          </div>
        </div>
      ) : (
        <div className="row g-3">
          {recommendations.map((rec) => (
            <div className="col-12 col-md-6 col-xl-4" key={rec.id}>
              <RecommendationCard
                rec={rec}
                busyId={busyId}
                onAccept={handleAccept}
                onDismiss={handleDismiss}
                onAddToPlanner={handleAddToPlanner}
                onViewDetails={setSelectedRec}
              />
            </div>
          ))}
        </div>
      )}

      <RecommendationDetailsModal rec={selectedRec} onClose={() => setSelectedRec(null)} />
    </div>
  );
}
