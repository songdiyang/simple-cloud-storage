import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, CloudOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

const Register = () => {
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    const result = await register(values);
    setLoading(false);
    
    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px',
      background: '#ffffff' /* 纯白背景 */
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: '400px',
          padding: '20px',
          background: '#ffffff', /* 纯白背景 */
          border: '1px solid #000000', /* 黑色边框 */
          borderRadius: '0' /* 无圆角 */
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: '#000000', /* 纯黑色 */
            borderRadius: '0', /* 无圆角 - 方形 */
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff', /* 白色文字 */
            fontSize: '36px',
            fontWeight: 'normal', /* 减小字重 */
            margin: '0 auto 16px'
          }}>
            <CloudOutlined />
          </div>
          <Title level={2} style={{ color: '#000000', margin: 0, fontWeight: 'normal' }}>
            创建账号
          </Title>
          <Text type="secondary" style={{ color: '#000000' }}>
            开始您的云存储之旅
          </Text>
        </div>

        <Form
          name="register"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
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
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input
              prefix={<MailOutlined style={{ color: '#000000' }} />} /* 黑色图标 */
              placeholder="邮箱"
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
            rules={[
              { required: true, message: '请输入密码' },
              { min: 8, message: '密码至少8个字符' }
            ]}
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

          <Form.Item
            name="password_confirm"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#000000' }} />} /* 黑色图标 */
              placeholder="确认密码"
              style={{
                height: '40px',
                border: '1px solid #000000', /* 黑色边框 */
                borderRadius: '0', /* 无圆角 */
                background: '#ffffff', /* 白色背景 */
                color: '#000000' /* 黑色文字 */
              }}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{
                height: '48px',
                fontSize: '16px',
                fontWeight: 'normal', /* 减小字重 */
                backgroundColor: '#000000', /* 纯黑色 */
                borderColor: '#000000', /* 黑色边框 */
                color: '#ffffff', /* 白色文字 */
                borderRadius: '0' /* 无圆角 */
              }}
            >
              注册
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ color: '#000000' }}>
              已有账号？{' '}
              <Link to="/login" style={{ color: '#000000', fontWeight: 'normal' }}>
                立即登录
              </Link>
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Register;