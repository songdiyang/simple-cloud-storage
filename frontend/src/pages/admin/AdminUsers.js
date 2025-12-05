import React, { useState } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Button, 
  Input, 
  Select, 
  Space, 
  Modal,
  Form,
  InputNumber,
  Switch,
  message,
  Typography,
  Tooltip,
  Badge
} from 'antd';
import { 
  UserOutlined, 
  CrownOutlined, 
  SearchOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import api from '../../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

// 格式化字节
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const AdminUsers = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [form] = Form.useForm();

  const { data: users, isLoading } = useQuery(
    ['admin-users', search, roleFilter], 
    () => api.get('/api/auth/admin/users/', { 
      params: { search, role: roleFilter } 
    }).then(res => res.data)
  );

  const updateUserMutation = useMutation(
    ({ userId, data }) => api.put(`/api/auth/admin/users/${userId}/`, data),
    {
      onSuccess: () => {
        message.success('用户信息更新成功');
        queryClient.invalidateQueries('admin-users');
        setEditModalVisible(false);
      },
      onError: (error) => {
        message.error(error.response?.data?.error || '更新失败');
      }
    }
  );

  const handleEdit = (user) => {
    setEditingUser(user);
    form.setFieldsValue({
      role: user.role,
      storage_quota_gb: user.storage_quota / (1024 * 1024 * 1024),
      is_active: user.is_active
    });
    setEditModalVisible(true);
  };

  const handleSubmit = async (values) => {
    updateUserMutation.mutate({
      userId: editingUser.id,
      data: {
        role: values.role,
        storage_quota: Math.round(values.storage_quota_gb * 1024 * 1024 * 1024),
        is_active: values.is_active
      }
    });
  };

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (text, record) => (
        <Space>
          {record.is_online ? (
            <Badge status="success" />
          ) : (
            <Badge status="default" />
          )}
          <Text strong>{text}</Text>
        </Space>
      )
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      responsive: ['md']
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role, record) => {
        const colors = {
          'admin': 'purple',
          'vip': 'gold',
          'user': 'default'
        };
        const icons = {
          'admin': <UserOutlined />,
          'vip': <CrownOutlined />,
          'user': <UserOutlined />
        };
        return (
          <Tag color={colors[role]} icon={icons[role]} style={{ border: '2px solid #333' }}>
            {record.role_display}
          </Tag>
        );
      }
    },
    {
      title: '存储使用',
      key: 'storage',
      responsive: ['lg'],
      render: (_, record) => (
        <Tooltip title={`${formatBytes(record.used_storage)} / ${formatBytes(record.storage_quota)}`}>
          <div style={{ width: 100 }}>
            <div style={{ 
              height: 8, 
              background: '#f0f0f0', 
              borderRadius: 4,
              border: '1px solid #333',
              overflow: 'hidden'
            }}>
              <div style={{ 
                height: '100%', 
                width: `${Math.min(record.storage_usage_percentage, 100)}%`,
                background: record.storage_usage_percentage > 80 
                  ? 'linear-gradient(90deg, #ff4d4f, #ff7875)' 
                  : 'linear-gradient(90deg, #667eea, #764ba2)',
                borderRadius: 4
              }} />
            </div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.storage_usage_percentage?.toFixed(1)}%
            </Text>
          </div>
        </Tooltip>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => active ? (
        <Tag color="success" icon={<CheckCircleOutlined />}>正常</Tag>
      ) : (
        <Tag color="error" icon={<CloseCircleOutlined />}>禁用</Tag>
      )
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      responsive: ['xl'],
      render: (time) => time ? new Date(time).toLocaleString() : '-'
    },
    {
      title: '注册时间',
      dataIndex: 'date_joined',
      key: 'date_joined',
      responsive: ['xl'],
      render: (time) => new Date(time).toLocaleDateString()
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button 
          type="primary"
          icon={<EditOutlined />}
          size="small"
          onClick={() => handleEdit(record)}
          style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: '2px solid #333'
          }}
        >
          编辑
        </Button>
      )
    }
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24, color: '#333' }}>
        <UserOutlined /> 用户管理
      </Title>

      <Card style={{ 
        border: '3px solid #333',
        borderRadius: 12,
        boxShadow: '4px 4px 0 #333'
      }}>
        {/* 搜索过滤 */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="搜索用户名"
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 200, border: '2px solid #333', borderRadius: 8 }}
            allowClear
          />
          <Select
            placeholder="筛选角色"
            value={roleFilter}
            onChange={setRoleFilter}
            style={{ width: 150 }}
            allowClear
          >
            <Option value="">全部角色</Option>
            <Option value="user">普通用户</Option>
            <Option value="vip">VIP用户</Option>
            <Option value="admin">管理员</Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={users || []}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* 编辑弹窗 */}
      <Modal
        title={<><EditOutlined /> 编辑用户: {editingUser?.username}</>}
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="role"
            label="用户角色"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="user">普通用户</Option>
              <Option value="vip">VIP用户</Option>
              <Option value="admin">管理员</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="storage_quota_gb"
            label="存储配额 (GB)"
            rules={[{ required: true }]}
          >
            <InputNumber 
              min={0.1} 
              max={100} 
              step={0.5} 
              style={{ width: '100%' }}
              addonAfter="GB"
            />
          </Form.Item>

          <Form.Item
            name="is_active"
            label="账户状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button onClick={() => setEditModalVisible(false)}>
                取消
              </Button>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={updateUserMutation.isLoading}
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: '2px solid #333'
                }}
              >
                保存修改
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AdminUsers;
