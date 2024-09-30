import { Spin } from "antd";

function UserInfo({ userData, title }) {
    if (!userData) return (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
            <Spin tip="Loading..." size="large" />
        </div>
    )

    return (
        <div className="user-info">
            <h2>{title}</h2>
            <p><strong>Username:</strong> {userData.username}</p> {/* Using sub as username */}
            <p><strong>Role:</strong> {userData.is_admin ? 'Admin' : 'User'}</p>
        </div>
    );
}

export default UserInfo;