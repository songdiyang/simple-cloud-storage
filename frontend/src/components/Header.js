import React from 'react';
import { Layout, Avatar, Dropdown, Space, Typography } from 'antd';
import { UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header = () => {
  const { user, logout } = useAuth();

  const menuItems = [
    {
      key: 'profile',
      icon: <SettingOutlined />,
      label: '个人设置',
      onClick: () => window.location.href = '/profile'
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout
    },
  ];

  return (
    <AntHeader 
      style={{ 
        padding: '0 24px', 
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{
          width: '40px',
          height: '40px',
          background: 'linear-gradient(145deg, #ff6b6b, #ff8e53)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '20px',
          fontWeight: 'bold',
          marginRight: '12px'
        }}>
          ☁
        </div>
        <Text style={{ fontSize: '20px', fontWeight: 'bold', color: '#333' }}>
          云盘系统
        </Text>
      </div>

      <Dropdown menu={{ items: menuItems }} placement="bottomRight">
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          cursor: 'pointer',
          padding: '8px 12px',
          borderRadius: '20px',
          transition: 'background 0.3s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0,0,0,0.05)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <Avatar 
            src={user?.avatar} 
            icon={<UserOutlined />} 
            size="small"
            style={{ marginRight: '8px' }}
          />
          <Space>
            <Text strong>{user?.username}</Text>
          </Space>
        </div>
      </Dropdown>
    </AntHeader>
  );
};

export default Header;