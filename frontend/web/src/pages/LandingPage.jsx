import { Link } from 'react-router-dom';

/** Public landing page: explains the product and offers login/register. */
export default function LandingPage() {
  return (
    <div className="container py-5">
      <div className="row justify-content-center text-center">
        <div className="col-lg-8">
          <img src="/favicon.svg" alt="" width="56" height="56" className="mb-3" />
          <h1 className="page-title display-6">AirWise AI</h1>
          <p className="fs-5 text-supporting">
            Check air quality and weather before you step out, plan safer routines, and
            understand the impact of greener choices.
          </p>
          <div className="d-flex flex-column flex-sm-row justify-content-center gap-2 mt-4">
            <Link to="/register" className="btn btn-primary btn-lg">
              Get started
            </Link>
            <Link to="/login" className="btn btn-outline-primary btn-lg">
              Log in
            </Link>
          </div>
        </div>
      </div>
      <div className="row g-4 mt-5">
        {[
          {
            icon: 'bi-wind',
            title: 'Know before you go',
            text: 'Current AQI and weather for your area, with freshness labels and clear sources.',
          },
          {
            icon: 'bi-calendar3',
            title: 'Plan smarter days',
            text: 'Run your errands and workouts during the cleanest, safest hours.',
          },
          {
            icon: 'bi-lightbulb',
            title: 'Personal guidance',
            text: 'AI recommendations grounded in trusted environmental documents — with citations.',
          },
        ].map((f) => (
          <div className="col-md-4" key={f.title}>
            <div className="card h-100 shadow-sm">
              <div className="card-body">
                <i className={`bi ${f.icon} fs-2 text-primary`} aria-hidden="true" />
                <h2 className="card-title h5 mt-2">{f.title}</h2>
                <p className="card-text text-supporting">{f.text}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
