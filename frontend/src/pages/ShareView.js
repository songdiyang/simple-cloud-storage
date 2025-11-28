import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Button, 
  Input, 
  Spin, 
  message, 
  Descriptions, 
  Tag,
  Space,
  Typography,
  Alert,
  Modal
} from 'antd';
import { 
  DownloadOutlined, 
  LockOutlined, 
  FileOutlined,
  ClockCircleOutlined,
  NumberOutlined,
  CloudUploadOutlined,
  SaveOutlined,
  FolderOutlined
} from '@ant-design/icons';
import api from '../services/api';
import FolderSelector from '../components/FolderSelector';

const { Title, Text } = Typography;

const ShareView = () => {
  const { shareCode } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [shareInfo, setShareInfo] = useState(null);
  const [password, setPassword] = useState('');
  const [passwordRequired, setPasswordRequired] = useState(false);
  const [error, setError] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showFolderSelector, setShowFolderSelector] = useState(false);

  useEffect(() => {
    fetchShareInfo();
  }, [shareCode]);

  const fetchShareInfo = async (pwd = '') => {
    try {
      setLoading(true);
      setError('');
      
      const response = await api.get(`/api/files/share/${shareCode}/`, {
        params: pwd ? { password: pwd } : {}
      });
      
      setShareInfo(response.data);
      setPasswordRequired(false);
    } catch (error) {
      if (error.response?.status === 403 && error.response?.data?.error === '需要密码') {
        setPasswordRequired(true);
      } else if (error.response?.status === 404) {
        setError('分享链接不存在或已过期');
      } else {
        setError(error.response?.data?.error || '获取分享信息失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = () => {
    if (!password.trim()) {
      message.error('请输入密码');
      return;
    }
    fetchShareInfo(password);
  };

  const handleDownload = async () => {
    try {
      setDownloading(true);
      
      const response = await api.post(`/api/files/share/${shareCode}/download/`, 
        passwordRequired ? { password } : {},
        {
          responseType: 'blob'
        }
      );

      // 创建下载链接
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // 从响应头获取文件名
      const contentDisposition = response.headers['content-disposition'];
      let filename = shareInfo?.file_name || 'download';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success('文件下载成功！');
      
      // 更新下载次数
      if (shareInfo) {
        setShareInfo({
          ...shareInfo,
          download_count: shareInfo.download_count + 1
        });
      }
    } catch (error) {
      message.error(error.response?.data?.error || '下载失败');
    } finally {
      setDownloading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleString('zh-CN');
  };

  const handleSaveToCloud = async (folderId = null) => {
    try {
      setSaving(true);
      
      const saveData = {
        share_code: shareCode,
        folder_id: folderId,
        password: passwordRequired ? password : undefined
      };

      const response = await api.post('/api/files/save-shared-file/', saveData);
      
      message.success('文件已保存到您的云盘！');
      setShowSaveModal(false);
      
      // 询问是否跳转到文件管理页面
      setTimeout(() => {
        if (window.confirm('文件已保存成功！是否前往文件管理页面查看？')) {
          navigate('/login');
        }
      }, 1000);
      
    } catch (error) {
      if (error.response?.status === 401) {
        message.error('请先登录后再保存文件到云盘');
        navigate('/login');
      } else {
        message.error(error.response?.data?.error || '保存到云盘失败');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleFolderSelect = (folderId) => {
    setShowFolderSelector(false);
    handleSaveToCloud(folderId);
  };

  const renderSaveModal = () => {
    return (
      <Modal
        title={
          <Space>
            <CloudUploadOutlined />
            保存到云盘
          </Space>
        }
        open={showSaveModal}
        onCancel={() => setShowSaveModal(false)}
        footer={null}
        width={500}
      >
        <Alert
          message={`将文件 "${shareInfo?.file_name}" 保存到您的云盘`}
          type="info"
          showIcon
          style={{ marginBottom: 20 }}
        />
        
        <Space direction="vertical" style={{ width: '100%' }}>
          <Button 
            block 
            icon={<SaveOutlined />}
            onClick={() => handleSaveToCloud(null)}
            loading={saving}
          >
            保存到根目录
          </Button>
          
          <Button 
            block 
            icon={<FolderOutlined />}
            onClick={() => {
              setShowSaveModal(false);
              setShowFolderSelector(true);
            }}
            loading={saving}
          >
            选择文件夹保存
          </Button>
          
          <Button onClick={() => setShowSaveModal(false)}>
            取消
          </Button>
        </Space>
      </Modal>
    );
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '60vh' 
      }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: 600, margin: '50px auto' }}>
        <Alert
          message="访问失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button type="primary" onClick={() => navigate('/login')}>
              返回登录
            </Button>
          }
        />
      </div>
    );
  }

  if (passwordRequired && !shareInfo) {
    return (
      <div style={{ maxWidth: 400, margin: '100px auto' }}>
        <Card>
          <Title level={3} style={{ textAlign: 'center', marginBottom: 30 }}>
            <LockOutlined /> 访问受保护的分享
          </Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Input.Password
              placeholder="请输入访问密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onPressEnter={handlePasswordSubmit}
            />
            <Button 
              type="primary" 
              block 
              onClick={handlePasswordSubmit}
              loading={loading}
            >
              解锁访问
            </Button>
          </Space>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: '50px auto', padding: '0 20px' }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 30 }}>
          <FileOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
          <Title level={2}>{shareInfo.file_name}</Title>
        </div>

        <Descriptions column={1} bordered style={{ marginBottom: 30 }}>
          <Descriptions.Item label="文件大小">
            <Tag color="blue">{formatFileSize(shareInfo.file_size)}</Tag>
          </Descriptions.Item>
          
          <Descriptions.Item label="下载次数">
            <Space>
              <NumberOutlined />
              <Text strong>
                {shareInfo.download_count} / {shareInfo.max_downloads || '无限制'}
              </Text>
            </Space>
          </Descriptions.Item>

          {shareInfo.expire_at && (
            <Descriptions.Item label="过期时间">
              <Space>
                <ClockCircleOutlined />
                <Text type={new Date(shareInfo.expire_at) < new Date() ? 'danger' : 'success'}>
                  {formatDate(shareInfo.expire_at)}
                </Text>
              </Space>
            </Descriptions.Item>
          )}

          {shareInfo.password_protected && (
            <Descriptions.Item label="访问保护">
              <Tag color="orange"><LockOutlined /> 密码保护</Tag>
            </Descriptions.Item>
          )}

          <Descriptions.Item label="分享时间">
            {formatDate(shareInfo.created_at)}
          </Descriptions.Item>
        </Descriptions>

        <div style={{ textAlign: 'center' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button
              type="primary"
              size="large"
              icon={<DownloadOutlined />}
              onClick={handleDownload}
              loading={downloading}
              disabled={
                shareInfo.max_downloads > 0 && 
                shareInfo.download_count >= shareInfo.max_downloads
              }
              block
            >
              {shareInfo.max_downloads > 0 && 
               shareInfo.download_count >= shareInfo.max_downloads
                ? '下载次数已用完'
                : '直接下载到本地'
              }
            </Button>
            
            <Button
              size="large"
              icon={<CloudUploadOutlined />}
              onClick={() => setShowSaveModal(true)}
              loading={saving}
              block
            >
              保存到云盘
            </Button>
          </Space>
        </div>

        <div style={{ textAlign: 'center', marginTop: 20 }}>
          <Button type="link" onClick={() => navigate('/login')}>
            返回登录页面
          </Button>
        </div>
      </Card>
      
      {renderSaveModal()}
      
      <FolderSelector
        visible={showFolderSelector}
        onCancel={() => setShowFolderSelector(false)}
        onConfirm={handleFolderSelect}
        loading={saving}
      />
    </div>
  );
};

export default ShareView;