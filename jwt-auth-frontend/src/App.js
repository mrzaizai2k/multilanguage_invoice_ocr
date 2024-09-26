import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/Utils';
import { Spin } from 'antd';

// Lazy loading components
const Login = lazy(() => import('./components/Login/Login'));
const Protected = lazy(() => import('./components/Protected'));
const UserDashboard = lazy(() => import('./components/UserDashboard'));
const AdminDashboard = lazy(() => import('./components/AdminDashboard'));

function App() {
  return (
    <Router>
      <Suspense fallback={<div style={{ display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column", height: "100vh" }}>
        <h1 style={{color: "#0099ff"}}>Invoice Extract System</h1><br/>
        <Spin tip="Loading..." size="large" />
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
