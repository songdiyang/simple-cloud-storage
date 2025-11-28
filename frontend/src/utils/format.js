
/**
 * 格式化字节数为可读格式
 */
export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

/**
 * 格式化日期时间
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * 获取文件图标
 */
export const getFileIcon = (fileName, fileType) => {
  const extension = (fileType || fileName?.split('.').pop()?.toLowerCase()) || '';
  
  const iconMap = {
    // 图片
    'jpg': 'FileImageOutlined',
    'jpeg': 'FileImageOutlined',
    'png': 'FileImageOutlined',
    'gif': 'FileImageOutlined',
    'bmp': 'FileImageOutlined',
    'svg': 'FileImageOutlined',
    
    // 文档
    'pdf': 'FilePdfOutlined',
    'doc': 'FileWordOutlined',
    'docx': 'FileWordOutlined',
    'xls': 'FileExcelOutlined',
    'xlsx': 'FileExcelOutlined',
    'ppt': 'FilePptOutlined',
    'pptx': 'FilePptOutlined',
    'txt': 'FileTextOutlined',
    'md': 'FileMarkdownOutlined',
    
    // 视频
    'mp4': 'VideoCameraOutlined',
    'avi': 'VideoCameraOutlined',
    'mov': 'VideoCameraOutlined',
    'wmv': 'VideoCameraOutlined',
    'flv': 'VideoCameraOutlined',
    'mkv': 'VideoCameraOutlined',
    
    // 音频
    'mp3': 'AudioOutlined',
    'wav': 'AudioOutlined',
    'flac': 'AudioOutlined',
    'aac': 'AudioOutlined',
    
    // 压缩文件
    'zip': 'FileZipOutlined',
    'rar': 'FileZipOutlined',
    '7z': 'FileZipOutlined',
    'tar': 'FileZipOutlined',
    'gz': 'FileZipOutlined',
    
    // 代码
    'js': 'CodeOutlined',
    'jsx': 'CodeOutlined',
    'ts': 'CodeOutlined',
    'tsx': 'CodeOutlined',
    'html': 'CodeOutlined',
    'css': 'CodeOutlined',
    'json': 'CodeOutlined',
    'xml': 'CodeOutlined',
    'py': 'CodeOutlined',
    'java': 'CodeOutlined',
    'cpp': 'CodeOutlined',
    'c': 'CodeOutlined',
  };
  
  return iconMap[extension] || 'FileOutlined';
};