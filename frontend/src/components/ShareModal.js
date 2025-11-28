import React, { useState } from 'react';
import { 
  Modal, 
  Form, 
  Input, 
  DatePicker, 
  InputNumber, 
  Switch, 
  Button, 
  message, 
  Space,
  Typography,
  Divider,
  Alert
} from 'antd';
import { 
  ShareAltOutlined, 
  CopyOutlined, 
  LockOutlined,
  ClockCircleOutlined,
  NumberOutlined
} from '@ant-design/icons';
import api from '../services/api';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const ShareModal = ({ visible, onCancel, file, onSuccess }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [shareLink, setShareLink] = useState('');
  const [shareCreated, setShareCreated] = useState(false);

  const handleSubmit = async (values) => {
    try {
      setLoading(true);
      
      const shareData = {
        password: values.password || undefined,
        expire_at: values.expire_at ? values.expire_at.toISOString() : undefined,
        max_downloads: values.max_downloads || undefined
      };

      const response = await api.post(`/api/files/${file.id}/share/`, shareData);
      
      const fullShareLink = `${window.location.origin}/share/${response.data.share_code}`;
      setShareLink(fullShareLink);
      setShareCreated(true);
      
      message.success('分享创建成功！');
      onSuccess?.();
    } catch (error) {
      message.error(error.response?.data?.error || '创建分享失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareLink);
    message.success('链接已复制到剪贴板');
  };

  const handleCancel = () => {
    form.resetFields();
    setShareLink('');
    setShareCreated(false);
    onCancel();
  };

  const disabledDate = (current) => {
    return current && current < dayjs().startOf('day');
  };

  return (
    <Modal
      title={
        <Space>
          <ShareAltOutlined />
          创建文件分享
        </Space>
      }
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      {!shareCreated ? (
        <>
          <Alert
            message={`分享文件: ${file?.name}`}
            type="info"
            showIcon
            style={{ marginBottom: 20 }}
          />
          
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
          >
            <Form.Item
              name="password"
              label={
                <Space>
                  <LockOutlined />
                  访问密码（可选）
                </Space>
              }
              help="留空则无需密码即可访问"
            >
              <Input.Password placeholder="设置访问密码" />
            </Form.Item>

            <Divider />

            <Form.Item
              name="expire_at"
              label={
                <Space>
                  <ClockCircleOutlined />
                  过期时间（可选）
                </Space>
              }
              help="留空则永不过期"
            >
              <DatePicker
                showTime
                placeholder="选择过期时间"
                disabledDate={disabledDate}
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item
              name="max_downloads"
              label={
                <Space>
                  <NumberOutlined />
                  最大下载次数（可选）
                </Space>
              }
              help="留空则无限制"
            >
              <InputNumber
                placeholder="设置最大下载次数"
                min={1}
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Divider />

            <Form.Item>
              <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                <Button onClick={handleCancel}>
                  取消
                </Button>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  icon={<ShareAltOutlined />}
                >
                  创建分享
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <Title level={4}>
            <ShareAltOutlined /> 分享创建成功！
          </Title>
          
          <div style={{ 
            background: '#f5f5f5', 
            padding: 15, 
            borderRadius: 8, 
            margin: '20px 0',
            wordBreak: 'break-all'
          }}>
            <Text copyable={{ text: shareLink }}>
              {shareLink}
            </Text>
          </div>

          <Space>
            <Button 
              type="primary" 
              icon={<CopyOutlined />}
              onClick={handleCopyLink}
            >
              复制链接
            </Button>
            <Button onClick={handleCancel}>
              关闭
            </Button>
          </Space>

          <Alert
            message="分享提示"
            description="任何人都可以通过此链接访问文件，请谨慎分享。如需取消分享，请在'我的分享'页面中删除。"
            type="warning"
            showIcon
            style={{ marginTop: 20 }}
          />
        </div>
      )}
    </Modal>
  );
};

export default ShareModal;