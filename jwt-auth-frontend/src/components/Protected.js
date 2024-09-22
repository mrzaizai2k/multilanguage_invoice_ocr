import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../services/api';
import { useNavigate } from 'react-router-dom';

function Protected() {
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get(`${API_URL}/users/me`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        setUserData(response.data);

        // Redirect based on admin status
        if (response.data.is_admin) {
          navigate('/admin-dashboard'); // Admin dashboard route
        } else {
          navigate('/user-dashboard'); // User dashboard route
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };
    fetchUserData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  return (
    <div className="uk-container uk-container-xsmall">
      <h1 className="uk-heading-small uk-margin-medium-top">Protected Page</h1>
      {userData ? (
        <>
          <p>Welcome, {userData.username}!</p>
        </>
      ) : (
        <p>Loading user data...</p>
      )}
      <button className="uk-button uk-button-danger" onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Protected;
