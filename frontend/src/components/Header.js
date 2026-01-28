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
        background: '#ffffff', /* 纯白色 */
        borderBottom: '1px solid #000000', /* 黑色边框 */
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
              width: '40px',
              borderRadius: '0', /* 无圆角 */
              border: '1px solid #000000', /* 黑色边框 */
              background: '#ffffff', /* 白色背景 */
              color: '#000000' /* 黑色图标 */
            }}
          />
        )}
        <div style={{
          width: showMenuButton ? '32px' : '40px',
          height: showMenuButton ? '32px' : '40px',
          background: '#000000', /* 纯黑色 */
          borderRadius: '0', /* 无圆角 - 方形 */
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff', /* 白色文字 */
          fontSize: showMenuButton ? '16px' : '20px',
          fontWeight: 'normal', /* 减小字重 */
          marginRight: '12px'
        }}>
          ☁
        </div>
        <Text style={{ 
          fontSize: showMenuButton ? '18px' : '20px', 
          fontWeight: 'normal', /* 减小字重 */
          color: '#000000' /* 纯黑色 */
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
          borderRadius: '0', /* 无圆角 */
          transition: 'none', /* 去除过渡 */
          border: '1px solid #000000', /* 黑色边框 */
          background: '#ffffff' /* 白色背景 */
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = '#f0f0f0'} /* 浅灰色悬停 */
        onMouseLeave={(e) => e.currentTarget.style.background = '#ffffff'}
        >
          <Avatar 
            src={user?.avatar} 
            icon={<UserOutlined />} 
            size="small"
            style={{ 
              marginRight: '8px',
              backgroundColor: '#000000', /* 黑色头像背景 */
              color: '#ffffff' /* 白色头像图标 */
            }}
          />
          <Space>
            <Text strong style={{ color: '#000000' }}>{user?.username}</Text>
          </Space>
        </div>
      </Dropdown>
    </AntHeader>
  );
};

export default Header;