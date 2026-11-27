import { useState, useEffect } from 'react';
import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';
import LocationSearch from '../../onboarding/components/LocationSearch.jsx';

/**
 * Location tab component for Profile page.
 * Handles location management (list, add, delete, set default).
 */
export default function LocationTab({
  locations,
  loading,
  selectedLocation,
  handleLocationSelect,
  handleSaveLocation,
  handleSetDefaultLocation,
  handleDeleteLocation,
  saving,
}) {
  if (loading) {
    return (
      <div className="text-center py-5">
        <LoadingSpinner size="lg" />
        <p className="text-supporting mt-2">Loading locations...</p>
      </div>
    );
  }

  return (
    <div>
      <h5 className="card-title mb-3">Saved Locations</h5>

      {locations.length > 0 ? (
        <div className="table-responsive mb-4">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th>Name</th>
                <th>City / State</th>
                <th>Coordinates</th>
                <th>Default</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {locations.map(loc => (
                <tr key={loc.id}>
                  <td>{loc.name}</td>
                  <td>
                    {loc.city && <span>{loc.city}</span>}
                    {loc.city && loc.state && <span className="text-muted">, </span>}
                    {loc.state && <span>{loc.state}</span>}
                    {loc.country && <span className="text-muted ms-1">({loc.country})</span>}
                  </td>
                  <td className="text-muted small">
                    {loc.lat?.toFixed(4)}, {loc.lon?.toFixed(4)}
                  </td>
                  <td>
                    {loc.is_default ? (
                      <span className="badge text-bg-success">Default</span>
                    ) : (
                      <button
                        className="btn btn-outline-primary btn-sm"
                        onClick={() => handleSetDefaultLocation(loc.id)}
                        disabled={saving}
                      >
                        Set Default
                      </button>
                    )}
                  </td>
                  <td>
                    {!loc.is_default && (
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleDeleteLocation(loc.id)}
                        disabled={saving}
                      >
                        <svg className="bi" width="16" height="16"><use xlinkHref="#trash" /></svg>
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-supporting">No locations saved yet.</p>
      )}

      <hr className="my-4" />
      <h5 className="card-title mb-3">Add New Location</h5>
      <p className="text-supporting mb-4">
        Search for a city or address to save as a location for air quality and weather monitoring.
      </p>
      <LocationSearch
        onLocationSelect={handleLocationSelect}
        selectedLocation={selectedLocation}
      />
      {selectedLocation && (
        <div className="alert alert-success mt-3 mb-0 small">
          <svg className="bi me-1" width="16" height="16"><use xlinkHref="#check-circle" /></svg>
          Selected: <strong>{selectedLocation.display_name}</strong>
          <div className="text-muted mt-1">
            Coordinates: {selectedLocation.lat?.toFixed(4)}, {selectedLocation.lon?.toFixed(4)}
            {selectedLocation.city && ` • City: ${selectedLocation.city}`}
            {selectedLocation.state && ` • State: ${selectedLocation.state}`}
            {selectedLocation.country && ` • Country: ${selectedLocation.country}`}
          </div>
        </div>
      )}
      <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-3">
        <button
          className="btn btn-primary"
          onClick={handleSaveLocation}
          disabled={saving || !selectedLocation}
        >
          {saving ? (
            <>
              <LoadingSpinner size="sm" className="me-2" />
              Saving...
            </>
          ) : (
            'Save Location'
          )}
        </button>
      </div>
    </div>
  );
}