import React, { useState } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  Table, 
  Space, 
  Tag, 
  message, 
  Spin,
  Descriptions,
  Modal,
  Typography,
  Alert,
  Result
} from 'antd';
import { 
  SearchOutlined, 
  DownloadOutlined, 
  FileOutlined,
  LockOutlined,
  CloudUploadOutlined,
  SaveOutlined,
  FolderOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import api from '../services/api';
import FolderSelector from '../components/FolderSelector';

const { Title, Text } = Typography;

const FileSearch = () => {
  const [shareCode, setShareCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [passwordInput, setPasswordInput] = useState('');
  const [passwordRequired, setPasswordRequired] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showFolderSelector, setShowFolderSelector] = useState(false);
  
  // 密码验证相关状态
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordVerifying, setPasswordVerifying] = useState(false);
  const [remainingAttempts, setRemainingAttempts] = useState(3);
  const [isLocked, setIsLocked] = useState(false);
  const [lockoutTime, setLockoutTime] = useState(0);
  const [passwordVerified, setPasswordVerified] = useState(false);
  const [pendingShareCode, setPendingShareCode] = useState('');

  const handleSearch = async () => {
    if (!shareCode.trim()) {
      message.error('请输入分享码');
      return;
    }

    try {
      setLoading(true);
      
      const response = await api.get(`/api/files/share/${shareCode.trim()}/`, {
        params: passwordInput ? { password: passwordInput } : {}
      });
      
      const fileInfo = response.data;
      
      // 添加到搜索结果（避免重复）
      setSearchResults(prev => {
        const exists = prev.find(item => item.share_code === shareCode.trim());
        if (exists) {
          message.warning('该分享文件已在结果列表中');
          return prev;
        }
        return [...prev, {
          ...fileInfo,
          share_code: shareCode.trim(),
          search_time: new Date().toISOString()
        }];
      });
      
      setShareCode('');
      setPasswordInput('');
      setPasswordRequired(false);
      setPasswordVerified(false);
      message.success('文件信息获取成功！');
      
    } catch (error) {
      if (error.response?.status === 403 && error.response?.data?.password_required) {
        // 需要密码，打开密码验证模态框
        setPendingShareCode(shareCode.trim());
        setRemainingAttempts(error.response?.data?.remaining_attempts || 3);
        setIsLocked(false);
        setPasswordVerified(false);
        setPasswordInput('');
        setShowPasswordModal(true);
      } else if (error.response?.status === 429) {
        // 尝试次数过多，被锁定
        setIsLocked(true);
        setLockoutTime(error.response?.data?.lockout_time || 300);
        setPendingShareCode(shareCode.trim());
        setShowPasswordModal(true);
      } else if (error.response?.status === 404) {
        message.error('分享码不存在或已过期');
      } else {
        message.error(error.response?.data?.error || '获取文件信息失败');
      }
    } finally {
      setLoading(false);
    }
  };

  // 密码验证函数
  const handleVerifyPassword = async () => {
    if (!passwordInput.trim()) {
      message.error('请输入密码');
      return;
    }

    try {
      setPasswordVerifying(true);
      
      const response = await api.post(`/api/files/share/${pendingShareCode}/verify-password/`, {
        password: passwordInput
      });
      
      if (response.data.success) {
        // 密码正确
        setPasswordVerified(true);
        setRemainingAttempts(3);
        message.success('密码正确！');
        
        // 将文件信息添加到搜索结果
        const fileInfo = response.data;
        setSearchResults(prev => {
          const exists = prev.find(item => item.share_code === pendingShareCode);
          if (exists) {
            return prev;
          }
          return [...prev, {
            ...fileInfo,
            share_code: pendingShareCode,
            search_time: new Date().toISOString(),
            password_verified: true,
            verified_password: passwordInput
          }];
        });
        
        // 2秒后关闭模态框
        setTimeout(() => {
          setShowPasswordModal(false);
          setPasswordInput('');
          setShareCode('');
        }, 1500);
      }
      
    } catch (error) {
      if (error.response?.status === 403) {
        // 密码错误
        const remaining = error.response?.data?.remaining;
        setRemainingAttempts(remaining || 0);
        message.error(error.response?.data?.error || '密码错误');
      } else if (error.response?.status === 429) {
        // 尝试次数过多，被锁定
        setIsLocked(true);
        setLockoutTime(error.response?.data?.lockout_time || 300);
        setRemainingAttempts(0);
        message.error(error.response?.data?.error || '尝试次数过多，请稍后再试');
      } else {
        message.error(error.response?.data?.error || '验证失败');
      }
    } finally {
      setPasswordVerifying(false);
    }
  };

  // 关闭密码模态框
  const handleClosePasswordModal = () => {
    setShowPasswordModal(false);
    setPasswordInput('');
    setPasswordVerified(false);
    setPendingShareCode('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
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
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('zh-CN');
  };

  const getFileTypeColor = (fileName) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    const colorMap = {
      pdf: 'red',
      doc: 'blue', docx: 'blue',
      xls: 'green', xlsx: 'green',
      ppt: 'orange', pptx: 'orange',
      jpg: 'purple', jpeg: 'purple', png: 'purple', gif: 'purple',
      mp4: 'cyan', avi: 'cyan', mov: 'cyan',
      zip: 'geekblue', rar: 'geekblue',
      txt: 'default', md: 'default'
    };
    return colorMap[ext] || 'default';
  };

  const handlePreview = (record) => {
    setSelectedFile(record);
    setShowPreviewModal(true);
    setPasswordRequired(false);
    setPasswordInput('');
  };

  const handleDownload = async (fileInfo, password = null) => {
    try {
      setDownloading(true);
      
      // 如果文件有已验证的密码，使用它
      const usePassword = password || fileInfo.verified_password || null;
      const requestData = usePassword ? { password: usePassword } : {};
      
      const response = await api.post(`/api/files/share/${fileInfo.share_code}/download/`, 
        requestData,
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
      let filename = fileInfo.file_name || 'download';
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
      
      // 更新搜索结果中的下载次数
      setSearchResults(prev => 
        prev.map(item => 
          item.share_code === fileInfo.share_code 
            ? { ...item, download_count: item.download_count + 1 }
            : item
        )
      );
      
    } catch (error) {
      if (error.response?.status === 403) {
        const remaining = error.response?.data?.remaining;
        if (remaining !== undefined) {
          message.error(`密码错误，还剩${remaining}次尝试机会`);
        } else {
          message.error('密码错误或文件需要密码');
        }
      } else if (error.response?.status === 429) {
        message.error('尝试次数过多，请5分钟后再试');
      } else {
        message.error(error.response?.data?.error || '下载失败');
      }
    } finally {
      setDownloading(false);
    }
  };

  const handleSaveToCloud = async (folderId = null) => {
    if (!selectedFile) return;

    try {
      setSaving(true);
      
      const saveData = {
        share_code: selectedFile.share_code,
        folder_id: folderId,
        password: selectedFile.verified_password || (passwordRequired ? passwordInput : undefined)
      };

      const response = await api.post('/api/files/save-shared-file/', saveData);
      
      message.success('文件已保存到您的云盘！');
      setShowSaveModal(false);
      setShowPreviewModal(false);
      
    } catch (error) {
      if (error.response?.status === 401) {
        message.error('请先登录后再保存文件到云盘');
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

  const columns = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (text, record) => (
        <Space>
          <FileOutlined style={{ color: '#1890ff' }} />
          <span>{text}</span>
          <Tag color={getFileTypeColor(text)}>
            {text.split('.').pop()?.toUpperCase()}
          </Tag>
        </Space>
      )
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size) => formatFileSize(size)
    },
    {
      title: '分享码',
      dataIndex: 'share_code',
      key: 'share_code',
      render: (code) => (
        <Text code copyable={{ text: code }}>
          {code}
        </Text>
      )
    },
    {
      title: '下载次数',
      dataIndex: 'download_count',
      key: 'download_count',
      render: (count, record) => (
        <Text>
          {count} / {record.max_downloads || '无限制'}
        </Text>
      )
    },
    {
      title: '搜索时间',
      dataIndex: 'search_time',
      key: 'search_time',
      render: (time) => formatDate(time)
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            查看
          </Button>
          <Button
            type="default"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
            loading={downloading}
            disabled={
              record.max_downloads > 0 && 
              record.download_count >= record.max_downloads
            }
          >
            下载
          </Button>
        </Space>
      )
    }
  ];

  const renderPreviewModal = () => {
    if (!selectedFile) return null;

    return (
      <Modal
        title={
          <Space>
            <FileOutlined />
            文件详情
          </Space>
        }
        open={showPreviewModal}
        onCancel={() => {
          setShowPreviewModal(false);
          setPasswordRequired(false);
          setPasswordInput('');
        }}
        footer={null}
        width={700}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <FileOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
          <Title level={3}>{selectedFile.file_name}</Title>
        </div>

        <Descriptions column={1} bordered style={{ marginBottom: 24 }}>
          <Descriptions.Item label="文件大小">
            <Tag color="blue">{formatFileSize(selectedFile.file_size)}</Tag>
          </Descriptions.Item>
          
          <Descriptions.Item label="分享码">
            <Text code copyable={{ text: selectedFile.share_code }}>
              {selectedFile.share_code}
            </Text>
          </Descriptions.Item>
          
          <Descriptions.Item label="下载次数">
            <Text strong>
              {selectedFile.download_count} / {selectedFile.max_downloads || '无限制'}
            </Text>
          </Descriptions.Item>

          {selectedFile.expire_at && (
            <Descriptions.Item label="过期时间">
              <Text type={new Date(selectedFile.expire_at) < new Date() ? 'danger' : 'success'}>
                {formatDate(selectedFile.expire_at)}
              </Text>
            </Descriptions.Item>
          )}

          {selectedFile.password_protected && (
            <Descriptions.Item label="访问保护">
              <Tag color="orange"><LockOutlined /> 密码保护</Tag>
            </Descriptions.Item>
          )}

          <Descriptions.Item label="分享时间">
            {formatDate(selectedFile.created_at)}
          </Descriptions.Item>
        </Descriptions>

        {selectedFile.password_protected && (
          <div style={{ marginBottom: 16 }}>
            <Input.Password
              placeholder="请输入访问密码"
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              prefix={<LockOutlined />}
            />
          </div>
        )}

        <Space direction="vertical" style={{ width: '100%' }}>
          <Button
            type="primary"
            size="large"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(selectedFile, passwordInput)}
            loading={downloading}
            disabled={selectedFile.password_protected && !passwordInput.trim()}
            block
          >
            直接下载到本地
          </Button>
          
          <Button
            size="large"
            icon={<CloudUploadOutlined />}
            onClick={() => {
              if (selectedFile.password_protected && !passwordInput.trim()) {
                message.error('请先输入密码');
                return;
              }
              setShowSaveModal(true);
            }}
            loading={saving}
            disabled={selectedFile.password_protected && !passwordInput.trim()}
            block
          >
            保存到云盘
          </Button>
        </Space>
      </Modal>
    );
  };

  const renderSaveModal = () => {
    if (!selectedFile) return null;

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
          message={`将文件 "${selectedFile.file_name}" 保存到您的云盘`}
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

  // 密码验证模态框
  const renderPasswordModal = () => {
    return (
      <Modal
        title={
          <Space>
            <LockOutlined />
            密码验证
          </Space>
        }
        open={showPasswordModal}
        onCancel={handleClosePasswordModal}
        footer={null}
        width={450}
        centered
      >
        {isLocked ? (
          // 被锁定状态
          <Result
            status="warning"
            icon={<ExclamationCircleOutlined style={{ color: '#faad14' }} />}
            title="尝试次数已用完"
            subTitle={`请等待 ${Math.ceil(lockoutTime / 60)} 分钟后再试`}
            extra={
              <Button onClick={handleClosePasswordModal}>
                知道了
              </Button>
            }
          />
        ) : passwordVerified ? (
          // 验证成功状态
          <Result
            status="success"
            icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            title="密码正确"
            subTitle="文件已添加到搜索结果，您现在可以下载文件了"
          />
        ) : (
          // 输入密码状态
          <div>
            <Alert
              message="该分享文件需要密码"
              description={`请输入密码访问文件，还剩 ${remainingAttempts} 次尝试机会`}
              type={remainingAttempts <= 1 ? 'error' : 'warning'}
              showIcon
              style={{ marginBottom: 20 }}
            />
            
            <Input.Password
              placeholder="请输入访问密码"
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              onPressEnter={handleVerifyPassword}
              prefix={<LockOutlined />}
              size="large"
              style={{ marginBottom: 16 }}
            />
            
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 16 
            }}>
              <Text type="secondary">
                剩余尝试次数：
                <Text 
                  strong 
                  type={remainingAttempts <= 1 ? 'danger' : 'warning'}
                >
                  {remainingAttempts}
                </Text>
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                5分钟内最多尝试3次
              </Text>
            </div>
            
            <Space style={{ width: '100%' }} direction="vertical">
              <Button
                type="primary"
                size="large"
                block
                onClick={handleVerifyPassword}
                loading={passwordVerifying}
                disabled={!passwordInput.trim()}
              >
                验证密码
              </Button>
              <Button
                size="large"
                block
                onClick={handleClosePasswordModal}
              >
                取消
              </Button>
            </Space>
          </div>
        )}
      </Modal>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: '24px' }}>
        <Title level={3} style={{ marginBottom: '20px' }}>
          <SearchOutlined /> 搜索分享文件
        </Title>
        
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="请输入分享码"
            value={shareCode}
            onChange={(e) => setShareCode(e.target.value)}
            onKeyPress={handleKeyPress}
            style={{ flex: 1 }}
            prefix={<SearchOutlined />}
          />
          <Button 
            type="primary" 
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={loading}
          >
            搜索
          </Button>
        </Space.Compact>

        {passwordRequired && (
          <Alert
            message="该分享文件需要密码"
            description="请在下方输入密码，然后重新搜索"
            type="warning"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Card>

      <Card>
        <Title level={4} style={{ marginBottom: '16px' }}>
          搜索结果 ({searchResults.length})
        </Title>
        
        <Table
          columns={columns}
          dataSource={searchResults}
          rowKey="share_code"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共找到 ${total} 个文件`,
            locale: { emptyText: '暂无搜索结果，请输入分享码进行搜索' }
          }}
          locale={{ emptyText: '暂无搜索结果，请输入分享码进行搜索' }}
        />
      </Card>

      {renderPreviewModal()}
      {renderSaveModal()}
      {renderPasswordModal()}
      
      <FolderSelector
        visible={showFolderSelector}
        onCancel={() => setShowFolderSelector(false)}
        onConfirm={handleFolderSelect}
        loading={saving}
      />
    </div>
  );
};

export default FileSearch;