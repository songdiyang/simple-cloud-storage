import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Drawer, Result, Button } from 'antd';
import { CloudOutlined } from '@ant-design/icons';
import './App.css';

import { useAuth } from './contexts/AuthContext';
import { useMobile } from './hooks/useMobile';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Files from './pages/Files';
import Shares from './pages/Shares';
import ShareView from './pages/ShareView';
import FileSearch from './pages/FileSearch';
import Profile from './pages/Profile';
import Trash from './pages/Trash';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

// 管理后台页面
import { 
  AdminLayout, 
  AdminDashboard, 
  AdminUsers, 
  AdminVIP, 
  AdminLogs 
} from './pages/admin';

const { Content } = Layout;

// 检查是否为管理员
const isAdminUser = (user) => {
  return user?.is_admin_user || user?.role === 'admin' || user?.is_superuser;
};

// 管理员路由保护组件
const AdminRoute = ({ children }) => {
  const { user } = useAuth();
  
  if (!isAdminUser(user)) {
    return (
      <Result
        status="403"
        title="无权访问"
        subTitle="抱歉，您没有权限访问管理后台"
        extra={
          <Button type="primary" href="/dashboard">
            返回首页
          </Button>
        }
      />
    );
  }
  
  return <AdminLayout>{children}</AdminLayout>;
};

// 普通用户路由保护组件（管理员不能访问）
const UserRoute = ({ children }) => {
  const { user } = useAuth();
  
  // 管理员重定向到管理后台
  if (isAdminUser(user)) {
    return <Navigate to="/admin" replace />;
  }
  
  return children;
};

function App() {
  const { user, loading } = useAuth();
  const { isMobile, isTablet } = useMobile();
  const [drawerVisible, setDrawerVisible] = React.useState(false);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">
          <CloudOutlined />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/share/:shareCode" element={<ShareView />} />
        <Route path="/admin/*" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  // 管理员登录后直接进入管理后台
  if (isAdminUser(user)) {
    return (
      <Routes>
        <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
        <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
        <Route path="/admin/vip" element={<AdminRoute><AdminVIP /></AdminRoute>} />
        <Route path="/admin/logs" element={<AdminRoute><AdminLogs /></AdminRoute>} />
        <Route path="/share/:shareCode" element={<ShareView />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    );
  }

  // 普通用户界面
  const sidebarContent = <Sidebar mobileMode={true} onClose={() => setDrawerVisible(false)} />;

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {isMobile || isTablet ? (
        <>
          <Drawer
            title="云盘系统"
            placement="left"
            onClose={() => setDrawerVisible(false)}
            open={drawerVisible}
            bodyStyle={{ padding: 0 }}
            width={240}
          >
            {sidebarContent}
          </Drawer>
          <Layout>
            <Header 
              showMenuButton={true}
              onMenuClick={() => setDrawerVisible(true)}
            />
            <Content style={{ 
              margin: isMobile ? '8px' : '12px 8px', 
              padding: isMobile ? '8px' : '12px',
              background: 'transparent',
              minHeight: 'calc(100vh - 64px)'
            }}>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/files" element={<Files />} />
                <Route path="/files/:folderId" element={<Files />} />
                <Route path="/shares" element={<Shares />} />
                <Route path="/trash" element={<Trash />} />
                <Route path="/search" element={<FileSearch />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/share/:shareCode" element={<ShareView />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Content>
          </Layout>
        </>
      ) : (
        <>
          <Sidebar />
          <Layout>
            <Header />
            <Content style={{ 
              margin: '24px 16px', 
              padding: '24px',
              background: 'transparent'
            }}>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/files" element={<Files />} />
                <Route path="/files/:folderId" element={<Files />} />
                <Route path="/shares" element={<Shares />} />
                <Route path="/trash" element={<Trash />} />
                <Route path="/search" element={<FileSearch />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/share/:shareCode" element={<ShareView />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Content>
          </Layout>
        </>
      )}
    </Layout>
  );
}

export default App;