import React, { createContext, useContext, useEffect, useState } from 'react';
import { message } from 'antd';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Token ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/api/auth/profile/');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await api.post('/api/auth/login/', credentials);
      const { token, user } = response.data;
      
      localStorage.setItem('token', token);
      api.defaults.headers.common['Authorization'] = `Token ${token}`;
      setUser(user);
      
      message.success('登录成功！');
      return { success: true };
    } catch (error) {
      let errorMessage = '登录失败，请稍后重试';
      
      if (error.response?.status === 400) {
        // Django REST Framework 返回的400错误通常包含详细的字段错误
        const errorData = error.response.data;
        if (errorData.non_field_errors) {
          errorMessage = errorData.non_field_errors[0];
        } else if (errorData.error) {
          errorMessage = errorData.error;
        } else {
          errorMessage = '用户名或密码错误，请检查后重试';
        }
      } else if (error.response?.status === 401) {
        errorMessage = '用户名或密码错误，请检查后重试';
      } else if (error.code === 'NETWORK_ERROR') {
        errorMessage = '网络连接失败，请检查网络后重试';
      }
      
      // 不在这里显示错误消息，让登录页面自己处理
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/api/auth/register/', userData);
      const { token, user } = response.data;
      
      localStorage.setItem('token', token);
      api.defaults.headers.common['Authorization'] = `Token ${token}`;
      setUser(user);
      
      message.success('注册成功！');
      return { success: true };
    } catch (error) {
      const errorData = error.response?.data;
      let errorMessage = '注册失败';
      
      if (errorData) {
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData.non_field_errors) {
          errorMessage = errorData.non_field_errors[0];
        } else if (errorData.username) {
          errorMessage = errorData.username[0];
        } else if (errorData.email) {
          errorMessage = errorData.email[0];
        }
      }
      
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      await api.post('/api/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
      message.success('已退出登录');
    }
  };

  const updateProfile = async (userData) => {
    try {
      const response = await api.put('/api/auth/profile/', userData);
      setUser(response.data);
      message.success('资料更新成功！');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || '更新失败';
      message.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    updateProfile,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};