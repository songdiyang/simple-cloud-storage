/**
 * 移动端工具函数
 */

// 检测是否为移动设备
export const isMobileDevice = () => {
  return window.innerWidth <= 768;
};

// 检测是否为触摸设备
export const isTouchDevice = () => {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
};

// 检测是否为iOS设备
export const isIOSDevice = () => {
  return /iPad|iPhone|iPod/.test(navigator.userAgent);
};

// 检测是否为Android设备
export const isAndroidDevice = () => {
  return /Android/.test(navigator.userAgent);
};

// 获取响应式断点
export const breakpoints = {
  xs: 480,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1600,
};

// 获取当前断点
export const getCurrentBreakpoint = () => {
  const width = window.innerWidth;
  if (width < breakpoints.xs) return 'xs';
  if (width < breakpoints.sm) return 'sm';
  if (width < breakpoints.md) return 'md';
  if (width < breakpoints.lg) return 'lg';
  if (width < breakpoints.xl) return 'xl';
  return 'xxl';
};

// 格式化文件大小为移动端友好格式
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const value = bytes / Math.pow(k, i);
  
  // 移动端使用更简洁的格式
  if (isMobileDevice()) {
    return `${value.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
  }
  
  return `${value.toFixed(2)} ${sizes[i]}`;
};

// 格式化日期为移动端友好格式
export const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (isMobileDevice()) {
    if (diffDays === 0) {
      return '今天';
    } else if (diffDays === 1) {
      return date > now ? '明天' : '昨天';
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else if (diffDays < 30) {
      return `${Math.floor(diffDays / 7)}周前`;
    } else if (diffDays < 365) {
      return `${Math.floor(diffDays / 30)}个月前`;
    } else {
      return `${Math.floor(diffDays / 365)}年前`;
    }
  }
  
  return date.toLocaleString('zh-CN');
};

// 防抖函数
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// 节流函数
export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// 移动端手势支持
export const addSwipeGesture = (element, onSwipeLeft, onSwipeRight) => {
  let touchStartX = 0;
  let touchEndX = 0;
  
  const handleTouchStart = (e) => {
    touchStartX = e.changedTouches[0].screenX;
  };
  
  const handleTouchEnd = (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  };
  
  const handleSwipe = () => {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        onSwipeLeft && onSwipeLeft();
      } else {
        onSwipeRight && onSwipeRight();
      }
    }
  };
  
  element.addEventListener('touchstart', handleTouchStart);
  element.addEventListener('touchend', handleTouchEnd);
  
  // 返回清理函数
  return () => {
    element.removeEventListener('touchstart', handleTouchStart);
    element.removeEventListener('touchend', handleTouchEnd);
  };
};

// 移动端优化配置
export const mobileConfig = {
  // 表格配置
  table: {
    size: 'small',
    scroll: { x: true },
    pagination: { simple: true, showSizeChanger: false },
  },
  
  // 按钮配置
  button: {
    size: 'middle',
    style: { height: 44, borderRadius: 8 }, // iOS推荐最小触摸目标44px
  },
  
  // 输入框配置
  input: {
    size: 'middle',
    style: { height: 44, fontSize: 16 }, // 防止iOS缩放
  },
  
  // 卡片配置
  card: {
    size: 'small',
    style: { margin: '0 8px', borderRadius: 12 },
  },
  
  // 模态框配置
  modal: {
    centered: true,
    width: '95%',
    style: { maxWidth: 400 },
  },
};