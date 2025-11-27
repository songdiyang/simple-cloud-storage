import React, { useState } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  Avatar, 
  Upload, 
  message,
  Typography,
  Row,
  Col,
  Space,
  Progress
} from 'antd';
import { 
  UserOutlined, 
  UploadOutlined, 
  SaveOutlined 
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useQuery } from 'react-query';
import api from '../services/api';

const { Title, Text } = Typography;

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const { data: storageInfo } = useQuery('storage-info', () =>
    api.get('/api/files/storage/').then(res => res.data)
  );

  React.useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
      });
    }
  }, [user, form]);

  const handleUpdateProfile = async (values) => {
    setLoading(true);
    const result = await updateProfile(values);
    setLoading(false);
    
    if (result.success) {
      message.success('个人资料更新成功！');
    }
  };

  const handleAvatarUpload = async (file) => {
    const formData = new FormData();
    formData.append('avatar', file);

    try {
      setLoading(true);
      // 为FormData请求移除Content-Type，让浏览器自动设置multipart/form-data
      const response = await api.post('/api/auth/upload-avatar/', formData, {
        headers: {
          'Content-Type': undefined,
        },
      });
      
      message.success('头像上传成功！');
      // 更新用户信息
      if (response.data.user) {
        // 这里需要触发用户信息更新
        window.location.reload(); // 简单的刷新方式
      }
    } catch (error) {
      message.error(error.response?.data?.error || '头像上传失败！');
    } finally {
      setLoading(false);
    }
    
    return false; // 阻止默认上传行为
  };

  const handleDeleteAvatar = async () => {
    try {
      setLoading(true);
      await api.delete('/api/auth/delete-avatar/');
      message.success('头像删除成功！');
      window.location.reload();
    } catch (error) {
      message.error(error.response?.data?.error || '头像删除失败！');
    } finally {
      setLoading(false);
    }
  };

  const uploadProps = {
    name: 'avatar',
    beforeUpload: (file) => {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        message.error('只支持 JPG、PNG、GIF、WebP 格式的图片！');
        return false;
      }
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('图片大小不能超过 2MB！');
        return false;
      }
      handleAvatarUpload(file);
      return false;
    },
    showUploadList: false,
  };

  return (
    <div>
      <Title level={2} style={{ color: '#333', marginBottom: '24px' }}>
        个人设置
      </Title>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={8}>
          <Card className="cel-card" title="个人信息">
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <Avatar
                size={120}
                src={user?.avatar ? `http://localhost:8000${user.avatar}` : undefined}
                icon={<UserOutlined />}
                style={{ marginBottom: '16px' }}
              />
              <div>
                <Space>
                  <Upload {...uploadProps}>
                    <Button 
                      icon={<UploadOutlined />} 
                      size="small"
                      className="cel-button"
                      loading={loading}
                    >
                      更换头像
                    </Button>
                  </Upload>
                  {user?.avatar && (
                    <Button 
                      size="small"
                      onClick={handleDeleteAvatar}
                      loading={loading}
                    >
                      删除头像
                    </Button>
                  )}
                </Space>
              </div>
            </div>

            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text type="secondary">用户名</Text>
                <div style={{ fontWeight: 'bold' }}>{user?.username}</div>
              </div>
              <div>
                <Text type="secondary">注册时间</Text>
                <div>{user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : '-'}</div>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card className="cel-card" title="编辑资料">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleUpdateProfile}
            >
              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="first_name"
                    label="名字"
                  >
                    <Input placeholder="请输入名字" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="last_name"
                    label="姓氏"
                  >
                    <Input placeholder="请输入姓氏" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="email"
                label="邮箱地址"
                rules={[
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input placeholder="请输入邮箱地址" />
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit"
                  loading={loading}
                  icon={<SaveOutlined />}
                  className="cel-button"
                >
                  保存更改
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: '24px' }}>
        <Col span={24}>
          <Card className="cel-card" title="存储信息">
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={8}>
                <div style={{ textAlign: 'center' }}>
                  <Title level={3} style={{ color: '#667eea', margin: 0 }}>
                    {storageInfo?.storage_quota_display || '0 B'}
                  </Title>
                  <Text type="secondary">存储配额</Text>
                </div>
              </Col>
              <Col xs={24} sm={8}>
                <div style={{ textAlign: 'center' }}>
                  <Title level={3} style={{ color: '#ff6b6b', margin: 0 }}>
                    {storageInfo?.used_storage_display || '0 B'}
                  </Title>
                  <Text type="secondary">已使用</Text>
                </div>
              </Col>
              <Col xs={24} sm={8}>
                <div style={{ textAlign: 'center' }}>
                  <Title level={3} style={{ color: '#43e97b', margin: 0 }}>
                    {storageInfo?.available_storage_display || '0 B'}
                  </Title>
                  <Text type="secondary">可用空间</Text>
                </div>
              </Col>
            </Row>

            <div style={{ marginTop: '24px' }}>
              <Text strong>存储使用率</Text>
              <Progress
                percent={storageInfo?.storage_usage_percentage || 0}
                strokeColor={{
                  '0%': '#667eea',
                  '100%': '#764ba2',
                }}
                format={(percent) => `${percent?.toFixed(1)}%`}
              />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Profile;