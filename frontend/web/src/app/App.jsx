import { BrowserRouter } from 'react-router-dom';
import AppRouter from './router.jsx';
import { AuthProvider } from './providers/AuthProvider.jsx';
import QueryProvider from './providers/QueryProvider.jsx';

/**
 * Root component. Providers compose here; routing lives in router.jsx.
 * BrowserRouter must wrap everything that uses router hooks
 * (Routes/NavLink/useLocation), including the providers below.
 */
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <QueryProvider>
          <AppRouter />
        </QueryProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
