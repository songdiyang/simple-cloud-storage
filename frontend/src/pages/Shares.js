import React, { useState } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  DatePicker, 
  InputNumber,
  message,
  Space,
  Tag,
  Typography,
  Popconfirm,
  Tooltip
} from 'antd';
import { 
  ShareAltOutlined, 
  PlusOutlined, 
  DeleteOutlined,
  CopyOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import dayjs from 'dayjs';
import api from '../services/api';
import { formatBytes, formatDateTime, getFileIcon } from '../utils/format';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const Shares = () => {
  const queryClient = useQueryClient();
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [shareForm] = Form.useForm();

  const { data: shares = [], isLoading } = useQuery(
    'my-shares',
    () => api.get('/api/files/shares/').then(res => res.data)
  );

  const createShareMutation = useMutation(
    (fileId) => api.post(`/api/files/${fileId}/share/`),
    {
      onSuccess: () => {
        message.success('分享创建成功！');
        setCreateModalVisible(false);
        shareForm.resetFields();
        queryClient.invalidateQueries('my-shares');
      },
      onError: (error) => {
        const errorMsg = error.response?.data?.error || '创建失败';
        message.error(errorMsg);
      }
    }
  );

  const deleteShareMutation = useMutation(
    (shareId) => api.delete(`/api/files/shares/${shareId}/delete/`),
    {
      onSuccess: () => {
        message.success('分享已取消！');
        queryClient.invalidateQueries('my-shares');
      },
      onError: (error) => {
        const errorMsg = error.response?.data?.error || '取消失败';
        message.error(errorMsg);
      }
    }
  );

  const columns = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (text) => (
        <Tooltip title={text}>
          <Text ellipsis style={{ maxWidth: '200px' }}>{text}</Text>
        </Tooltip>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size_display',
      key: 'file_size_display',
    },
    {
      title: '分享码',
      dataIndex: 'share_code',
      key: 'share_code',
      render: (code, record) => (
        <Space>
          <Tag color="blue">{code}</Tag>
          <Button
            type="text"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => {
              navigator.clipboard.writeText(code);
              message.success('分享码已复制到剪贴板！');
            }}
          />
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive, record) => (
        <Space direction="vertical" size="small">
          <Tag color={isActive ? 'green' : 'red'}>
            {isActive ? '有效' : '无效'}
          </Tag>
          {record.is_expired && (
            <Tag color="orange">已过期</Tag>
          )}
        </Space>
      ),
    },
    {
      title: '下载次数',
      dataIndex: 'download_count',
      key: 'download_count',
      render: (count, record) => (
        <Text>
          {count} / {record.max_downloads || '无限制'}
        </Text>
      ),
    },
    {
      title: '过期时间',
      dataIndex: 'expire_at',
      key: 'expire_at',
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '永不过期',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => window.open(`/share/${record.share_code}`, '_blank')}
          />
          <Popconfirm
            title="确定取消这个分享吗？"
            onConfirm={() => deleteShareMutation.mutate(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              danger
              size="small"
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ color: '#333', margin: 0 }}>
          我的分享
        </Title>
        
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setCreateModalVisible(true)}
          className="cel-button"
        >
          创建分享
        </Button>
      </div>

      <Card className="cel-card">
        <Table
          columns={columns}
          dataSource={shares}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: false,
            showQuickJumper: true,
          }}
        />
      </Card>

      {/* 创建分享模态框 */}
      <Modal
        title="创建文件分享"
        open={createModalVisible}
        onOk={() => shareForm.submit()}
        onCancel={() => setCreateModalVisible(false)}
        confirmLoading={createShareMutation.isLoading}
        width={600}
      >
        <Form
          form={shareForm}
          layout="vertical"
          onFinish={(values) => {
            // 这里需要先选择文件，然后创建分享
            // 简化起见，这里只是示例
            message.info('请先在文件页面选择要分享的文件');
          }}
        >
          <Form.Item>
            <Text type="secondary">
              请前往"我的文件"页面，点击文件操作栏的分享按钮来创建分享链接。
            </Text>
          </Form.Item>
          
          <Form.Item
            name="password"
            label="访问密码（可选）"
          >
            <Input.Password placeholder="留空表示无需密码" />
          </Form.Item>
          
          <Form.Item
            name="expire_at"
            label="过期时间（可选）"
          >
            <DatePicker
              showTime
              placeholder="留空表示永不过期"
              style={{ width: '100%' }}
            />
          </Form.Item>
          
          <Form.Item
            name="max_downloads"
            label="最大下载次数（可选）"
          >
            <InputNumber
              placeholder="留空表示无限制"
              style={{ width: '100%' }}
              min={1}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Shares;