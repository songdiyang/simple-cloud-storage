import React from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Typography, 
  Table,
  Tag,
  Spin,
  Space
} from 'antd';
import { 
  UserOutlined, 
  CrownOutlined, 
  TeamOutlined,
  CloudOutlined,
  RiseOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import api from '../../services/api';

const { Title, Text } = Typography;

// 格式化字节
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const AdminDashboard = () => {
  const { data: dashboardData, isLoading } = useQuery('admin-dashboard', () =>
    api.get('/api/auth/admin/dashboard/').then(res => res.data)
  );

  const { data: onlineUsers } = useQuery('admin-online-users', () =>
    api.get('/api/auth/admin/online-users/').then(res => res.data),
    { refetchInterval: 30000 } // 每30秒刷新
  );

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  const { user_stats, storage_stats, pending_vip_applications } = dashboardData || {};

  // 在线用户表格列
  const onlineColumns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '角色',
      dataIndex: 'role_display',
      key: 'role',
      render: (text, record) => (
        <Tag color={record.role === 'vip' ? 'gold' : record.role === 'admin' ? 'purple' : 'default'}>
          {text}
        </Tag>
      )
    },
    {
      title: '最后活动',
      dataIndex: 'last_activity',
      key: 'last_activity',
      render: (time) => new Date(time).toLocaleString()
    }
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24, color: '#333' }}>
        <Space>
          <span style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            控制台
          </span>
        </Space>
      </Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={8} lg={4}>
          <Card style={{ 
            border: '3px solid #333',
            borderRadius: 12,
            boxShadow: '4px 4px 0 #333'
          }}>
            <Statistic
              title="总用户数"
              value={user_stats?.total || 0}
              prefix={<TeamOutlined style={{ color: '#667eea' }} />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card style={{ 
            border: '3px solid #333',
            borderRadius: 12,
            boxShadow: '4px 4px 0 #333',
            background: 'linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%)'
          }}>
            <Statistic
              title="VIP用户"
              value={user_stats?.vip || 0}
              prefix={<CrownOutlined style={{ color: '#ffd700' }} />}
              valueStyle={{ color: '#d48806' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card style={{ 
            border: '3px solid #333',
            borderRadius: 12,
            boxShadow: '4px 4px 0 #333',
            background: 'linear-gradient(135deg, #f0f5ff 0%, #d6e4ff 100%)'
          }}>
            <Statistic
              title="管理员"
              value={user_stats?.admin || 0}
              prefix={<UserOutlined style={{ color: '#722ed1' }} />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card style={{ 
            border: '3px solid #333',
            borderRadius: 12,
            boxShadow: '4px 4px 0 #333',
            background: 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)'
          }}>
            <Statistic
              title="在线用户"
              value={user_stats?.online || 0}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card style={{ 
            border: '3px solid #333',
            borderRadius: 12,
            boxShadow: '4px 4px 0 #333'
          }}>
            <Statistic
              title="今日新增"
              value={user_stats?.today_new || 0}
              prefix={<RiseOutlined style={{ color: '#13c2c2' }} />}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card style={{ 
            border: '3px solid #333',
            borderRadius: 12,
            boxShadow: '4px 4px 0 #333',
            background: pending_vip_applications > 0 ? 'linear-gradient(135deg, #fff2e8 0%, #ffd8bf 100%)' : undefined
          }}>
            <Statistic
              title="待审核VIP"
              value={pending_vip_applications || 0}
              prefix={<ClockCircleOutlined style={{ color: '#fa8c16' }} />}
              valueStyle={{ color: pending_vip_applications > 0 ? '#fa541c' : undefined }}
            />
          </Card>
        </Col>
      </Row>

      {/* 存储统计 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card 
            title={<><CloudOutlined /> 存储统计</>}
            style={{ 
              border: '3px solid #333',
              borderRadius: 12,
              boxShadow: '4px 4px 0 #333'
            }}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="总配额"
                  value={formatBytes(storage_stats?.total_quota || 0)}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="已使用"
                  value={formatBytes(storage_stats?.total_used || 0)}
                  valueStyle={{ 
                    color: storage_stats?.total_used > storage_stats?.total_quota * 0.8 ? '#ff4d4f' : '#3f8600' 
                  }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 在线用户列表 */}
        <Col xs={24} lg={12}>
          <Card 
            title={<><CheckCircleOutlined style={{ color: '#52c41a' }} /> 当前在线用户</>}
            style={{ 
              border: '3px solid #333',
              borderRadius: 12,
              boxShadow: '4px 4px 0 #333'
            }}
            extra={<Text type="secondary">每30秒自动刷新</Text>}
          >
            <Table
              columns={onlineColumns}
              dataSource={onlineUsers || []}
              rowKey="username"
              size="small"
              pagination={false}
              locale={{ emptyText: '暂无在线用户' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 用户分布 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card 
            title="用户角色分布"
            style={{ 
              border: '3px solid #333',
              borderRadius: 12,
              boxShadow: '4px 4px 0 #333'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
              <div style={{ 
                flex: user_stats?.normal || 1,
                height: 40,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '8px 0 0 8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontWeight: 'bold',
                border: '2px solid #333'
              }}>
                普通用户 ({user_stats?.normal || 0})
              </div>
              <div style={{ 
                flex: user_stats?.vip || 0.1,
                height: 40,
                background: 'linear-gradient(135deg, #ffd700 0%, #ffb700 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#333',
                fontWeight: 'bold',
                border: '2px solid #333'
              }}>
                VIP ({user_stats?.vip || 0})
              </div>
              <div style={{ 
                flex: user_stats?.admin || 0.1,
                height: 40,
                background: 'linear-gradient(135deg, #722ed1 0%, #531dab 100%)',
                borderRadius: '0 8px 8px 0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontWeight: 'bold',
                border: '2px solid #333'
              }}>
                管理员 ({user_stats?.admin || 0})
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AdminDashboard;
