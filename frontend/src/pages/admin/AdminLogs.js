import React from 'react';
import { 
  Card, 
  Table, 
  Typography,
  Tag,
  Space,
  Spin
} from 'antd';
import { 
  HistoryOutlined,
  UserOutlined,
  GlobalOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import api from '../../services/api';

const { Title, Text } = Typography;

const AdminLogs = () => {
  const { data: loginRecords, isLoading } = useQuery('admin-login-records', () =>
    api.get('/api/auth/admin/login-records/').then(res => res.data),
    { refetchInterval: 60000 } // 每分钟刷新
  );

  const columns = [
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      render: (text) => (
        <Space>
          <UserOutlined style={{ color: '#667eea' }} />
          <Text strong>{text}</Text>
        </Space>
      )
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      render: (ip) => (
        <Tag icon={<GlobalOutlined />} color="blue" style={{ border: '1px solid #333' }}>
          {ip || '未知'}
        </Tag>
      )
    },
    {
      title: '登录时间',
      dataIndex: 'login_time',
      key: 'login_time',
      render: (time) => (
        <Space>
          <ClockCircleOutlined style={{ color: '#999' }} />
          {new Date(time).toLocaleString()}
        </Space>
      )
    },
    {
      title: '时间距今',
      dataIndex: 'login_time',
      key: 'time_ago',
      render: (time) => {
        const now = new Date();
        const loginTime = new Date(time);
        const diffMs = now - loginTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return <Tag color="green">刚刚</Tag>;
        if (diffMins < 60) return <Tag color="blue">{diffMins} 分钟前</Tag>;
        if (diffHours < 24) return <Tag color="orange">{diffHours} 小时前</Tag>;
        return <Tag>{diffDays} 天前</Tag>;
      }
    }
  ];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24, color: '#333' }}>
        <HistoryOutlined /> 登录日志
        <Text type="secondary" style={{ fontSize: 14, marginLeft: 16 }}>
          最近 100 条记录
        </Text>
      </Title>

      <Card style={{ 
        border: '3px solid #333',
        borderRadius: 12,
        boxShadow: '4px 4px 0 #333'
      }}>
        <Table
          columns={columns}
          dataSource={loginRecords || []}
          rowKey="id"
          pagination={{ pageSize: 20 }}
          scroll={{ x: 600 }}
        />
      </Card>
    </div>
  );
};

export default AdminLogs;
