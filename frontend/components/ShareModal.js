import React, { useState } from 'react';
import { Modal, Form, Input, DatePicker, InputNumber, message } from 'antd';
import { LockOutlined, ClockCircleOutlined, DownloadOutlined } from '@ant-design/icons';
import api from '../services/api';
import dayjs from 'dayjs';

const ShareModal = ({ visible, onCancel, onOk, fileId }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      
      // 格式化数据
      const shareData = {
        password: values.password || '',
        max_downloads: values.max_downloads || null,
        expire_at: values.expire_at ? values.expire_at.toISOString() : null
      };

      const response = await api.post(`/api/files/${fileId}/share/`, shareData);
      
      message.success('分享创建成功！');
      
      // 复制分享链接到剪贴板
      const shareUrl = `${window.location.origin}/share/${response.data.share_code}`;
      await navigator.clipboard.writeText(shareUrl);
      message.success('分享链接已复制到剪贴板！');
      
      form.resetFields();
      onOk && onOk(response.data);
      
    } catch (error) {
      if (error.response?.data?.error) {
        message.error(error.response.data.error);
      } else {
        message.error('分享创建失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel && onCancel();
  };

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <LockOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          创建文件分享
        </div>
      }
      open={visible}
      onCancel={handleCancel}
      onOk={handleSubmit}
      okText="创建分享"
      cancelText="取消"
      confirmLoading={loading}
      width={500}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          max_downloads: null,
          expire_at: null
        }}
      >
        <div style={{ 
          marginBottom: 16, 
          padding: 12, 
          backgroundColor: '#f6f8fa', 
          borderRadius: 6 
        }}>
          <div style={{ color: '#666', fontSize: '13px', lineHeight: '1.5' }}>
            创建分享后，任何人都可以通过链接访问此文件。您可以设置访问限制来保护文件安全。
          </div>
        </div>

        <Form.Item
          label={
            <span>
              <DownloadOutlined style={{ marginRight: 4 }} />
              最大下载次数
            </span>
          }
          name="max_downloads"
          help="不限制请留空"
        >
          <InputNumber
            placeholder="不限制"
            min={1}
            max={1000}
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Form.Item
          label={
            <span>
              <ClockCircleOutlined style={{ marginRight: 4 }} />
              过期时间
            </span>
          }
          name="expire_at"
          help="不限制请留空"
        >
          <DatePicker
            showTime
            placeholder="选择过期时间"
            style={{ width: '100%' }}
            disabledDate={(current) => current && current < dayjs().endOf('day')}
          />
        </Form.Item>

        <Form.Item
          label={
            <span>
              <LockOutlined style={{ marginRight: 4 }} />
              访问密码
            </span>
          }
          name="password"
          help="留空则无需密码"
        >
          <Input.Password
            placeholder="设置访问密码（可选）"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ShareModal;