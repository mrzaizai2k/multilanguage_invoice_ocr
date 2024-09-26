import React, { useState, useCallback, useEffect, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './UserDashboard.css';
import { API_URL } from '../../services/api';
import { MdUploadFile, MdLogout, MdOutlinePersonOutline } from "react-icons/md";
import { BsFileEarmarkRichtext } from "react-icons/bs";
import InvoiceList from './pages/InvoiceList';
import AddInvoice from './pages/AddInovice';
import UserInfo from './pages/UserInfo';

// Memoized components
const MemoizedUserInfo = memo(UserInfo);
const MemoizedInvoiceList = memo(InvoiceList);
const MemoizedAddInvoice = memo(AddInvoice); // Memoize AddInvoice component


function UserDashboard() {
  const [activeTab, setActiveTab] = useState('userInfo');
  const [userData, setUserData] = useState(null); // State for user data
  const navigate = useNavigate();

  // Fetch user data on component mount
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get(`${API_URL}/users/me`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        setUserData(response.data);
      } catch (error) {
        console.error("Error fetching user data", error);
        // Handle error, maybe log out or show an error message
      }
    };

    fetchUserData();
  }, [navigate]);

  // Memoize the tab change handler
  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
  }, []);

  // Memoize the logout handler
  const handleLogout = useCallback(() => {
    localStorage.removeItem('token'); // Clear token on logout
    navigate('/login');
  }, [navigate]);

  // Memoize the content displayed based on the active tab
  const tabContent = React.useMemo(() => {
    switch (activeTab) {
      case 'userInfo':
        return <MemoizedUserInfo userData={userData} />;
      case 'invoice':
        return <MemoizedInvoiceList />;
      case 'addInvoice':
        return <MemoizedAddInvoice username={userData?.username} />;
      default:
        return null;
    }
  }, [activeTab, userData]);

  return (
    <div className="dashboard">
      <Sidebar 
        activeTab={activeTab} 
        onTabChange={handleTabChange} 
        onLogout={handleLogout} 
      />
      <div className="content">
        {tabContent}
      </div>
    </div>
  );
}

// Separate Sidebar component
const Sidebar = memo(({ activeTab, onTabChange, onLogout }) => (
  <div className="sidebar">
    <h1>Invoice Extract System</h1>
    <SidebarButton 
      active={activeTab === 'userInfo'} 
      onClick={() => onTabChange('userInfo')}
      icon={<MdOutlinePersonOutline  />}
      text="User Info"
    />
    <SidebarButton 
      active={activeTab === 'invoice'} 
      onClick={() => onTabChange('invoice')}
      icon={<BsFileEarmarkRichtext />}
      text="Invoice"
    />
    <SidebarButton 
      active={activeTab === 'addInvoice'} 
      onClick={() => onTabChange('addInvoice')}
      icon={<MdUploadFile />}
      text="Add Invoice"
    />
    <SidebarButton 
      className="logout"
      onClick={onLogout}
      icon={<MdLogout />}
      text="Logout"
    />
  </div>
));

// Reusable SidebarButton component
const SidebarButton = memo(({ active, onClick, icon, text, className = '' }) => (
  <button 
    className={`${active ? 'active' : ''} ${className}`} 
    onClick={onClick}
  >
    <span className="icon">{icon}</span> {text}
  </button>
));

export default UserDashboard;
