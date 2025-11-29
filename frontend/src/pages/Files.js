import React, { useState, useEffect } from 'react';
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
  Tooltip,
  List,
  Avatar
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
  const [isMobile, setIsMobile] = useState(false);

  // 检测移动设备
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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
      // 明确设置Content-Type为multipart/form-data
      return api.post('/api/files/upload/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
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
        console.error('Upload error:', error);
        const errorMsg = error.response?.data?.error || error.message || '上传失败';
        message.error(`上传失败: ${errorMsg}`);
        
        // 如果是认证错误，重定向到登录页
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
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
              onClick={() => handleShareFile(record)}
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
  const [selectedFile, setSelectedFile] = useState(null);

  const handleShareFile = (file) => {
    setSelectedFile(file);
    setShareModalVisible(true);
  };

  const handleShareModalOk = () => {
    setShareModalVisible(false);
    setSelectedFile(null);
    queryClient.invalidateQueries('my-shares');
  };

  const handleShareModalCancel = () => {
    setShareModalVisible(false);
    setSelectedFile(null);
  };

  // 移动端文件夹列表项
  const MobileFolderItem = ({ folder }) => (
    <List.Item
      style={{ 
        padding: '12px 0',
        borderBottom: '1px solid #f0f0f0',
        cursor: 'pointer'
      }}
      onClick={() => navigate(`/files/${folder.id}`)}
      actions={[
        <Popconfirm
          key="delete"
          title="确定删除这个文件夹吗？"
          onConfirm={() => deleteFolderMutation.mutate(folder.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="text" danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      ]}
    >
      <List.Item.Meta
        avatar={<Avatar icon={<FolderOutlined />} style={{ backgroundColor: '#fa709a' }} />}
        title={folder.name}
        description={`${folder.children_count} 个子文件夹, ${folder.files_count} 个文件`}
      />
    </List.Item>
  );

  // 移动端文件列表项
  const MobileFileItem = ({ file }) => (
    <List.Item
      style={{ padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}
      actions={[
        <Button 
          key="download"
          type="text" 
          size="small" 
          icon={<CloudDownloadOutlined />}
          onClick={() => downloadFile(file)}
        />,
        <Button 
          key="share"
          type="text" 
          size="small" 
          icon={<ShareAltOutlined />}
          onClick={() => handleShareFile(file)}
        />,
        <Popconfirm
          key="delete"
          title="确定删除这个文件吗？"
          onConfirm={() => deleteFileMutation.mutate(file.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="text" danger size="small" icon={<DeleteOutlined />} />
        </Popconfirm>
      ]}
    >
      <List.Item.Meta
        avatar={
          <Avatar 
            icon={<FileOutlined />} 
            style={{ backgroundColor: getFileIconColor(file.file_extension) }} 
          />
        }
        title={
          <Tooltip title={file.original_name}>
            <Text ellipsis style={{ maxWidth: '200px' }}>{file.name}</Text>
          </Tooltip>
        }
        description={
          <Space direction="vertical" size="small">
            <Text type="secondary">{file.size_display}</Text>
            <Tag color="blue" size="small">{file.file_type || '未知'}</Tag>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {new Date(file.created_at).toLocaleString()}
            </Text>
          </Space>
        }
      />
    </List.Item>
  );

  return (
    <div>
      <div style={{ 
        marginBottom: isMobile ? '16px' : '24px', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        flexDirection: isMobile ? 'column' : 'row',
        gap: isMobile ? '12px' : '0'
      }}>
        <Space direction={isMobile ? 'vertical' : 'horizontal'} style={{ width: isMobile ? '100%' : 'auto' }}>
          {folderId && (
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/files')}
              style={{ width: isMobile ? '100%' : 'auto' }}
            >
              返回上级
            </Button>
          )}
          <Title level={isMobile ? 4 : 2} style={{ color: '#333', margin: 0 }}>
            我的文件
          </Title>
        </Space>
        
        <Space direction={isMobile ? 'vertical' : 'horizontal'} style={{ width: isMobile ? '100%' : 'auto' }}>
          <Button 
            type="primary" 
            icon={<UploadOutlined />}
            onClick={() => setUploadModalVisible(true)}
            className="cel-button"
            style={{ width: isMobile ? '100%' : 'auto' }}
          >
            上传文件
          </Button>
          <Button 
            icon={<FolderAddOutlined />}
            onClick={() => setFolderModalVisible(true)}
            className="cel-button"
            style={{ width: isMobile ? '100%' : 'auto' }}
          >
            新建文件夹
          </Button>
        </Space>
      </div>

      {isMobile ? (
        // 移动端视图
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {folders.length > 0 && (
            <Card className="cel-card" title="文件夹" size="small">
              <List
                dataSource={folders}
                renderItem={MobileFolderItem}
                size="small"
              />
            </Card>
          )}
          
          <Card className="cel-card" title="文件" size="small">
            <List
              dataSource={filesData?.results || filesData || []}
              renderItem={MobileFileItem}
              loading={isLoading}
              size="small"
              pagination={
                filesData?.count > 20 ? {
                  total: filesData?.count,
                  pageSize: 20,
                  showSizeChanger: false,
                  showQuickJumper: false,
                  simple: true,
                } : false
              }
            />
          </Card>
        </Space>
      ) : (
        // 桌面端视图
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
      )}

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
        onSuccess={handleShareModalOk}
        file={selectedFile}
      />
    </div>
  );
};

export default Files;