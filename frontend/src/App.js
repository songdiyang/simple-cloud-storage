import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Drawer } from 'antd';
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
import Sidebar from './components/Sidebar';
import Header from './components/Header';

const { Content } = Layout;

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
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

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