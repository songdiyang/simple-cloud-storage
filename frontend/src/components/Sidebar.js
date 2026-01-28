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
        borderBottom: '1px solid #000000' /* 黑色边框 */
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          background: '#000000', /* 纯黑色 */
          borderRadius: '0', /* 无圆角 - 方形 */
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff', /* 白色文字 */
          fontSize: '24px',
          fontWeight: 'normal' /* 减小字重 */
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
          background: '#ffffff', /* 白色背景 */
          fontSize: '16px',
          color: '#000000' /* 黑色文字 */
        }}
        itemIcon={
          <span style={{ color: '#000000' }} /> /* 确保图标为黑色 */
        }
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
        background: '#ffffff', /* 纯白色 */
        borderRight: '1px solid #000000', /* 黑色边框 */
      }}
    >
      {sidebarContent}
    </Sider>
  );
};

export default Sidebar;