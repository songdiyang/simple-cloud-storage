import React from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Space, 
  Typography, 
  Empty, 
  Modal,
  message,
  Tag,
  Popconfirm,
  Statistic,
  Row,
  Col
} from 'antd';
import { 
  DeleteOutlined, 
  UndoOutlined, 
  ExclamationCircleOutlined,
  FileOutlined,
  FolderOutlined,
  FileImageOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileZipOutlined,
  PlayCircleOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import api from '../services/api';

const { Title, Text } = Typography;
const { confirm } = Modal;

// 文件图标映射
const getFileIcon = (fileType) => {
  const type = fileType?.toLowerCase() || '';
  if (['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'].includes(type)) {
    return <FileImageOutlined style={{ color: '#52c41a' }} />;
  }
  if (['.pdf'].includes(type)) {
    return <FilePdfOutlined style={{ color: '#ff4d4f' }} />;
  }
  if (['.doc', '.docx', '.txt', '.md'].includes(type)) {
    return <FileTextOutlined style={{ color: '#1890ff' }} />;
  }
  if (['.zip', '.rar', '.7z', '.tar', '.gz'].includes(type)) {
    return <FileZipOutlined style={{ color: '#faad14' }} />;
  }
  if (['.mp4', '.avi', '.mov', '.mkv', '.mp3', '.wav'].includes(type)) {
    return <PlayCircleOutlined style={{ color: '#722ed1' }} />;
  }
  return <FileOutlined style={{ color: '#666' }} />;
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 格式化时间
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const Trash = () => {
  const queryClient = useQueryClient();

  // 获取回收站文件列表
  const { data: trashFiles, isLoading } = useQuery('trash-files', () =>
    api.get('/api/files/trash/').then(res => res.data)
  );

  // 获取回收站统计
  const { data: trashStats } = useQuery('trash-stats', () =>
    api.get('/api/files/trash/stats/').then(res => res.data)
  );

  // 恢复文件
  const restoreMutation = useMutation(
    (fileId) => api.post(`/api/files/trash/${fileId}/restore/`),
    {
      onSuccess: () => {
        message.success('文件已恢复');
        queryClient.invalidateQueries('trash-files');
        queryClient.invalidateQueries('trash-stats');
        queryClient.invalidateQueries('file-list');
      },
      onError: (error) => {
        message.error(error.response?.data?.error || '恢复失败');
      }
    }
  );

  // 彻底删除
  const deleteMutation = useMutation(
    (fileId) => api.delete(`/api/files/trash/${fileId}/delete/`),
    {
      onSuccess: () => {
        message.success('文件已彻底删除');
        queryClient.invalidateQueries('trash-files');
        queryClient.invalidateQueries('trash-stats');
        queryClient.invalidateQueries('storage-info');
      },
      onError: (error) => {
        message.error(error.response?.data?.error || '删除失败');
      }
    }
  );

  // 清空回收站
  const emptyTrashMutation = useMutation(
    () => api.delete('/api/files/trash/empty/'),
    {
      onSuccess: (res) => {
        message.success(res.data.message || '回收站已清空');
        queryClient.invalidateQueries('trash-files');
        queryClient.invalidateQueries('trash-stats');
        queryClient.invalidateQueries('storage-info');
      },
      onError: (error) => {
        message.error(error.response?.data?.error || '清空失败');
      }
    }
  );

  // 确认清空回收站
  const handleEmptyTrash = () => {
    confirm({
      title: '确认清空回收站？',
      icon: <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />,
      content: (
        <div>
          <p>此操作将彻底删除回收站中的所有文件，无法恢复！</p>
          <p>共 <Text strong type="danger">{trashStats?.count || 0}</Text> 个文件，
             占用 <Text strong>{trashStats?.total_size_display || '0 B'}</Text></p>
        </div>
      ),
      okText: '确认清空',
      okType: 'danger',
      cancelText: '取消',
      onOk() {
        emptyTrashMutation.mutate();
      }
    });
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space>
          {getFileIcon(record.file_type)}
          <Text ellipsis style={{ maxWidth: 300 }}>{name}</Text>
        </Space>
      )
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      width: 100,
      render: (size) => formatFileSize(size)
    },
    {
      title: '删除时间',
      dataIndex: 'deleted_at',
      key: 'deleted_at',
      width: 180,
      render: (time) => formatDate(time)
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            icon={<UndoOutlined />}
            size="small"
            onClick={() => restoreMutation.mutate(record.id)}
            loading={restoreMutation.isLoading}
            style={{ 
              background: '#52c41a',
              border: '2px solid #333'
            }}
          >
            恢复
          </Button>
          <Popconfirm
            title="确认彻底删除？"
            description="此操作无法恢复！"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="删除"
            cancelText="取消"
            okType="danger"
          >
            <Button
              danger
              icon={<DeleteOutlined />}
              size="small"
              style={{ border: '2px solid #333' }}
            >
              彻底删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Title level={2} style={{ color: '#333', marginBottom: '24px' }}>
        <DeleteOutlined style={{ marginRight: 12 }} />
        回收站
      </Title>

      {/* 统计信息 */}
      <Row gutter={24} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={8}>
          <Card 
            style={{ 
              border: '3px solid #333',
              borderRadius: 12,
              boxShadow: '4px 4px 0 #333'
            }}
          >
            <Statistic
              title="文件数量"
              value={trashStats?.count || 0}
              suffix="个"
              valueStyle={{ color: '#666' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card 
            style={{ 
              border: '3px solid #333',
              borderRadius: 12,
              boxShadow: '4px 4px 0 #333'
            }}
          >
            <Statistic
              title="占用空间"
              value={trashStats?.total_size_display || '0 B'}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} style={{ marginTop: { xs: 16, sm: 0 } }}>
          <Card 
            style={{ 
              border: '3px solid #333',
              borderRadius: 12,
              boxShadow: '4px 4px 0 #333',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Button
              danger
              type="primary"
              icon={<ClearOutlined />}
              onClick={handleEmptyTrash}
              disabled={!trashStats?.count}
              loading={emptyTrashMutation.isLoading}
              style={{ 
                border: '2px solid #333',
                fontWeight: 'bold'
              }}
            >
              清空回收站
            </Button>
          </Card>
        </Col>
      </Row>

      {/* 文件列表 */}
      <Card 
        style={{ 
          border: '3px solid #333',
          borderRadius: 12,
          boxShadow: '4px 4px 0 #333'
        }}
      >
        <Table
          columns={columns}
          dataSource={trashFiles || []}
          rowKey="id"
          loading={isLoading}
          pagination={{ 
            pageSize: 10,
            showTotal: (total) => `共 ${total} 个文件`
          }}
          locale={{
            emptyText: (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="回收站是空的"
              />
            )
          }}
          scroll={{ x: 700 }}
        />
      </Card>

      {/* 提示信息 */}
      <div style={{ 
        marginTop: 16, 
        padding: 16, 
        background: '#fffbe6',
        border: '2px solid #ffe58f',
        borderRadius: 8
      }}>
        <Text type="warning">
          💡 提示：回收站中的文件仍占用存储空间。彻底删除后可释放空间。
        </Text>
      </div>
    </div>
  );
};

export default Trash;
