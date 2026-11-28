/**
 * Timezone-safe local calendar date utilities (YYYY-MM-DD).
 * Avoids `.toISOString().slice(0, 10)` which shifts dates to UTC.
 */

export function toLocalIsoDate(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function parseLocalIsoDate(isoDate) {
  const [y, m, d] = String(isoDate).split('-').map(Number);
  return new Date(y, (m || 1) - 1, d || 1);
}

export function addDaysIso(isoDate, offset) {
  const d = parseLocalIsoDate(isoDate);
  d.setDate(d.getDate() + offset);
  return toLocalIsoDate(d);
}

export function getWeekStartIso(isoDate) {
  const d = parseLocalIsoDate(isoDate);
  const mondayOffset = (d.getDay() + 6) % 7; // 0=Mon .. 6=Sun
  d.setDate(d.getDate() - mondayOffset);
  return toLocalIsoDate(d);
}
