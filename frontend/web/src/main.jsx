import React from 'react';
import ReactDOM from 'react-dom/client';

// Bootstrap 5 CSS, JS bundle (needed for dropdowns/offcanvas) and icons
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css';

import './styles/variables.css';
import './styles/global.css';
import './styles/layout.css';
import './styles/responsive.css';

import App from './app/App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
