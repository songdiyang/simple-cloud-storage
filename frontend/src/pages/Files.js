import React, { useState } from 'react';
import { 
  Card, 
  Button, 
  Table, 
  Modal, 
  Form, 
  Input, 
  Upload, 
  message,
  Space,
  Popconfirm,
  Tag,
  Typography,
  Row,
  Col,
  Tooltip
} from 'antd';
import { 
  UploadOutlined, 
  FolderAddOutlined, 
  DeleteOutlined,
  ShareAltOutlined,
  FileOutlined,
  FolderOutlined,
  ArrowLeftOutlined,
  CloudDownloadOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import api from '../services/api';
import ShareModal from '../components/ShareModal';

const { Title, Text } = Typography;
const { Dragger } = Upload;

const Files = () => {
  const { folderId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [folderModalVisible, setFolderModalVisible] = useState(false);
  const [folderForm] = Form.useForm();

  const { data: folders = [] } = useQuery(
    ['folders', folderId],
    () => api.get('/api/files/folders/', { 
      params: folderId ? { parent_id: folderId } : {} 
    }).then(res => res.data)
  );

  const { data: filesData, isLoading } = useQuery(
    ['files', folderId],
    () => api.get('/api/files/', { 
      params: folderId ? { folder_id: folderId } : {} 
    }).then(res => res.data),
    { refetchOnWindowFocus: false }
  );

  const uploadMutation = useMutation(
    (fileObj) => {
      const data = new FormData();
      data.append('file', fileObj);
      if (folderId) {
        data.append('folder_id', folderId);
      }
      // 为FormData请求移除Content-Type，让浏览器自动设置multipart/form-data
      return api.post('/api/files/upload/', data, {
        headers: {
          'Content-Type': undefined,
        },
      });
    },
    {
      onSuccess: () => {
        message.success('文件上传成功！');
        setUploadModalVisible(false);
        queryClient.invalidateQueries('files');
        queryClient.invalidateQueries('storage-info');
      },
      onError: (error) => {
        const errorMsg = error.response?.data?.error || '上传失败';
        message.error(errorMsg);
      }
    }
  );

  const createFolderMutation = useMutation(
    (data) => api.post('/api/files/folders/create/', {
      ...data,
      parent_id: folderId
    }),
    {
      onSuccess: () => {
        message.success('文件夹创建成功！');
        setFolderModalVisible(false);
        folderForm.resetFields();
        queryClient.invalidateQueries('folders');
      },
      onError: (error) => {
        const errorMsg = error.response?.data?.error || '创建失败';
        message.error(errorMsg);
      }
    }
  );

  const deleteFileMutation = useMutation(
    (fileId) => api.delete(`/api/files/${fileId}/delete/`),
    {
      onSuccess: () => {
        message.success('文件删除成功！');
        queryClient.invalidateQueries('files');
        queryClient.invalidateQueries('storage-info');
      },
      onError: (error) => {
        const errorMsg = error.response?.data?.error || '删除失败';
        message.error(errorMsg);
      }
    }
  );

  const downloadFile = async (file) => {
    try {
      message.loading('正在准备下载...', 0);
      
      // 方式1: 获取下载URL
      const response = await api.get(`/api/files/${file.id}/download-url/`);
      const { download_url, filename, method } = response.data;
      
      if (method === 'direct') {
        // 直接下载API
        message.destroy();
        message.loading('正在下载文件...', 0);
        
        const downloadResponse = await api.get(`/api/files/${file.id}/download/`, {
          responseType: 'blob'
        });
        
        // 创建Blob URL
        const blob = new Blob([downloadResponse.data], { type: file.mime_type });
        const url = window.URL.createObjectURL(blob);
        
        // 创建隐藏的a标签进行下载
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 清理URL对象
        window.URL.revokeObjectURL(url);
        
        message.destroy();
        message.success('文件下载完成！');
      } else {
        // Swift临时URL下载
        // 创建隐藏的a标签进行下载
        const link = document.createElement('a');
        link.href = download_url;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        message.destroy();
        message.success('文件下载开始！');
      }
    } catch (error) {
      message.destroy();
      
      // 如果URL下载失败，尝试直接流式下载
      try {
        message.loading('正在下载文件...', 0);
        
        const response = await api.get(`/api/files/${file.id}/download/`, {
          responseType: 'blob'
        });
        
        // 创建Blob URL
        const blob = new Blob([response.data], { type: file.mime_type });
        const url = window.URL.createObjectURL(blob);
        
        // 创建隐藏的a标签进行下载
        const link = document.createElement('a');
        link.href = url;
        link.download = file.original_name;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 清理URL对象
        window.URL.revokeObjectURL(url);
        
        message.destroy();
        message.success('文件下载完成！');
      } catch (streamError) {
        message.destroy();
        const errorMsg = error.response?.data?.error || streamError.message || '下载失败';
        message.error(`下载失败: ${errorMsg}`);
      }
    }
  };

  const deleteFolderMutation = useMutation(
    (folderId) => api.delete(`/api/files/folders/${folderId}/delete/`),
    {
      onSuccess: () => {
        message.success('文件夹删除成功！');
        queryClient.invalidateQueries('folders');
      },
      onError: (error) => {
        const errorMsg = error.response?.data?.error || '删除失败';
        message.error(errorMsg);
      }
    }
  );

  const uploadProps = {
    name: 'file',
    multiple: false,
    customRequest: ({ file, onSuccess, onError }) => {
      uploadMutation.mutate(file, {
        onSuccess: () => onSuccess(),
        onError: (error) => onError(error)
      });
    },
    showUploadList: false,
  };

  const folderColumns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <FolderOutlined style={{ color: '#fa709a', fontSize: '18px' }} />
          <Button 
            type="link" 
            onClick={() => navigate(`/files/${record.id}`)}
            style={{ padding: 0, height: 'auto' }}
          >
            {text}
          </Button>
        </Space>
      ),
    },
    {
      title: '文件数量',
      dataIndex: 'files_count',
      key: 'files_count',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Popconfirm
            title="确定删除这个文件夹吗？"
            onConfirm={() => deleteFolderMutation.mutate(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="text" 
              danger 
              icon={<DeleteOutlined />}
              size="small"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const fileColumns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <FileOutlined style={{ 
            color: getFileIconColor(record.file_extension),
            fontSize: '18px' 
          }} />
          <Tooltip title={record.original_name}>
            <Text ellipsis style={{ maxWidth: '200px' }}>{text}</Text>
          </Tooltip>
        </Space>
      ),
    },
    {
      title: '大小',
      dataIndex: 'size_display',
      key: 'size_display',
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      render: (type) => (
        <Tag color="blue">{type || '未知'}</Tag>
      ),
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="下载文件">
            <Button 
              type="text" 
              icon={<CloudDownloadOutlined />}
              size="small"
              onClick={() => downloadFile(record)}
            />
          </Tooltip>
          <Tooltip title="分享文件">
            <Button 
              type="text" 
              icon={<ShareAltOutlined />}
              size="small"
              onClick={() => handleShareFile(record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除这个文件吗？"
            onConfirm={() => deleteFileMutation.mutate(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除文件">
              <Button 
                type="text" 
                danger 
                icon={<DeleteOutlined />}
                size="small"
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const getFileIconColor = (extension) => {
    const colorMap = {
      '.pdf': '#ff6b6b',
      '.doc': '#4facfe',
      '.xls': '#43e97b',
      '.jpg': '#fa709a',
      '.png': '#fee140',
      '.mp4': '#30cfd0',
      '.mp3': '#a8edea',
      '.zip': '#ff9a9e',
    };
    return colorMap[extension] || '#667eea';
  };

  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState(null);

  const handleShareFile = (fileId) => {
    setSelectedFileId(fileId);
    setShareModalVisible(true);
  };

  const handleShareModalOk = (shareData) => {
    setShareModalVisible(false);
    setSelectedFileId(null);
    queryClient.invalidateQueries('my-shares');
  };

  const handleShareModalCancel = () => {
    setShareModalVisible(false);
    setSelectedFileId(null);
  };

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          {folderId && (
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/files')}
            >
              返回上级
            </Button>
          )}
          <Title level={2} style={{ color: '#333', margin: 0 }}>
            我的文件
          </Title>
        </Space>
        
        <Space>
          <Button 
            type="primary" 
            icon={<UploadOutlined />}
            onClick={() => setUploadModalVisible(true)}
            className="cel-button"
          >
            上传文件
          </Button>
          <Button 
            icon={<FolderAddOutlined />}
            onClick={() => setFolderModalVisible(true)}
            className="cel-button"
          >
            新建文件夹
          </Button>
        </Space>
      </div>

      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card className="cel-card" title="文件夹">
            <Table
              columns={folderColumns}
              dataSource={folders}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        <Col span={24}>
          <Card className="cel-card" title="文件">
            <Table
              columns={fileColumns}
              dataSource={filesData?.results || filesData || []}
              rowKey="id"
              loading={isLoading}
              pagination={{
                total: filesData?.count,
                pageSize: 20,
                showSizeChanger: false,
                showQuickJumper: true,
              }}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* 上传文件模态框 */}
      <Modal
        title="上传文件"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
        width={600}
      >
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <UploadOutlined style={{ fontSize: '48px', color: '#667eea' }} />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个文件上传，文件大小不能超过系统限制
          </p>
        </Dragger>
      </Modal>

      {/* 创建文件夹模态框 */}
      <Modal
        title="新建文件夹"
        open={folderModalVisible}
        onOk={() => folderForm.submit()}
        onCancel={() => setFolderModalVisible(false)}
        confirmLoading={createFolderMutation.isLoading}
      >
        <Form
          form={folderForm}
          layout="vertical"
          onFinish={(values) => createFolderMutation.mutate(values)}
        >
          <Form.Item
            name="name"
            label="文件夹名称"
            rules={[{ required: true, message: '请输入文件夹名称' }]}
          >
            <Input placeholder="请输入文件夹名称" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 分享模态框 */}
      <ShareModal
        visible={shareModalVisible}
        onCancel={handleShareModalCancel}
        onOk={handleShareModalOk}
        fileId={selectedFileId}
      />
    </div>
  );
};

export default Files;