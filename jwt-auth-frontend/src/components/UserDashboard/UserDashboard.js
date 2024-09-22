import React, { useState, useCallback, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import './UserDashboard.css';

// Memoized components
const MemoizedUserInfo = memo(UserInfo);
const MemoizedInvoiceList = memo(InvoiceList);
const MemoizedAddInvoice = memo(AddInvoice);

function UserDashboard() {
  const [activeTab, setActiveTab] = useState('userInfo');
  const navigate = useNavigate();

  // Use useCallback to memoize these functions
  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
  }, []);

  const handleLogout = useCallback(() => {
    navigate('/login');
  }, [navigate]);

  // Memoize the tab content
  const tabContent = React.useMemo(() => {
    switch (activeTab) {
      case 'userInfo':
        return <MemoizedUserInfo />;
      case 'invoice':
        return <MemoizedInvoiceList />;
      case 'addInvoice':
        return <MemoizedAddInvoice />;
      default:
        return null;
    }
  }, [activeTab]);

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
      icon="👤"
      text="User Info"
    />
    <SidebarButton 
      active={activeTab === 'invoice'} 
      onClick={() => onTabChange('invoice')}
      icon="📄"
      text="Invoice"
    />
    <SidebarButton 
      active={activeTab === 'addInvoice'} 
      onClick={() => onTabChange('addInvoice')}
      icon="➕"
      text="Add Invoice"
    />
    <SidebarButton 
      className="logout"
      onClick={onLogout}
      icon="🚪"
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

function UserInfo({ userData }) {
  if (!userData) return <p>Loading...</p>;

  return (
    <div className="user-info">
      <h2>User Information</h2>
      <p><strong>Name:</strong> {userData.name}</p>
      <p><strong>Role:</strong> {userData.is_admin ? 'Admin' : 'User'}</p>
    </div>
  );
}

function InvoiceList() {
  return <h2>Invoice List</h2>;
}

function AddInvoice() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = useCallback((event) => {
    setSelectedFile(event.target.files[0]);
  }, []);

  const handleUpload = useCallback(async () => {
    if (!selectedFile) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    // Upload logic here
  }, [selectedFile]);

  return (
    <div className="add-invoice">
      <div className="drop-zone">
        <div className="icon">↑</div>
        <p>Drag and drop your image here or</p>
        <input type="file" accept=".jpg,.png,.pdf" onChange={handleFileChange} />
        <button className="browse-btn" onClick={handleUpload}>
          Upload File
        </button>
        <div className="file-types">
          <span>JPG</span>
          <span>PNG</span>
          <span>PDF</span>
        </div>
      </div>
    </div>
  );
}

export default UserDashboard;