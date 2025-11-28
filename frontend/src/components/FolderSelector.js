import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Tree, 
  Button, 
  message, 
  Spin,
  Typography,
  Space
} from 'antd';
import { 
  FolderOutlined, 
  FileOutlined,
  InboxOutlined
} from '@ant-design/icons';
import api from '../services/api';

const { Title } = Typography;

const FolderSelector = ({ 
  visible, 
  onCancel, 
  onConfirm, 
  loading = false 
}) => {
  const [treeData, setTreeData] = useState([]);
  const [selectedKeys, setSelectedKeys] = useState([]);
  const [loadingTree, setLoadingTree] = useState(false);

  useEffect(() => {
    if (visible) {
      fetchFolders();
    }
  }, [visible]);

  const fetchFolders = async () => {
    try {
      setLoadingTree(true);
      const response = await api.get('/api/files/folders/');
      
      const folders = response.data;
      const treeData = buildTreeData(folders);
      
      setTreeData([
        {
          title: '根目录',
          key: 'root',
          icon: <InboxOutlined />,
          children: treeData
        }
      ]);
    } catch (error) {
      message.error('获取文件夹列表失败');
    } finally {
      setLoadingTree(false);
    }
  };

  const buildTreeData = (folders, parentId = null) => {
    return folders
      .filter(folder => folder.parent === parentId)
      .map(folder => ({
        title: folder.name,
        key: folder.id,
        icon: <FolderOutlined />,
        children: buildTreeData(folders, folder.id)
      }));
  };

  const handleSelect = (selectedKeys) => {
    setSelectedKeys(selectedKeys);
  };

  const handleConfirm = () => {
    const selectedKey = selectedKeys[0];
    const folderId = selectedKey === 'root' ? null : selectedKey;
    onConfirm(folderId);
  };

  return (
    <Modal
      title={
        <Space>
          <FolderOutlined />
          选择保存位置
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button 
          key="confirm" 
          type="primary" 
          onClick={handleConfirm}
          loading={loading}
        >
          确认保存
        </Button>
      ]}
      width={600}
    >
      <Spin spinning={loadingTree}>
        <div style={{ minHeight: 300, maxHeight: 400, overflow: 'auto' }}>
          {treeData.length > 0 ? (
            <Tree
              showIcon
              defaultExpandAll
              onSelect={handleSelect}
              selectedKeys={selectedKeys}
              treeData={treeData}
            />
          ) : (
            <div style={{ textAlign: 'center', padding: '50px 0' }}>
              <FolderOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
              <div style={{ marginTop: 16, color: '#999' }}>
                暂无文件夹，将保存到根目录
              </div>
            </div>
          )}
        </div>
      </Spin>
    </Modal>
  );
};

export default FolderSelector;