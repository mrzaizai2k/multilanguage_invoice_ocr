import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Step 1
import './UserDashboard.css';

function UserDashboard() {
  const [activeTab, setActiveTab] = useState('userInfo');
  const navigate = useNavigate(); // Step 2

  const renderTabContent = () => {
    switch (activeTab) {
      case 'userInfo':
        return <UserInfo />;
      case 'invoice':
        return <InvoiceList />;
      case 'addInvoice':
        return <AddInvoice />;
      default:
        return null;
    }
  };

  return (
    <div className="dashboard">
      <div className="sidebar">
        <h1>Invoice Extract System</h1>
        <button className={activeTab === 'userInfo' ? 'active' : ''} onClick={() => setActiveTab('userInfo')}>
          <span className="icon">👤</span> User Info
        </button>
        <button className={activeTab === 'invoice' ? 'active' : ''} onClick={() => setActiveTab('invoice')}>
          <span className="icon">📄</span> Invoice
        </button>
        <button className={activeTab === 'addInvoice' ? 'active' : ''} onClick={() => setActiveTab('addInvoice')}>
          <span className="icon">➕</span> Add Invoice
        </button>
        {/* Moved the Logout button here */}
        <button className="logout" onClick={() => navigate('/login')}>
          <span className="icon">🚪</span> Logout
        </button>
      </div>
      <div className="content">
        {renderTabContent()}
      </div>
    </div>
  );
}
function UserInfo({ userData }) {
    if (!userData) return <p>Loading...</p>;
  
    return (
      <div className="user-info">
        <h2>User Information</h2>
        <p><strong>Name:</strong> {userData.name}</p>
        <p><strong>Role:</strong> {userData.is_admin ? 'Admin' : 'User'}</p>
        {/* Add more user info as needed */}
      </div>
    );
  }

function InvoiceList() {
  return <h2>Invoice List</h2>;
}

function AddInvoice() {
    const [selectedFile, setSelectedFile] = useState(null);
  
    const handleFileChange = (event) => {
      setSelectedFile(event.target.files[0]);
    };
  
    const handleUpload = async () => {
      if (!selectedFile) {
        alert("Please select a file to upload.");
        return;
      }
  
      const formData = new FormData();
      formData.append('file', selectedFile);
  
    //   try {
    //     const response = await axios.post(`${API_URL}/upload`, formData, {
    //       headers: {
    //         'Content-Type': 'multipart/form-data',
    //         Authorization: `Bearer ${localStorage.getItem('token')}`,
    //       },
    //     });
    //     console.log('File uploaded successfully:', response.data);
    //     // Handle success (e.g., show a message or redirect)
    //   } catch (error) {
    //     console.error('Error uploading file:', error);
    //     // Handle error (e.g., show an error message)
    //   }
    };
  
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
