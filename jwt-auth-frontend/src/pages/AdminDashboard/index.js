import React, { useState, useCallback, useEffect, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AdminDashboard.css';
import { API_URL } from '../../services/api';
import { MdUploadFile, MdLogout, MdOutlinePersonOutline } from "react-icons/md";
import { BsFileEarmarkRichtext } from "react-icons/bs";
import { Helmet } from 'react-helmet';
import AddInvoice from '../../components/AddInovice';
import UserInfo from '../../components/UserInfo';
import InvoiceList from './InvoiceList';
import { Modal } from 'antd';

const MemoizedUserInfo = memo(UserInfo);
const MemoizedInvoiceList = memo(InvoiceList);
const MemoizedAddInvoice = memo(AddInvoice);

const { confirm } = Modal;

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('userInfo');
  const [userData, setUserData] = useState(null);
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

  // Show logout confirmation
  const showLogoutConfirm = () => {
    confirm({
      title: 'Are you sure you want to logout?',
      okText: 'Yes',
      okType: 'danger',
      cancelText: 'No',
      onOk: () => {
        localStorage.removeItem('token');
        navigate('/login');
      },
      onCancel() {
        console.log('Cancel');
      },
    });
  };

  const tabContent = React.useMemo(() => {
    switch (activeTab) {
      case 'userInfo':
        return <MemoizedUserInfo userData={userData} title="Admin Information" />;
      case 'invoice':
        return <MemoizedInvoiceList userData={userData?.username} />;
      case 'addInvoice':
        return <MemoizedAddInvoice username={userData?.username} />;
      default:
        return null;
    }
  }, [activeTab, userData]);

  return (
    <>
      <Helmet>
        <title>Invoice Extract System - AdminInfo</title>
      </Helmet>

      <div className="dashboard">
        <Sidebar
          activeTab={activeTab}
          onTabChange={handleTabChange}
          onLogout={showLogoutConfirm}
        />
        <div className="content">
          {tabContent}
        </div>
      </div>
    </>
  );
}

const Sidebar = memo(({ activeTab, onTabChange, onLogout }) => (
  <div className="sidebar">
    <h1 style={{ cursor: "default" }}>Invoice Extract System</h1>
    <div className="menu__list">
      <SidebarButton
        active={activeTab === 'userInfo'}
        onClick={() => onTabChange('userInfo')}
        icon={<MdOutlinePersonOutline />}
        text="Admin Info"
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

export default AdminDashboard;