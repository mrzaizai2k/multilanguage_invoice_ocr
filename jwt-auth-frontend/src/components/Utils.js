import React from 'react';
import { Link, Navigate } from 'react-router-dom';

// Navbar Component
export function Navbar() {
  return (
    <nav className="uk-navbar-container" uk-navbar="true">
      <div className="uk-navbar-left">
        <ul className="uk-navbar-nav">
          <li><Link to="/login">Login</Link></li>
          <li><Link to="/protected">Protected</Link></li>
        </ul>
      </div>
    </nav>
  );
}

// ProtectedRoute Component
export function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
