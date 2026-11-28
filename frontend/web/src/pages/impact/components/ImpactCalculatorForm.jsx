import { useState } from 'react';
import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Transport & energy impact calculator and activity logger (Phase 7).
 */
export default function ImpactCalculatorForm({ factors, onPreview, onLog, saving }) {
  const transportFactors = factors.filter((f) => f.unit.includes('km'));

  const [form, setForm] = useState({
    activity_category: 'transport',
    baseline_mode: 'petrol_car',
    alternative_mode: 'metro_rail',
    quantity: '10',
    passengers: '1',
    description: '',
  });
  const [preview, setPreview] = useState(null);
  const [previewing, setPreviewing] = useState(false);

  const buildPayload = () => ({
    activity_category: form.activity_category,
    baseline_mode: form.baseline_mode,
    alternative_mode: form.alternative_mode,
    quantity: parseFloat(form.quantity),
    passengers: parseInt(form.passengers || '1', 10),
    description: form.description.trim() || null,
  });

  const handlePreview = async () => {
    if (!form.quantity || parseFloat(form.quantity) <= 0) return;
    setPreviewing(true);
    try {
      const res = await onPreview(buildPayload());
      setPreview(res);
    } finally {
      setPreviewing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.quantity || parseFloat(form.quantity) <= 0) return;
    await onLog(buildPayload());
    setPreview(null);
    setForm((p) => ({ ...p, description: '' }));
  };

  return (
    <div className="card shadow-sm mb-3">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h2 className="section-heading mb-0">Log Sustainable Activity & Calculator</h2>
          <span className="badge text-bg-light border">Estimates only</span>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="row g-2 mb-3">
            <div className="col-12 col-md-3">
              <label className="form-label small" htmlFor="impact-cat">Activity Type</label>
              <select
                id="impact-cat"
                className="form-select form-select-sm"
                value={form.activity_category}
                onChange={(e) => {
                  setForm((p) => ({ ...p, activity_category: e.target.value }));
                  setPreview(null);
                }}
              >
                <option value="transport">Transport Mode Shift</option>
                <option value="electricity">Electricity Saved (kWh)</option>
              </select>
            </div>

            {form.activity_category === 'transport' && (
              <>
                <div className="col-12 col-md-3">
                  <label className="form-label small" htmlFor="impact-base">Replaced Mode</label>
                  <select
                    id="impact-base"
                    className="form-select form-select-sm"
                    value={form.baseline_mode}
                    onChange={(e) => setForm((p) => ({ ...p, baseline_mode: e.target.value }))}
                  >
                    {transportFactors.map((f) => (
                      <option key={f.activity} value={f.activity}>
                        {f.activity.replace(/_/g, ' ')} ({f.co2e_kg_per_unit} {f.unit})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-12 col-md-3">
                  <label className="form-label small" htmlFor="impact-alt">Chosen Mode</label>
                  <select
                    id="impact-alt"
                    className="form-select form-select-sm"
                    value={form.alternative_mode}
                    onChange={(e) => setForm((p) => ({ ...p, alternative_mode: e.target.value }))}
                  >
                    {transportFactors.map((f) => (
                      <option key={f.activity} value={f.activity}>
                        {f.activity.replace(/_/g, ' ')} ({f.co2e_kg_per_unit} {f.unit})
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            <div className="col-6 col-md-2">
              <label className="form-label small" htmlFor="impact-qty">
                {form.activity_category === 'electricity' ? 'Saved (kWh)' : 'Distance (km)'}
              </label>
              <input
                id="impact-qty"
                type="number"
                step="0.1"
                min="0.1"
                className="form-control form-control-sm"
                value={form.quantity}
                onChange={(e) => setForm((p) => ({ ...p, quantity: e.target.value }))}
                required
              />
            </div>

            {form.activity_category === 'transport' && (
              <div className="col-6 col-md-1">
                <label className="form-label small" htmlFor="impact-pax">Pax</label>
                <input
                  id="impact-pax"
                  type="number"
                  min="1"
                  max="60"
                  className="form-control form-control-sm"
                  value={form.passengers}
                  onChange={(e) => setForm((p) => ({ ...p, passengers: e.target.value }))}
                  title="Shared occupancy divisor (e.g., 2 for carpooling)"
                />
              </div>
            )}
          </div>

          <div className="row g-2 align-items-end">
            <div className="col-12 col-md-8">
              <label className="form-label small" htmlFor="impact-desc">Notes (optional)</label>
              <input
                id="impact-desc"
                type="text"
                className="form-control form-control-sm"
                value={form.description}
                onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                placeholder="e.g., Took metro instead of petrol car to college"
              />
            </div>
            <div className="col-12 col-md-4 d-flex gap-2 justify-content-md-end">
              <button
                type="button"
                className="btn btn-outline-secondary btn-sm"
                onClick={handlePreview}
                disabled={previewing || saving}
              >
                {previewing ? 'Calculating...' : 'Preview Estimate'}
              </button>
              <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>
                {saving ? (
                  <>
                    <LoadingSpinner size="sm" className="me-1" /> Saving...
                  </>
                ) : (
                  'Log Activity'
                )}
              </button>
            </div>
          </div>
        </form>

        {preview && (
          <div className="alert alert-info mt-3 mb-0 small">
            <strong>Estimated CO2e avoided: {preview.co2e_saved_kg.toFixed(3)} kg CO2e</strong>{' '}
            (Baseline {preview.baseline_co2e_kg.toFixed(3)} kg − Alternative {preview.alternative_co2e_kg.toFixed(3)} kg)
            <div className="text-muted mt-1">{preview.note}</div>
          </div>
        )}
      </div>
    </div>
  );
}
