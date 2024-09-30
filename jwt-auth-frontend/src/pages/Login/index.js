import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../../services/api';
import { BsEyeFill, BsEyeSlashFill } from "react-icons/bs";
import { Spin } from 'antd';
import Helmet from "react-helmet";
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false); // New state for password visibility
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await login(username, password);
      console.log(response);
      localStorage.setItem('token', response.data.access_token);
      navigate('/protected');
    } catch (error) {
      setError('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  // Function to toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <>
      <Helmet>
          <title>Login</title>
      </Helmet>
      
      <div className="login-container">
        <div className="login-box">
          <div className="login-header">
            <div className="logo">
              <svg viewBox="0 0 24 24" width="45" height="45">
                <path d="M3 3h18v18H3z" fill="#0099ff" />
                <path d="M7 7h10v2H7zm0 4h10v2H7zm0 4h7v2H7z" fill="white" />
              </svg>
            </div>
            <h1>Invoice Extract System</h1>
          </div>
          <h2>Log in</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="password-input">
                <input
                  type={showPassword ? 'text' : 'password'} // Toggle input type based on state
                  id="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <span className="password-toggle" onClick={togglePasswordVisibility}>
                  {showPassword ? <BsEyeFill /> : <BsEyeSlashFill />} {/* Change icon based on visibility */}
                </span>
              </div>
            </div>
            <button type="submit" className="login-button" disabled={loading}>
              {loading ? <Spin /> : 'Log in'}
            </button>
          </form>
          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    </>
  );
}

export default Login;