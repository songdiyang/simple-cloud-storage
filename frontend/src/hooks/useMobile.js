import { useState, useEffect } from 'react';
import { isMobileDevice, getCurrentBreakpoint, breakpoints } from '../utils/mobile';

/**
 * 移动端响应式 Hook
 */
export const useMobile = () => {
  const [isMobile, setIsMobile] = useState(isMobileDevice());
  const [breakpoint, setBreakpoint] = useState(getCurrentBreakpoint());
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setIsMobile(width <= breakpoints.md);
      setBreakpoint(getCurrentBreakpoint());
      setWindowSize({ width, height });
    };

    window.addEventListener('resize', handleResize);
    
    // 初始化
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return {
    isMobile,
    isTablet: breakpoint === 'sm' || breakpoint === 'md',
    isDesktop: breakpoint === 'lg' || breakpoint === 'xl' || breakpoint === 'xxl',
    breakpoint,
    windowSize,
    isSmallScreen: windowSize.width <= breakpoints.xs,
    isMediumScreen: windowSize.width > breakpoints.xs && windowSize.width <= breakpoints.md,
    isLargeScreen: windowSize.width > breakpoints.md,
  };
};

/**
 * 移动端手势 Hook
 */
export const useSwipeGesture = (onSwipeLeft, onSwipeRight) => {
  const [touchStart, setTouchStart] = useState({ x: 0, y: 0 });
  const [touchEnd, setTouchEnd] = useState({ x: 0, y: 0 });

  const minSwipeDistance = 50;

  const onTouchStart = (e) => {
    setTouchEnd({ x: 0, y: 0 });
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const onTouchMove = (e) => {
    setTouchEnd({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const onTouchEnd = () => {
    if (!touchStart.x || !touchEnd.x) return;

    const distance = touchStart.x - touchEnd.x;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && onSwipeLeft) {
      onSwipeLeft();
    }
    if (isRightSwipe && onSwipeRight) {
      onSwipeRight();
    }
  };

  return {
    onTouchStart,
    onTouchMove,
    onTouchEnd,
  };
};

/**
 * 移动端虚拟键盘 Hook
 */
export const useVirtualKeyboard = () => {
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  const [isKeyboardOpen, setIsKeyboardOpen] = useState(false);

  useEffect(() => {
    const initialViewportHeight = window.visualViewport?.height || window.innerHeight;

    const handleResize = () => {
      const currentHeight = window.visualViewport?.height || window.innerHeight;
      const heightDiff = initialViewportHeight - currentHeight;
      
      if (heightDiff > 150) { // 假设键盘高度至少150px
        setKeyboardHeight(heightDiff);
        setIsKeyboardOpen(true);
      } else {
        setKeyboardHeight(0);
        setIsKeyboardOpen(false);
      }
    };

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleResize);
    } else {
      // 降级方案
      window.addEventListener('resize', handleResize);
      window.addEventListener('orientationchange', handleResize);
    }

    return () => {
      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', handleResize);
      } else {
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('orientationchange', handleResize);
      }
    };
  }, []);

  return {
    keyboardHeight,
    isKeyboardOpen,
  };
};

/**
 * 移动端网络状态 Hook
 */
export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionType, setConnectionType] = useState('unknown');

  useEffect(() => {
    const updateOnlineStatus = () => setIsOnline(navigator.onLine);
    
    const updateConnectionType = () => {
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      if (connection) {
        setConnectionType(connection.effectiveType || 'unknown');
      }
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    updateConnectionType();

    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (connection) {
      connection.addEventListener('change', updateConnectionType);
    }

    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
      
      if (connection) {
        connection.removeEventListener('change', updateConnectionType);
      }
    };
  }, []);

  return {
    isOnline,
    connectionType,
    isSlowConnection: ['slow-2g', '2g'].includes(connectionType),
  };
};

/**
 * 移动端触摸反馈 Hook
 */
export const useTouchFeedback = () => {
  const [activeElement, setActiveElement] = useState(null);

  const handleTouchStart = (e) => {
    setActiveElement(e.currentTarget);
  };

  const handleTouchEnd = () => {
    setTimeout(() => setActiveElement(null), 150);
  };

  const getTouchStyle = (element) => ({
    opacity: activeElement === element ? 0.7 : 1,
    transform: activeElement === element ? 'scale(0.98)' : 'scale(1)',
    transition: 'all 0.1s ease',
  });

  return {
    handleTouchStart,
    handleTouchEnd,
    getTouchStyle,
    isActive: (element) => activeElement === element,
  };
};