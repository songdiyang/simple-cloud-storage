import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Row, 
  Col, 
  Typography, 
  Button, 
  Spin, 
  message, 
  Input,
  Modal,
  Result,
  Statistic
} from 'antd';
import { 
  DownloadOutlined, 
  FileOutlined, 
  LockOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { formatBytes } from '../utils/format';
import api from '../services/api';

const { Title, Text, Paragraph } = Typography;

const ShareView = () => {
  const { shareCode } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [shareInfo, setShareInfo] = useState(null);
  const [password, setPassword] = useState('');
  const [passwordRequired, setPasswordRequired] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchShareInfo();
  }, [shareCode]);

  const fetchShareInfo = async (pwd = '') => {
    try {
      setLoading(true);
      const response = await api.get(`/api/files/share/${shareCode}/`, {
        params: { password: pwd }
      });
      setShareInfo(response.data);
      setPasswordRequired(false);
    } catch (error) {
      if (error.response?.status === 403 && error.response?.data?.error === '需要密码') {
        setPasswordRequired(true);
      } else {
        message.error(error.response?.data?.error || '分享链接无效');
        navigate('/');
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
      
      // 直接下载文件
      const response = await fetch(`/api/files/share/${shareCode}/download/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '下载失败');
      }
      
      // 获取文件blob
      const blob = await response.blob();
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = shareInfo.file_name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // 清理URL对象
      window.URL.revokeObjectURL(url);
      
      message.success('下载完成');
      
      // 刷新分享信息（更新下载次数）
      fetchShareInfo(password);
      
    } catch (error) {
      message.error(error.message || '下载失败');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '60vh' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (passwordRequired) {
    return (
      <Row justify="center" align="middle" style={{ minHeight: '60vh' }}>
        <Col xs={24} sm={16} md={12} lg={8}>
          <Card>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <LockOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              <Title level={3}>需要密码访问</Title>
              <Text type="secondary">此分享文件需要密码才能访问</Text>
            </div>
            
            <Input.Password
              placeholder="请输入访问密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onPressEnter={handlePasswordSubmit}
              size="large"
              style={{ marginBottom: 16 }}
            />
            
            <Button
              type="primary"
              block
              size="large"
              onClick={handlePasswordSubmit}
            >
              访问文件
            </Button>
          </Card>
        </Col>
      </Row>
    );
  }

  if (!shareInfo) {
    return (
      <Result
        status="404"
        title="分享不存在"
        subTitle="您访问的分享链接不存在或已被删除"
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            返回首页
          </Button>
        }
      />
    );
  }

  if (shareInfo.is_expired) {
    return (
      <Result
        status="warning"
        title="分享已过期"
        subTitle="此分享链接已过期或下载次数已达上限"
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            返回首页
          </Button>
        }
      />
    );
  }

  return (
    <Row justify="center">
      <Col xs={24} sm={20} md={16} lg={12}>
        <Card>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <FileOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 16 }} />
            <Title level={2}>{shareInfo.file_name}</Title>
            <Paragraph type="secondary">
              分享者分享了此文件，您可以免费下载
            </Paragraph>
          </div>

          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Statistic
                title="文件大小"
                value={formatBytes(shareInfo.file_size)}
                prefix={<FileOutlined />}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="下载次数"
                value={`${shareInfo.download_count}/${shareInfo.max_downloads || '∞'}`}
                prefix={<DownloadOutlined />}
              />
            </Col>
          </Row>

          {shareInfo.expire_at && (
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Text type="secondary">
                过期时间: {new Date(shareInfo.expire_at).toLocaleString()}
              </Text>
            </div>
          )}

          <div style={{ marginTop: 32, textAlign: 'center' }}>
            <Button
              type="primary"
              size="large"
              icon={<DownloadOutlined />}
              loading={downloading}
              onClick={handleDownload}
              disabled={shareInfo.is_expired}
            >
              {downloading ? '准备下载...' : '下载文件'}
            </Button>
          </div>

          {shareInfo.is_expired && (
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Text type="danger">
                <ExclamationCircleOutlined /> 此分享已过期
              </Text>
            </div>
          )}
        </Card>
      </Col>
    </Row>
  );
};

export default ShareView;