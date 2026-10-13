import React from 'react';
import ReactDOM from 'react-dom/client';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';
import App from './App';

// Django session authentication uses CSRF enforcement for state-changing
// requests. The backend sets the csrftoken cookie on GET /api/user/ (which
// the app already calls on load); axios then sends it back as X-CSRFToken on
// same-origin POSTs (login, register, logout, reviews). This covers the
// first anonymous login/registration request too.
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
