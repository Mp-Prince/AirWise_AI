import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../app/providers/AuthProvider.jsx';
import PageHeader from '../../components/common/PageHeader.jsx';
import ErrorAlert from '../../components/common/ErrorAlert.jsx';
import LoadingSpinner from '../../components/common/LoadingSpinner.jsx';
import ImpactTrendChart from '../../components/charts/ImpactTrendChart.jsx';
import impactService from '../../services/impactService.js';
import { toLocalIsoDate } from '../../utils/dateUtils.js';
import ImpactMetricCard from './components/ImpactMetricCard.jsx';
import ImpactDateFilter from './components/ImpactDateFilter.jsx';
import ImpactCalculatorForm from './components/ImpactCalculatorForm.jsx';
import ImpactBreakdown from './components/ImpactBreakdown.jsx';
import CalculationDetailsModal from './components/CalculationDetailsModal.jsx';

/**
 * Impact tracker (page workflows doc, section 8): reproducible CO2e
 * estimates with stored factor snapshots, assumptions, and Chart.js trend.
 */
export default function ImpactTrackerPage() {
  const { user } = useAuth();
  const [period, setPeriod] = useState('30d');
  const [customFrom, setCustomFrom] = useState(() => toLocalIsoDate());
  const [customTo, setCustomTo] = useState(() => toLocalIsoDate());
  const [factors, setFactors] = useState([]);
  const [summary, setSummary] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);

  const loadData = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const rangeParams =
        period === 'custom'
          ? { from: customFrom, to: customTo }
          : { period };

      const [factorsRes, summaryRes, recordsRes] = await Promise.all([
        impactService.getFactors(),
        impactService.getSummary(rangeParams),
        impactService.getRecords(rangeParams),
      ]);
      setFactors(factorsRes.factors || []);
      setSummary(summaryRes);
      setRecords(recordsRes.records || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load impact data');
    } finally {
      setLoading(false);
    }
  }, [user, period, customFrom, customTo]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleLogActivity = async (payload) => {
    setSaving(true);
    setError(null);
    try {
      await impactService.logActivity(payload);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to log activity');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteRecord = async (rec) => {
    if (!window.confirm('Delete this logged impact record?')) return;
    setBusyId(rec.id);
    setError(null);
    try {
      await impactService.deleteRecord(rec.id);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete record');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="container-fluid px-3 px-lg-4">
      <PageHeader
        title="Impact Tracker"
        subtitle="Estimated CO2e avoided from your transport and energy choices."
      />

      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

      <ImpactCalculatorForm
        factors={factors}
        onPreview={impactService.calculatePreview}
        onLog={handleLogActivity}
        saving={saving}
      />

      <ImpactDateFilter
        period={period}
        customFrom={customFrom}
        customTo={customTo}
        onPeriodChange={setPeriod}
        onCustomFromChange={setCustomFrom}
        onCustomToChange={setCustomTo}
      />

      {loading ? (
        <div className="text-center py-5">
          <LoadingSpinner size="lg" />
          <p className="text-supporting mt-2 mb-0">Loading impact summary...</p>
        </div>
      ) : (
        <>
          <div className="row g-3 mb-3">
            <div className="col-12 col-md-4">
              <ImpactMetricCard
                label="CO2e avoided"
                value={summary ? summary.total_co2e_avoided_kg.toFixed(2) : '0.00'}
                unit="kg CO2e"
                hint="Calculated from published emission factor snapshots"
                badgeText="Estimated"
              />
            </div>
            <div className="col-12 col-md-4">
              <ImpactMetricCard
                label="Activities logged"
                value={summary ? summary.total_activities : 0}
                hint={`Baseline ${(summary?.total_baseline_co2e_kg || 0).toFixed(2)} kg → ${(summary?.total_alternative_co2e_kg || 0).toFixed(2)} kg`}
                badgeText="Logged"
              />
            </div>
            <div className="col-12 col-md-4">
              <ImpactMetricCard
                label="Active streak"
                value={summary ? summary.active_days_streak : 0}
                unit="day(s)"
                hint="Consecutive days with logged eco actions"
                badgeText="Streak"
              />
            </div>
          </div>

          <div className="card shadow-sm mb-3">
            <div className="card-body">
              <h2 className="section-heading mb-3">CO2e Savings Trend (Estimated)</h2>
              <ImpactTrendChart trend={summary?.trend || []} />
            </div>
          </div>

          {summary?.disclaimer && (
            <div className="alert alert-light border small mb-3">
              <i className="bi bi-info-circle me-1" aria-hidden="true" />
              {summary.disclaimer}
            </div>
          )}

          <ImpactBreakdown
            breakdown={summary?.breakdown || []}
            records={records}
            onViewCalculation={setSelectedRecord}
            onDeleteRecord={handleDeleteRecord}
            busyId={busyId}
          />
        </>
      )}

      <CalculationDetailsModal
        record={selectedRecord}
        onClose={() => setSelectedRecord(null)}
      />
    </div>
  );
}
