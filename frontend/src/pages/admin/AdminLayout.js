import React from 'react';
import { Layout, Menu, Typography, Avatar, Dropdown, Space } from 'antd';
import { 
  DashboardOutlined, 
  UserOutlined, 
  CrownOutlined, 
  HistoryOutlined,
  LogoutOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

const AdminLayout = ({ children }) => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    {
      key: '/admin',
      icon: <DashboardOutlined />,
      label: <Link to="/admin">控制台</Link>
    },
    {
      key: '/admin/users',
      icon: <UserOutlined />,
      label: <Link to="/admin/users">用户管理</Link>
    },
    {
      key: '/admin/vip',
      icon: <CrownOutlined />,
      label: <Link to="/admin/vip">VIP审核</Link>
    },
    {
      key: '/admin/logs',
      icon: <HistoryOutlined />,
      label: <Link to="/admin/logs">登录日志</Link>
    }
  ];

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout
    }
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={240}
        style={{
          background: 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)',
          boxShadow: '4px 0 10px rgba(0,0,0,0.3)'
        }}
      >
        {/* Logo */}
        <div style={{
          padding: '20px',
          textAlign: 'center',
          borderBottom: '2px solid rgba(255,255,255,0.1)'
        }}>
          <SettingOutlined style={{ fontSize: 32, color: '#667eea' }} />
          <Title level={4} style={{ color: '#fff', margin: '8px 0 0 0' }}>
            管理后台
          </Title>
        </div>

        {/* Menu */}
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{
            background: 'transparent',
            border: 'none',
            marginTop: 16
          }}
          theme="dark"
        />
      </Sider>

      <Layout>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          border: '2px solid #333'
        }}>
          <div>
            <Text strong style={{ fontSize: 16 }}>
              云存储系统 · 管理中心
            </Text>
          </div>

          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar 
                src={user?.avatar ? `http://localhost:8000${user.avatar}` : undefined}
                icon={<UserOutlined />}
                style={{ border: '2px solid #667eea' }}
              />
              <Text strong>{user?.username}</Text>
            </Space>
          </Dropdown>
        </Header>

        <Content style={{
          margin: '24px',
          padding: '24px',
          background: '#f5f5f5',
          minHeight: 'calc(100vh - 112px)'
        }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;
