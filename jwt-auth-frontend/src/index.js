import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css'; // Optional for styles
import './components/Login.css'; // Optional for styles

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
