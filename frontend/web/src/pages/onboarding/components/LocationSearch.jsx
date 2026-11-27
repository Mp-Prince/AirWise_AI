import { useState, useEffect, useRef } from 'react';
import environmentalApi from '../../../services/environmentalApi';
import LoadingSpinner from '../../../components/common/LoadingSpinner.jsx';

/**
 * Location search component using Nominatim geocoding via backend.
 * Supports autocomplete-style search with debouncing.
 */
export default function LocationSearch({ onLocationSelect, selectedLocation, disabled = false }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const debounceRef = useRef(null);

  // Handle clicks outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target) &&
          inputRef.current && !inputRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const searchLocations = async (searchQuery) => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setResults([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await environmentalApi.searchLocations(searchQuery.trim());
      setResults(response.results || []);
    } catch (err) {
      setError('Failed to search locations');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    setShowDropdown(true);

    // Debounce search
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    debounceRef.current = setTimeout(() => {
      searchLocations(value);
    }, 300);
  };

  const handleResultClick = (location) => {
    const label = location.display_name || location.name || '';
    setQuery(label);
    setResults([]);
    setShowDropdown(false);
    if (onLocationSelect) {
      onLocationSelect(location);
    }
  };

  const handleFocus = () => {
    if (query.length >= 2 && results.length > 0) {
      setShowDropdown(true);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  // Sync input text with selected location prop
  useEffect(() => {
    if (selectedLocation) {
      const label = selectedLocation.display_name || selectedLocation.name || '';
      if (label) {
        setQuery(label);
      }
    }
  }, [selectedLocation]);

  if (disabled) {
    return (
      <div className="form-floating">
        <input
          type="text"
          className="form-control bg-light"
          value={selectedLocation?.display_name || selectedLocation?.name || ''}
          placeholder="Location"
          disabled
        />
        <label>Location (saved)</label>
      </div>
    );
  }

  return (
    <div className="position-relative" ref={dropdownRef}>
      <div className="form-floating">
        <input
          ref={inputRef}
          type="text"
          className="form-control"
          value={query}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          placeholder="Search for a city or address"
          autoComplete="off"
          aria-autocomplete="list"
          aria-controls="location-results"
          aria-expanded={showDropdown && results.length > 0}
        />
        <label>Search location</label>
      </div>

      {loading && (
        <div className="position-absolute top-0 end-0 m-2">
          <LoadingSpinner size="sm" />
        </div>
      )}

      {showDropdown && results.length > 0 && (
        <ul
          id="location-results"
          className="dropdown-menu w-100 mt-1 shadow-sm"
          style={{ maxHeight: '300px', overflowY: 'auto', zIndex: 1000 }}
          role="listbox"
        >
          {results.map((location, index) => (
            <li key={index}>
              <button
                type="button"
                className="dropdown-item d-flex flex-column align-items-start gap-1 text-start"
                onClick={() => handleResultClick(location)}
                role="option"
              >
                <strong>{location.name}</strong>
                <small className="text-supporting">
                  {location.display_name}
                </small>
                <small className="text-muted">
                  {location.lat?.toFixed(4)}, {location.lon?.toFixed(4)}
                  {location.type && ` • ${location.type}`}
                </small>
              </button>
            </li>
          ))}
        </ul>
      )}

      {showDropdown && !loading && results.length === 0 && query.length >= 2 && (
        <ul className="dropdown-menu w-100 mt-1 shadow-sm" style={{ zIndex: 1000 }}>
          <li className="dropdown-item text-center text-supporting">
            No locations found for "{query}"
          </li>
        </ul>
      )}

      {error && (
        <div className="text-danger small mt-1" role="alert">
          {error}
        </div>
      )}
    </div>
  );
}