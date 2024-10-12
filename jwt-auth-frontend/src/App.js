import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/Utils';
import { Spin } from 'antd';

// Lazy loading components
const Login = lazy(() => import('./pages/Login'));
const Protected = lazy(() => import('./components/Protected'));
const UserDashboard = lazy(() => import('./pages/UserDashboard'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));

function App() {
  return (
    <Router>
      <Suspense fallback={<div style={{ display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column", height: "100vh" }}>
        <h1 style={{color: "#0099ff"}}>System zur Spesenabrechnung V 1.0</h1><br/>
        <Spin size="large"/>
      </div>}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <Protected />
              </ProtectedRoute>
            }
          />
          <Route path="/user-dashboard" element={<UserDashboard />} />
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

export default App;
