import React from 'react';
import { Layout, Avatar, Dropdown, Space, Typography, Button } from 'antd';
import { UserOutlined, LogoutOutlined, SettingOutlined, MenuOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header = ({ showMenuButton = false, onMenuClick }) => {
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
        padding: '0 16px', 
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        minHeight: '64px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        {showMenuButton && (
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={onMenuClick}
            style={{ 
              marginRight: '12px',
              fontSize: '18px',
              height: '40px',
              width: '40px'
            }}
          />
        )}
        <div style={{
          width: showMenuButton ? '32px' : '40px',
          height: showMenuButton ? '32px' : '40px',
          background: 'linear-gradient(145deg, #ff6b6b, #ff8e53)',
          borderRadius: showMenuButton ? '8px' : '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: showMenuButton ? '16px' : '20px',
          fontWeight: 'bold',
          marginRight: '12px'
        }}>
          ☁
        </div>
        <Text style={{ 
          fontSize: showMenuButton ? '18px' : '20px', 
          fontWeight: 'bold', 
          color: '#333' 
        }}>
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