import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Typography, message, Spin, Alert } from 'antd';
import { UserOutlined, LockOutlined, CloudOutlined, ReloadOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const { Title, Text } = Typography;

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState({ checking: true, online: false });
  const { login } = useAuth();
  const navigate = useNavigate();

  // 检查API连接状态
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await api.get('/api/auth/', { timeout: 5000 });
        setApiStatus({ checking: false, online: true });
      } catch (error) {
        setApiStatus({ checking: false, online: false });
        console.warn('API连接检查失败:', error.message);
      }
    };

    checkApiStatus();
  }, []);

  const onFinish = async (values) => {
    setLoading(true);
    
    try {
      const result = await login(values);
      if (result.success) {
        message.success('登录成功！正在跳转...');
        setTimeout(() => navigate('/dashboard'), 1000);
      } else {
        // 使用 alert 弹窗显示错误，不改变界面
        const errorMsg = result.error || '登录失败，请稍后重试';
        alert(errorMsg);
      }
    } catch (error) {
      alert('网络连接异常，请检查网络后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleRetryApi = () => {
    setApiStatus({ checking: true, online: false });
    setTimeout(() => {
      checkApiStatus();
    }, 1000);
  };

  const checkApiStatus = async () => {
    try {
      await api.get('/api/auth/', { timeout: 5000 });
      setApiStatus({ checking: false, online: true });
    } catch (error) {
      setApiStatus({ checking: false, online: false });
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '16px',
      background: '#ffffff', /* 纯白背景 */
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* API状态提示 */}
      {!apiStatus.checking && !apiStatus.online && (
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
          width: '90%',
          maxWidth: '400px'
        }}>
          <Alert
            message="服务连接失败"
            description="无法连接到服务器，请检查网络连接或稍后重试。"
            type="error"
            showIcon
            closable={false}
            action={
              <Button size="small" onClick={handleRetryApi}>
                重试
              </Button>
            }
            style={{ 
              borderRadius: '0', /* 无圆角 */
              border: '1px solid #000000' /* 黑色边框 */
            }}
          />
        </div>
      )}

      <Card
        style={{
          width: '100%',
          maxWidth: '400px',
          padding: '24px',
          border: '1px solid #000000', /* 黑色边框 */
          borderRadius: '0', /* 无圆角 */
          boxShadow: 'none' /* 去除阴影 */
        }}
        bodyStyle={{ 
          padding: 0,
          background: '#ffffff' /* 白色背景 */
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '64px',
            height: '64px',
            background: '#000000', /* 纯黑色 */
            borderRadius: '0', /* 无圆角 - 方形 */
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff', /* 白色文字 */
            fontSize: '28px',
            margin: '0 auto 20px'
          }}>
            <CloudOutlined />
          </div>
          <Title level={3} style={{ 
            color: '#000000', /* 纯黑色 */
            margin: '0 0 8px 0',
            fontSize: '24px',
            fontWeight: 400 /* 减小字重 */
          }}>
            登录
          </Title>
          <Text style={{ 
            color: '#000000', /* 纯黑色 */
            fontSize: '14px'
          }}>
            欢迎使用云存储系统
          </Text>
        </div>


          <Form
            name="login"
            onFinish={onFinish}
            layout="vertical"
            size="large"
            style={{ marginTop: '24px' }}
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
              style={{ marginBottom: '16px' }}
            >
              <Input
                prefix={<UserOutlined style={{ color: '#000000' }} />} /* 黑色图标 */
                placeholder="用户名"
                style={{
                  height: '40px',
                  border: '1px solid #000000', /* 黑色边框 */
                  borderRadius: '0', /* 无圆角 */
                  background: '#ffffff', /* 白色背景 */
                  color: '#000000' /* 黑色文字 */
                }}
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
              style={{ marginBottom: '24px' }}
            >
              <Input.Password
                prefix={<LockOutlined style={{ color: '#000000' }} />} /* 黑色图标 */
                placeholder="密码"
                style={{
                  height: '40px',
                  border: '1px solid #000000', /* 黑色边框 */
                  borderRadius: '0', /* 无圆角 */
                  background: '#ffffff', /* 白色背景 */
                  color: '#000000' /* 黑色文字 */
                }}
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: '16px' }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                disabled={!apiStatus.online && !apiStatus.checking}
                block
                style={{
                  height: '40px',
                  fontSize: '16px',
                  fontWeight: 400, /* 减小字重 */
                  backgroundColor: '#000000', /* 纯黑色 */
                  borderColor: '#000000', /* 黑色边框 */
                  borderRadius: '0', /* 无圆角 */
                  color: '#ffffff' /* 白色文字 */
                }}
              >
                {loading ? '登录中...' : '登录'}
              </Button>
            </Form.Item>
          </Form>

          <div style={{ 
            textAlign: 'center',
            borderTop: '1px solid #000000', /* 黑色边框 */
            paddingTop: '16px',
            marginTop: '16px'
          }}>
            <Text style={{ color: '#000000', fontSize: '14px' }}>
              还没有账号？{' '}
              <Link 
                to="/register" 
                style={{ 
                  color: '#000000', /* 黑色链接 */
                  textDecoration: 'none',
                  fontWeight: 400 /* 减小字重 */
                }}
              >
                立即注册
              </Link>
            </Text>
          </div>
        </Card>
    </div>
  );
};

export default Login;