import React, { useState } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Button, 
  Space, 
  Modal,
  Input,
  message,
  Typography,
  Tabs,
  Empty,
  Popconfirm
} from 'antd';
import { 
  CrownOutlined, 
  CheckOutlined,
  CloseOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import api from '../../services/api';

const { Title, Text } = Typography;
const { TextArea } = Input;

const AdminVIP = () => {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('pending');
  const [rejectModalVisible, setRejectModalVisible] = useState(false);
  const [rejectingApp, setRejectingApp] = useState(null);
  const [rejectNote, setRejectNote] = useState('');

  const { data: applications, isLoading } = useQuery(
    ['admin-vip-applications', statusFilter], 
    () => api.get('/api/auth/admin/vip-applications/', { 
      params: { status: statusFilter } 
    }).then(res => res.data)
  );

  const reviewMutation = useMutation(
    ({ applicationId, action, admin_note }) => 
      api.post(`/api/auth/admin/vip-applications/${applicationId}/review/`, { action, admin_note }),
    {
      onSuccess: (_, variables) => {
        message.success(variables.action === 'approve' ? 'VIP申请已通过' : 'VIP申请已拒绝');
        queryClient.invalidateQueries('admin-vip-applications');
        queryClient.invalidateQueries('admin-dashboard');
        setRejectModalVisible(false);
        setRejectNote('');
      },
      onError: (error) => {
        message.error(error.response?.data?.error || '操作失败');
      }
    }
  );

  const handleApprove = (applicationId) => {
    reviewMutation.mutate({ applicationId, action: 'approve', admin_note: '' });
  };

  const handleReject = (app) => {
    setRejectingApp(app);
    setRejectModalVisible(true);
  };

  const submitReject = () => {
    if (!rejectingApp) return;
    reviewMutation.mutate({ 
      applicationId: rejectingApp.id, 
      action: 'reject', 
      admin_note: rejectNote 
    });
  };

  const columns = [
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      render: (text) => <Text strong>{text}</Text>
    },
    {
      title: '赞助单号',
      dataIndex: 'order_number',
      key: 'order_number',
      render: (text) => (
        <Text copyable style={{ 
          padding: '4px 8px', 
          background: '#f5f5f5', 
          borderRadius: 4,
          border: '1px solid #d9d9d9'
        }}>
          {text}
        </Text>
      )
    },
    {
      title: '申请时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleString()
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status, record) => {
        const config = {
          'pending': { color: 'orange', text: '待审核' },
          'approved': { color: 'success', text: '已通过' },
          'rejected': { color: 'error', text: '已拒绝' }
        };
        return <Tag color={config[status]?.color}>{config[status]?.text}</Tag>;
      }
    },
    {
      title: '审核时间',
      dataIndex: 'reviewed_at',
      key: 'reviewed_at',
      render: (time) => time ? new Date(time).toLocaleString() : '-'
    },
    {
      title: '审核人',
      dataIndex: 'reviewed_by',
      key: 'reviewed_by',
      render: (text) => text || '-'
    },
    {
      title: '备注',
      dataIndex: 'admin_note',
      key: 'admin_note',
      render: (text) => text || '-',
      ellipsis: true
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => {
        if (record.status !== 'pending') {
          return <Text type="secondary">已处理</Text>;
        }
        return (
          <Space>
            <Popconfirm
              title="确认通过此VIP申请？"
              description="通过后用户将升级为VIP，存储空间扩容至5GB"
              onConfirm={() => handleApprove(record.id)}
              okText="确认通过"
              cancelText="取消"
              icon={<ExclamationCircleOutlined style={{ color: '#52c41a' }} />}
            >
              <Button 
                type="primary"
                icon={<CheckOutlined />}
                size="small"
                style={{ 
                  background: '#52c41a',
                  border: '2px solid #333'
                }}
              >
                通过
              </Button>
            </Popconfirm>
            <Button 
              danger
              icon={<CloseOutlined />}
              size="small"
              onClick={() => handleReject(record)}
              style={{ border: '2px solid #333' }}
            >
              拒绝
            </Button>
          </Space>
        );
      }
    }
  ];

  const tabItems = [
    { key: 'pending', label: '待审核', children: null },
    { key: 'approved', label: '已通过', children: null },
    { key: 'rejected', label: '已拒绝', children: null },
    { key: '', label: '全部', children: null }
  ];

  const pendingCount = applications?.filter(a => a.status === 'pending').length || 0;

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24, color: '#333' }}>
        <CrownOutlined style={{ color: '#ffd700' }} /> VIP申请审核
        {pendingCount > 0 && (
          <Tag color="orange" style={{ marginLeft: 12 }}>
            {pendingCount} 条待处理
          </Tag>
        )}
      </Title>

      <Card style={{ 
        border: '3px solid #333',
        borderRadius: 12,
        boxShadow: '4px 4px 0 #333'
      }}>
        <Tabs 
          activeKey={statusFilter} 
          onChange={setStatusFilter}
          items={tabItems}
        />

        <Table
          columns={columns}
          dataSource={applications || []}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
          scroll={{ x: 900 }}
          locale={{
            emptyText: <Empty description="暂无申请记录" />
          }}
        />
      </Card>

      {/* 拒绝原因弹窗 */}
      <Modal
        title={<><CloseOutlined style={{ color: '#ff4d4f' }} /> 拒绝VIP申请</>}
        open={rejectModalVisible}
        onCancel={() => {
          setRejectModalVisible(false);
          setRejectNote('');
        }}
        onOk={submitReject}
        okText="确认拒绝"
        okButtonProps={{ danger: true, loading: reviewMutation.isLoading }}
        cancelText="取消"
      >
        <div style={{ marginBottom: 16 }}>
          <Text>用户: <Text strong>{rejectingApp?.username}</Text></Text>
          <br />
          <Text>单号: <Text code>{rejectingApp?.order_number}</Text></Text>
        </div>
        <TextArea
          placeholder="请输入拒绝原因（可选）"
          value={rejectNote}
          onChange={(e) => setRejectNote(e.target.value)}
          rows={4}
        />
      </Modal>
    </div>
  );
};

export default AdminVIP;
