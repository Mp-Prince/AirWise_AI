import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

/**
 * Daily estimated CO2e avoided bar chart using Chart.js (Phase 7).
 */
export default function ImpactTrendChart({ trend }) {
  if (!trend || trend.length === 0) {
    return (
      <p className="text-supporting text-center py-4 mb-0">
        Log an activity above to chart your estimated daily CO2e avoided.
      </p>
    );
  }

  const data = {
    labels: trend.map((pt) => pt.date),
    datasets: [
      {
        label: 'Estimated CO2e avoided (kg)',
        data: trend.map((pt) => pt.co2e_kg),
        backgroundColor: '#176B5B',
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'top' },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'kg CO2e (estimated)' },
      },
    },
  };

  return (
    <div style={{ height: '260px' }}>
      <Bar data={data} options={options} />
    </div>
  );
}
