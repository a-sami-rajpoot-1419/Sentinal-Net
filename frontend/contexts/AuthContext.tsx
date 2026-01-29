/**
 * Authentication Context
 * Manages global authentication state including user, tokens, and auth operations
 */

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import axios, { AxiosInstance } from 'axios';

// Types
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: 'user' | 'admin' | 'moderator';
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;

  // Auth operations
  signUp: (email: string, password: string, full_name?: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  updateProfile: (full_name: string, avatar_url?: string) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize API client
  const apiClient = useCallback((): AxiosInstance => {
    const client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000'),
    });

    // Add token to requests
    client.interceptors.request.use((config) => {
      const storedTokens = localStorage.getItem('auth_tokens');
      if (storedTokens) {
        const parsedTokens = JSON.parse(storedTokens);
        config.headers.Authorization = `Bearer ${parsedTokens.access_token}`;
      }
      return config;
    });

    // Handle token expiration
    client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Try to refresh token
            const storedTokens = localStorage.getItem('auth_tokens');
            if (storedTokens) {
              const parsedTokens = JSON.parse(storedTokens);
              const response = await axios.post(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/refresh`,
                {},
                {
                  headers: {
                    Authorization: `Bearer ${parsedTokens.access_token}`,
                  },
                }
              );

              const newTokens = {
                access_token: response.data.access_token,
                refresh_token: response.data.refresh_token,
                token_type: response.data.token_type,
                expires_in: response.data.expires_in,
              };

              localStorage.setItem('auth_tokens', JSON.stringify(newTokens));
              setTokens(newTokens);

              // Retry original request
              originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
              return client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            handleLogout();
          }
        }

        return Promise.reject(error);
      }
    );

    return client;
  }, []);

  // Load auth state from storage on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedTokens = localStorage.getItem('auth_tokens');
        const storedUser = localStorage.getItem('auth_user');

        if (storedTokens && storedUser) {
          setTokens(JSON.parse(storedTokens));
          setUser(JSON.parse(storedUser));

          // Verify token is still valid
          try {
            const client = apiClient();
            const response = await client.get('/auth/me');
            setUser(response.data);
          } catch (err) {
            // Token invalid, clear storage
            localStorage.removeItem('auth_tokens');
            localStorage.removeItem('auth_user');
            setTokens(null);
            setUser(null);
          }
        }
      } catch (err) {
        console.error('Error initializing auth:', err);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [apiClient]);

  // Sign up
  const signUp = useCallback(async (email: string, password: string, full_name?: string) => {
    setLoading(true);
    setError(null);
    try {
      const client = apiClient();
      const response = await client.post('/auth/register', {
        email,
        password,
        full_name,
      });

      const newTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      };

      localStorage.setItem('auth_tokens', JSON.stringify(newTokens));
      localStorage.setItem('auth_user', JSON.stringify(response.data.user));

      setTokens(newTokens);
      setUser(response.data.user);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Sign up failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  // Sign in
  const signIn = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const client = apiClient();
      const response = await client.post('/auth/login', {
        email,
        password,
      });

      const newTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      };

      localStorage.setItem('auth_tokens', JSON.stringify(newTokens));
      localStorage.setItem('auth_user', JSON.stringify(response.data.user));

      setTokens(newTokens);
      setUser(response.data.user);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Sign in failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  // Sign out
  const handleLogout = useCallback(async () => {
    try {
      const client = apiClient();
      await client.post('/auth/logout');
    } catch (err) {
      console.error('Error during logout:', err);
    } finally {
      localStorage.removeItem('auth_tokens');
      localStorage.removeItem('auth_user');
      setTokens(null);
      setUser(null);
      setError(null);
    }
  }, [apiClient]);

  const signOut = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await handleLogout();
    } catch (err: any) {
      setError(err.message || 'Logout failed');
    } finally {
      setLoading(false);
    }
  }, [handleLogout]);

  // Update profile
  const updateProfile = useCallback(async (full_name: string, avatar_url?: string) => {
    setLoading(true);
    setError(null);
    try {
      const client = apiClient();
      const response = await client.put('/auth/profile', {
        full_name,
        avatar_url,
      });

      localStorage.setItem('auth_user', JSON.stringify(response.data));
      setUser(response.data);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Profile update failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  // Reset password
  const resetPassword = useCallback(async (email: string) => {
    setLoading(true);
    setError(null);
    try {
      const client = apiClient();
      await client.post('/auth/password-reset', {
        email,
      });
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Password reset request failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  // Refresh token
  const refreshToken = useCallback(async () => {
    try {
      const client = apiClient();
      const response = await client.post('/auth/refresh', {});

      const newTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      };

      localStorage.setItem('auth_tokens', JSON.stringify(newTokens));
      localStorage.setItem('auth_user', JSON.stringify(response.data.user));

      setTokens(newTokens);
      setUser(response.data.user);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Token refresh failed';
      setError(message);
      throw new Error(message);
    }
  }, [apiClient]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextType = {
    user,
    tokens,
    loading,
    error,
    isAuthenticated: !!user && !!tokens,
    signUp,
    signIn,
    signOut,
    updateProfile,
    resetPassword,
    refreshToken,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
