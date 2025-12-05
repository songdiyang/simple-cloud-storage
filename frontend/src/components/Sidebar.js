import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  FolderOutlined,
  ShareAltOutlined,
  SearchOutlined,
  UserOutlined,
  DeleteOutlined
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar = ({ mobileMode = false, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // 普通用户菜单（管理员有独立界面）
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/files',
      icon: <FolderOutlined />,
      label: '我的文件',
    },
    {
      key: '/shares',
      icon: <ShareAltOutlined />,
      label: '我的分享',
    },
    {
      key: '/trash',
      icon: <DeleteOutlined />,
      label: '回收站',
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: '搜索文件',
    },
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: '个人设置',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
    if (mobileMode && onClose) {
      onClose();
    }
  };

  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/files')) return '/files';
    return path;
  };

  const sidebarContent = (
    <>
      <div style={{ 
        height: '64px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          background: 'linear-gradient(145deg, #667eea, #764ba2)',
          borderRadius: '15px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '24px',
          fontWeight: 'bold'
        }}>
          ☁
        </div>
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={[getSelectedKey()]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          border: 'none',
          background: 'transparent',
          fontSize: '16px'
        }}
      />
    </>
  );

  if (mobileMode) {
    return sidebarContent;
  }

  return (
    <Sider
      width={240}
      style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.2)',
      }}
    >
      {sidebarContent}
    </Sider>
  );
};

export default Sidebar;