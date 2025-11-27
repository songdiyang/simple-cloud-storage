import React from 'react';
import { Row, Col, Card, Statistic, Progress, Typography, Space } from 'antd';
import { 
  CloudOutlined, 
  FolderOutlined, 
  FileOutlined, 
  ShareAltOutlined 
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import api from '../services/api';

const { Title, Text } = Typography;

const Dashboard = () => {
  const { data: storageInfo } = useQuery('storage-info', () =>
    api.get('/api/files/storage/').then(res => res.data)
  );

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div>
      <Title level={2} style={{ color: '#333', marginBottom: '24px' }}>
        仪表盘
      </Title>

      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="modern-card">
            <Statistic
              title="存储配额"
              value={storageInfo?.storage_quota || 0}
              formatter={(value) => formatBytes(value)}
              prefix={<CloudOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="modern-card">
            <Statistic
              title="已使用存储"
              value={storageInfo?.used_storage || 0}
              formatter={(value) => formatBytes(value)}
              prefix={<FileOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="modern-card">
            <Statistic
              title="文件总数"
              value={storageInfo?.total_files || 0}
              prefix={<FileOutlined style={{ color: '#722ed1' }} />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="modern-card">
            <Statistic
              title="文件夹总数"
              value={storageInfo?.total_folders || 0}
              prefix={<FolderOutlined style={{ color: '#fa8c16' }} />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card className="modern-card" title="存储使用情况">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>总体使用率</Text>
                <Progress
                  percent={storageInfo?.storage_usage_percentage || 0}
                  strokeColor={{
                    '0%': '#1890ff',
                    '100%': '#52c41a',
                  }}
                  format={(percent) => `${percent?.toFixed(1)}%`}
                  className="progress-custom"
                />
              </div>
              <div>
                <Text type="secondary">
                  已使用: {formatBytes(storageInfo?.used_storage || 0)} / 
                  {formatBytes(storageInfo?.storage_quota || 0)}
                </Text>
              </div>
              <div>
                <Text type="secondary">
                  可用空间: {formatBytes(storageInfo?.available_storage || 0)}
                </Text>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card className="modern-card" title="快速操作">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{
                padding: '16px',
                background: '#f6ffed',
                border: '1px solid #b7eb8f',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onClick={() => window.location.href = '/files'}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#d9f7be';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#f6ffed';
              }}
              >
                <Space>
                  <FolderOutlined style={{ fontSize: '20px', color: '#52c41a' }} />
                  <div>
                    <Text strong>管理文件</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>浏览和管理您的文件</Text>
                  </div>
                </Space>
              </div>

              <div style={{
                padding: '16px',
                background: '#e6f7ff',
                border: '1px solid #91d5ff',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onClick={() => window.location.href = '/shares'}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#bae7ff';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#e6f7ff';
              }}
              >
                <Space>
                  <ShareAltOutlined style={{ fontSize: '20px', color: '#1890ff' }} />
                  <div>
                    <Text strong>分享文件</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>创建和管理分享链接</Text>
                  </div>
                </Space>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;