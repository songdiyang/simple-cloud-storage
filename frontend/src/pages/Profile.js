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
  Progress,
  Modal,
  Tag,
  Result,
  Divider
} from 'antd';
import { 
  UserOutlined, 
  UploadOutlined, 
  SaveOutlined,
  CrownOutlined,
  GiftOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  EditOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useQuery } from 'react-query';
import api from '../services/api';

const { Title, Text } = Typography;

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  
  // VIP 相关状态
  const [showVipModal, setShowVipModal] = useState(false);
  const [vipStep, setVipStep] = useState('info'); // 'info' | 'form' | 'success'
  const [orderNumber, setOrderNumber] = useState('');
  const [applyLoading, setApplyLoading] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false); // 显示拒绝原因弹窗
  const [rejectDismissed, setRejectDismissed] = useState(false); // 用户已查看并关闭拒绝信息
  
  // 修改用户名相关状态
  const [showUsernameModal, setShowUsernameModal] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [usernameLoading, setUsernameLoading] = useState(false);

  const { data: storageInfo } = useQuery('storage-info', () =>
    api.get('/api/files/storage/').then(res => res.data)
  );
  
  // 获取 VIP 状态
  const { data: vipStatus, refetch: refetchVipStatus } = useQuery('vip-status', () =>
    api.get('/api/auth/vip/status/').then(res => res.data)
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
  
  // 修改用户名
  const handleChangeUsername = async () => {
    if (!newUsername.trim()) {
      message.error('请输入新用户名');
      return;
    }
    
    try {
      setUsernameLoading(true);
      const response = await api.put('/api/auth/change-username/', { 
        username: newUsername.trim() 
      });
      message.success('用户名修改成功');
      setShowUsernameModal(false);
      setNewUsername('');
      // 刷新页面以更新用户信息
      window.location.reload();
    } catch (error) {
      message.error(error.response?.data?.error || '修改失败');
    } finally {
      setUsernameLoading(false);
    }
  };

  // VIP 申请提交
  const handleVipApply = async () => {
    if (!orderNumber.trim()) {
      message.error('请输入赞助单号');
      return;
    }
    
    try {
      setApplyLoading(true);
      await api.post('/api/auth/vip/apply/', { order_number: orderNumber });
      setVipStep('success');
      refetchVipStatus();
    } catch (error) {
      message.error(error.response?.data?.error || '申请提交失败');
    } finally {
      setApplyLoading(false);
    }
  };
  
  // 关闭 VIP 弹窗
  const handleCloseVipModal = () => {
    setShowVipModal(false);
    setVipStep('info');
    setOrderNumber('');
  };
  
  // VIP 弹窗内容
  const renderVipModalContent = () => {
    if (vipStep === 'success') {
      return (
        <Result
          icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
          title="感谢您的支持！"
          subTitle="管理员审核后将为您扩容存储空间至 5GB"
          extra={
            <Button type="primary" onClick={handleCloseVipModal} className="cel-button">
              知道了
            </Button>
          }
        />
      );
    }
    
    if (vipStep === 'form') {
      return (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <GiftOutlined style={{ fontSize: 48, color: '#ffd700', marginBottom: 16 }} />
          <Title level={4}>输入赞助单号</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
            请输入您的赞助订单号，管理员将在审核后为您开通 VIP
          </Text>
          <Input
            placeholder="请输入赞助单号"
            value={orderNumber}
            onChange={(e) => setOrderNumber(e.target.value)}
            style={{ 
              maxWidth: 300, 
              marginBottom: 24,
              borderRadius: 8,
              border: '2px solid #667eea'
            }}
            size="large"
          />
          <div>
            <Space>
              <Button onClick={() => setVipStep('info')}>
                返回
              </Button>
              <Button 
                type="primary" 
                onClick={handleVipApply}
                loading={applyLoading}
                className="cel-button"
                style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
              >
                提交申请
              </Button>
            </Space>
          </div>
        </div>
      );
    }
    
    // 默认显示赞助信息
    return (
      <div style={{ textAlign: 'center' }}>
        {/* 赞助图片区域 - 赛璐璐风格边框 */}
        <div style={{
          border: '3px solid #333',
          borderRadius: 16,
          padding: 20,
          marginBottom: 24,
          background: 'linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%)',
          boxShadow: '4px 4px 0 #333'
        }}>
          <CrownOutlined style={{ fontSize: 64, color: '#ffd700', marginBottom: 16 }} />
          <Title level={3} style={{ margin: 0, color: '#333' }}>成为 VIP 用户</Title>
          <Divider />
          
          {/* 赞助图片占位符 */}
          <div style={{
            border: '2px dashed #999',
            borderRadius: 12,
            padding: 40,
            marginBottom: 20,
            background: '#f5f5f5'
          }}>
            <img 
              src="/sponsor.png" 
              alt="赞助二维码"
              style={{ maxWidth: '100%', maxHeight: 200 }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div style={{ display: 'none', color: '#999' }}>
              <GiftOutlined style={{ fontSize: 48, marginBottom: 8 }} />
              <div>赞助图片</div>
              <Text type="secondary" style={{ fontSize: 12 }}>
                请将图片放置在 frontend/public/sponsor.png
              </Text>
            </div>
          </div>
          
          <Space direction="vertical" size="small">
            <Text strong style={{ fontSize: 16 }}>✨ VIP 特权 ✨</Text>
            <Text>📦 存储空间从 200MB 扩容至 <Text strong style={{ color: '#667eea' }}>5GB</Text></Text>
            <Text>🚀 尊享 VIP 专属标识</Text>
          </Space>
        </div>
        
        <Button 
          type="primary" 
          size="large"
          icon={<CrownOutlined />}
          onClick={() => setVipStep('form')}
          className="cel-button"
          style={{ 
            background: 'linear-gradient(135deg, #ffd700 0%, #ffb700 100%)',
            border: '2px solid #333',
            color: '#333',
            fontWeight: 'bold',
            boxShadow: '3px 3px 0 #333'
          }}
        >
          我已赞助，填写单号
        </Button>
      </div>
    );
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
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontWeight: 'bold' }}>{user?.username}</span>
                  <Button 
                    type="link" 
                    size="small" 
                    icon={<EditOutlined />}
                    onClick={() => {
                      setNewUsername(user?.username || '');
                      setShowUsernameModal(true);
                    }}
                    style={{ padding: 0, height: 'auto' }}
                  >
                    修改
                  </Button>
                </div>
              </div>
              <div>
                <Text type="secondary">用户等级</Text>
                <div>
                  {vipStatus?.is_vip ? (
                    <Tag color="gold" icon={<CrownOutlined />} style={{ 
                      border: '2px solid #333',
                      fontWeight: 'bold'
                    }}>
                      VIP用户
                    </Tag>
                  ) : (
                    <Space>
                      <Tag color="default">普通用户</Tag>
                      {/* VIP申请状态 */}
                      {vipStatus?.has_pending_application ? (
                        <Tag color="processing">审核中</Tag>
                      ) : (vipStatus?.has_rejected_application && !rejectDismissed) ? (
                        <Tag 
                          color="error" 
                          icon={<CloseCircleOutlined />}
                          style={{ cursor: 'pointer' }}
                          onClick={() => setShowRejectModal(true)}
                        >
                          审核失败
                        </Tag>
                      ) : (
                        <Button 
                          type="link" 
                          size="small"
                          icon={<CrownOutlined />}
                          onClick={() => setShowVipModal(true)}
                          style={{ color: '#ffd700', padding: 0 }}
                        >
                          升级VIP
                        </Button>
                      )}
                    </Space>
                  )}
                </div>
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
            
            {/* VIP 升级入口 */}
            {!vipStatus?.is_vip && (
              <div style={{ 
                marginTop: 24, 
                padding: 16, 
                background: 'linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%)',
                borderRadius: 12,
                border: '2px solid #ffd700',
                textAlign: 'center'
              }}>
                <CrownOutlined style={{ fontSize: 24, color: '#ffd700', marginBottom: 8 }} />
                <div>
                  <Text strong>升级 VIP 获取 5GB 存储空间</Text>
                </div>
                {vipStatus?.has_pending_application ? (
                  <Tag color="processing" style={{ marginTop: 12 }}>申请审核中，请耐心等待</Tag>
                ) : (vipStatus?.has_rejected_application && !rejectDismissed) ? (
                  <Space direction="vertical" style={{ marginTop: 12 }}>
                    <Tag color="error" icon={<CloseCircleOutlined />}>
                      上次申请未通过
                    </Tag>
                    <Button 
                      type="primary"
                      icon={<CrownOutlined />}
                      onClick={() => setShowVipModal(true)}
                      style={{ 
                        background: 'linear-gradient(135deg, #ffd700 0%, #ffb700 100%)',
                        border: '2px solid #333',
                        color: '#333',
                        fontWeight: 'bold'
                      }}
                    >
                      重新申请
                    </Button>
                  </Space>
                ) : (
                  <Button 
                    type="primary"
                    icon={<CrownOutlined />}
                    onClick={() => setShowVipModal(true)}
                    style={{ 
                      marginTop: 12,
                      background: 'linear-gradient(135deg, #ffd700 0%, #ffb700 100%)',
                      border: '2px solid #333',
                      color: '#333',
                      fontWeight: 'bold'
                    }}
                  >
                    成为 VIP
                  </Button>
                )}
              </div>
            )}
          </Card>
        </Col>
      </Row>
      
      {/* VIP 申请弹窗 */}
      <Modal
        title={
          <Space>
            <CrownOutlined style={{ color: '#ffd700' }} />
            <span>成为 VIP 用户</span>
          </Space>
        }
        open={showVipModal}
        onCancel={handleCloseVipModal}
        footer={null}
        width={500}
        centered
        className="cel-modal"
      >
        {renderVipModalContent()}
      </Modal>
      
      {/* 审核失败原因弹窗 */}
      <Modal
        title={
          <Space>
            <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
            <span>VIP 申请审核未通过</span>
          </Space>
        }
        open={showRejectModal}
        onCancel={() => {
          setShowRejectModal(false);
          setRejectDismissed(true);
        }}
        footer={
          <Space>
            <Button onClick={() => {
              setShowRejectModal(false);
              setRejectDismissed(true);
            }}>
              关闭
            </Button>
            <Button 
              type="primary" 
              icon={<CrownOutlined />}
              onClick={() => {
                setShowRejectModal(false);
                setRejectDismissed(true);
                setShowVipModal(true);
              }}
              style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
            >
              重新申请
            </Button>
          </Space>
        }
        centered
        className="cel-modal"
      >
        <div style={{ 
          padding: '20px',
          background: '#fff2f0',
          borderRadius: 12,
          border: '2px solid #ffccc7'
        }}>
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">申请单号：</Text>
            <Text strong style={{ marginLeft: 8 }}>
              {vipStatus?.rejected_application?.order_number}
            </Text>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">申请时间：</Text>
            <Text style={{ marginLeft: 8 }}>
              {vipStatus?.rejected_application?.created_at 
                ? new Date(vipStatus.rejected_application.created_at).toLocaleString()
                : '-'
              }
            </Text>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">审核时间：</Text>
            <Text style={{ marginLeft: 8 }}>
              {vipStatus?.rejected_application?.reviewed_at 
                ? new Date(vipStatus.rejected_application.reviewed_at).toLocaleString()
                : '-'
              }
            </Text>
          </div>
          <Divider style={{ margin: '12px 0' }} />
          <div>
            <Text type="secondary">拒绝原因：</Text>
            <div style={{ 
              marginTop: 8,
              padding: 12,
              background: '#fff',
              borderRadius: 8,
              border: '1px solid #ffccc7'
            }}>
              <Text type="danger" strong>
                {vipStatus?.rejected_application?.reject_reason || '未说明原因'}
              </Text>
            </div>
          </div>
        </div>
      </Modal>
      
      {/* 修改用户名弹窗 */}
      <Modal
        title={
          <Space>
            <EditOutlined style={{ color: '#667eea' }} />
            <span>修改用户名</span>
          </Space>
        }
        open={showUsernameModal}
        onCancel={() => {
          setShowUsernameModal(false);
          setNewUsername('');
        }}
        footer={
          <Space>
            <Button onClick={() => {
              setShowUsernameModal(false);
              setNewUsername('');
            }}>
              取消
            </Button>
            <Button 
              type="primary" 
              loading={usernameLoading}
              onClick={handleChangeUsername}
              className="cel-button"
            >
              确认修改
            </Button>
          </Space>
        }
        centered
        className="cel-modal"
      >
        <div style={{ padding: '20px 0' }}>
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">当前用户名：</Text>
            <Text strong style={{ marginLeft: 8 }}>{user?.username}</Text>
          </div>
          <div>
            <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
              新用户名：
            </Text>
            <Input
              placeholder="请输入新用户名"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              maxLength={30}
              showCount
              style={{ 
                borderRadius: 8,
                border: '2px solid #667eea'
              }}
              size="large"
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                用户名只能包含字母、数字、下划线或中文，长度 3-30 个字符
              </Text>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Profile;