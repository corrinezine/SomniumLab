"use client"

/**
 * AURA STUDIO - Supabase 认证提供者
 * 
 * 这个组件提供了完整的前端认证功能：
 * - 用户注册、登录、登出
 * - JWT Token 管理
 * - 认证状态管理
 * - 自动 Token 刷新
 * 
 * 作者：AI 编程导师
 * 设计理念：React Context + Supabase Auth
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { createClient, SupabaseClient, User, Session, AuthError, AuthChangeEvent } from '@supabase/supabase-js'

// 🔧 Supabase 配置
// 这些配置从环境变量中获取，确保安全性
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('缺少 Supabase 环境变量配置')
}

// 创建 Supabase 客户端
const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 🔄 同步用户到后端
const syncUserToBackend = async (user: User): Promise<void> => {
  try {
    console.log('🔄 正在同步用户到后端:', user.email)
    
    const response = await fetch('http://localhost:8000/api/auth/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        auth_user_id: user.id,
        email: user.email,
        username: user.user_metadata?.username || user.email?.split('@')[0]
      })
    })

    if (response.ok) {
      const result = await response.json()
      console.log('✅ 用户同步成功:', result.message)
    } else {
      console.warn('⚠️ 用户同步失败，但不影响认证流程')
    }
  } catch (error) {
    console.warn('⚠️ 用户同步请求失败:', error)
  }
}

// 📋 认证状态接口定义
interface AuthState {
  user: User | null                    // 当前用户信息
  session: Session | null              // 当前会话信息
  loading: boolean                     // 加载状态
  token: string | null                 // JWT Token
}

// 📋 认证操作接口定义
interface AuthActions {
  signUp: (email: string, password: string) => Promise<AuthResult>
  signIn: (email: string, password: string) => Promise<AuthResult>
  signOut: () => Promise<void>
  refreshToken: () => Promise<void>
}

// 📋 认证结果接口
interface AuthResult {
  success: boolean
  error?: string
  user?: User
  needsEmailConfirmation?: boolean
}

// 📋 认证上下文类型
type AuthContextType = AuthState & AuthActions

// 🎯 创建认证上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// 🎯 认证提供者组件
interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  // 🔄 状态管理
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState<string | null>(null)

  // 🚀 初始化认证状态
  useEffect(() => {
    // 获取初始会话
    const initializeAuth = async () => {
      try {
        console.log('🔍 正在初始化认证状态...')
        
        // 从 Supabase 获取当前会话
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('❌ 获取会话失败:', error.message)
        } else if (session) {
          console.log('✅ 发现现有会话，用户:', session.user.email)
          // 更新状态
          setSession(session)
          setUser(session.user)
          setToken(session.access_token)
          
          // 保存 Token 到本地存储（可选）
          localStorage.setItem('supabase_token', session.access_token)
          
          // 同步用户到后端（确保数据一致性）
          syncUserToBackend(session.user).catch(error => {
            console.warn('⚠️ 初始化时同步用户失败:', error)
          })
        } else {
          console.log('ℹ️ 未发现现有会话')
        }
      } catch (error) {
        console.error('❌ 初始化认证状态时发生错误:', error)
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  // 🎧 监听认证状态变化
  useEffect(() => {
    console.log('🎧 设置认证状态监听器...')
    
    // Supabase 认证状态变化监听器
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        console.log(`🔄 认证状态变化: ${event}`)
        
        switch (event) {
          case 'SIGNED_IN':
            console.log('✅ 用户已登录:', session?.user.email)
            setSession(session)
            setUser(session?.user ?? null)
            setToken(session?.access_token ?? null)
            
            // 保存 Token 到本地存储
            if (session?.access_token) {
              localStorage.setItem('supabase_token', session.access_token)
            }
            
            // 同步用户到后端
            if (session?.user) {
              syncUserToBackend(session.user).catch(error => {
                console.warn('⚠️ 自动同步用户失败:', error)
              })
            }
            break
            
          case 'SIGNED_OUT':
            console.log('👋 用户已登出')
            setSession(null)
            setUser(null)
            setToken(null)
            
            // 清除本地存储
            localStorage.removeItem('supabase_token')
            break
            
          case 'TOKEN_REFRESHED':
            console.log('🔄 Token 已刷新')
            setSession(session)
            setToken(session?.access_token ?? null)
            
            // 更新本地存储
            if (session?.access_token) {
              localStorage.setItem('supabase_token', session.access_token)
            }
            break
            
          case 'PASSWORD_RECOVERY':
            console.log('🔑 密码重置流程')
            break
        }
        
        setLoading(false)
      }
    )

    // 清理监听器
    return () => {
      console.log('🧹 清理认证状态监听器')
      subscription.unsubscribe()
    }
  }, [])

  // 📝 用户注册
  const signUp = async (email: string, password: string): Promise<AuthResult> => {
    try {
      console.log('📝 正在注册用户:', email)
      setLoading(true)

      // 输入验证
      if (!email || !password) {
        return {
          success: false,
          error: '请填写邮箱和密码'
        }
      }

      if (password.length < 6) {
        return {
          success: false,
          error: '密码至少需要6个字符'
        }
      }

      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          // 可以添加额外的用户元数据
          data: {
            app_name: 'AURA STUDIO'
          }
        }
      })

      if (error) {
        console.error('❌ 注册失败:', error.message, error)
        
        // 特殊处理频率限制错误
        if (error.message.includes('rate limit') || error.message.includes('Too many') || error.status === 429) {
          return {
            success: false,
            error: '注册请求过于频繁，请等待60秒后再试。如果多次尝试失败，建议稍后再来。'
          }
        }
        
        return {
          success: false,
          error: getErrorMessage(error)
        }
      }

      if (data.user && !data.session) {
        // 需要邮箱确认，但可以先同步用户信息
        console.log('📧 需要邮箱确认')
        
        // 即使没有会话，也尝试同步用户（为后续登录做准备）
        syncUserToBackend(data.user).catch(error => {
          console.warn('⚠️ 注册后同步用户失败:', error)
        })
        
        return {
          success: true,
          user: data.user,
          needsEmailConfirmation: true
        }
      }

      console.log('✅ 注册成功:', data.user?.email)
      
      // 如果有会话（即时登录），同步用户信息
      if (data.user && data.session) {
        syncUserToBackend(data.user).catch(error => {
          console.warn('⚠️ 注册后同步用户失败:', error)
        })
      }
      
      return {
        success: true,
        user: data.user ?? undefined
      }

    } catch (error: any) {
      console.error('❌ 注册过程中发生错误:', error)
      
      // 处理网络错误或其他异常
      if (error?.status === 429) {
        return {
          success: false,
          error: '请求过于频繁，请等待一分钟后再试'
        }
      }
      
      return {
        success: false,
        error: error?.message || '注册过程中发生未知错误'
      }
    } finally {
      setLoading(false)
    }
  }

  // 🔐 用户登录
  const signIn = async (email: string, password: string): Promise<AuthResult> => {
    try {
      console.log('🔐 正在登录用户:', email)
      setLoading(true)

      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        console.error('❌ 登录失败:', error.message)
        return {
          success: false,
          error: getErrorMessage(error)
        }
      }

      console.log('✅ 登录成功:', data.user.email)
      return {
        success: true,
        user: data.user
      }

    } catch (error) {
      console.error('❌ 登录过程中发生错误:', error)
      return {
        success: false,
        error: '登录过程中发生未知错误'
      }
    } finally {
      setLoading(false)
    }
  }

  // 👋 用户登出
  const signOut = async (): Promise<void> => {
    try {
      console.log('👋 正在登出用户...')
      setLoading(true)

      const { error } = await supabase.auth.signOut()

      if (error) {
        console.error('❌ 登出失败:', error.message)
        throw new Error(getErrorMessage(error))
      }

      console.log('✅ 登出成功')

    } catch (error) {
      console.error('❌ 登出过程中发生错误:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 🔄 刷新 Token
  const refreshToken = async (): Promise<void> => {
    try {
      console.log('🔄 正在刷新 Token...')
      
      const { data, error } = await supabase.auth.refreshSession()

      if (error) {
        console.error('❌ 刷新 Token 失败:', error.message)
        throw new Error(getErrorMessage(error))
      }

      console.log('✅ Token 刷新成功')

    } catch (error) {
      console.error('❌ 刷新 Token 过程中发生错误:', error)
      throw error
    }
  }

  // 🎯 上下文值
  const value: AuthContextType = {
    // 状态
    user,
    session,
    loading,
    token,
    // 操作
    signUp,
    signIn,
    signOut,
    refreshToken
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// 🎯 使用认证上下文的 Hook
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  
  if (context === undefined) {
    throw new Error('useAuth 必须在 AuthProvider 内部使用')
  }
  
  return context
}

// 🎯 受保护路由组件
interface ProtectedRouteProps {
  children: ReactNode
  fallback?: ReactNode
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { user, loading } = useAuth()

  // 加载中显示加载状态
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">正在验证身份...</p>
        </div>
      </div>
    )
  }

  // 未登录显示回退内容或登录提示
  if (!user) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">需要登录</h2>
          <p className="text-gray-600">请先登录后再访问此页面</p>
        </div>
      </div>
    )
  }

  // 已登录显示受保护内容
  return <>{children}</>
}

// 🛠️ 工具函数：错误消息处理
function getErrorMessage(error: AuthError): string {
  // 将 Supabase 错误消息转换为用户友好的中文消息
  const message = error.message || error.toString()
  
  // 处理常见错误
  switch (message) {
    case 'Invalid login credentials':
      return '邮箱或密码错误'
    case 'Email not confirmed':
      return '请先确认您的邮箱'
    case 'User already registered':
      return '该邮箱已被注册'
    case 'Password should be at least 6 characters':
      return '密码至少需要6个字符'
    case 'Signup requires a valid email':
      return '请输入有效的邮箱地址'
    case 'Too many requests':
      return '请求过于频繁，请稍后再试'
    default:
      // 处理频率限制相关错误
      if (message.includes('rate limit') || message.includes('Too many') || message.includes('429')) {
        return '注册请求过于频繁，请等待60秒后再试'
      }
      if (message.includes('security purposes')) {
        return '安全限制：请等待片刻后再尝试注册'
      }
      if (message.includes('For security purposes')) {
        return '安全验证中，请稍等片刻后重试'
      }
      return message || '发生未知错误'
  }
}

// 🎯 导出 Supabase 客户端（供其他组件使用）
export { supabase } 