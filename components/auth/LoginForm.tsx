"use client"

/**
 * AURA STUDIO - 登录表单组件
 * 
 * 提供用户登录和注册功能的表单界面
 * 
 * 作者：AI 编程导师
 */

import React, { useState } from 'react'
import { useAuth } from './AuthProvider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Mail, Lock, Eye, EyeOff } from 'lucide-react'

interface LoginFormProps {
  onSuccess?: () => void
  defaultMode?: 'login' | 'register'
}

export function LoginForm({ onSuccess, defaultMode = 'login' }: LoginFormProps) {
  // 🔄 状态管理
  const [mode, setMode] = useState<'login' | 'register'>(defaultMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // 🎯 获取认证方法
  const { signIn, signUp, loading } = useAuth()

  // 📝 表单验证
  const validateForm = (): boolean => {
    setError('')

    if (!email || !password) {
      setError('请填写所有必填字段')
      return false
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('请输入有效的邮箱地址')
      return false
    }

    if (password.length < 6) {
      setError('密码至少需要6个字符')
      return false
    }

    if (mode === 'register' && password !== confirmPassword) {
      setError('两次输入的密码不一致')
      return false
    }

    return true
  }

  // 🔐 处理登录
  const handleLogin = async () => {
    if (!validateForm()) return

    setIsSubmitting(true)
    setError('')

    try {
      const result = await signIn(email, password)

      if (result.success) {
        setSuccess('登录成功！正在跳转...')
        onSuccess?.()
      } else {
        setError(result.error || '登录失败')
      }
    } catch (error) {
      setError('登录过程中发生错误')
      console.error('Login error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  // 📝 处理注册
  const handleRegister = async () => {
    if (!validateForm()) return

    setIsSubmitting(true)
    setError('')

    try {
      const result = await signUp(email, password)

      if (result.success) {
        if (result.needsEmailConfirmation) {
          setSuccess('注册成功！请检查您的邮箱并点击确认链接')
        } else {
          setSuccess('注册成功！正在跳转...')
          onSuccess?.()
        }
      } else {
        setError(result.error || '注册失败')
      }
    } catch (error) {
      setError('注册过程中发生错误')
      console.error('Register error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  // 📋 处理表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (mode === 'login') {
      await handleLogin()
    } else {
      await handleRegister()
    }
  }

  // 🔄 切换模式
  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login')
    setError('')
    setSuccess('')
    setConfirmPassword('')
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 📧 邮箱输入 */}
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium text-gray-700">
            邮箱地址
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              id="email"
              type="email"
              placeholder="输入您的邮箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-10"
              disabled={loading || isSubmitting}
              required
            />
          </div>
        </div>

        {/* 🔒 密码输入 */}
        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium text-gray-700">
            密码
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="输入您的密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="pl-10 pr-10"
              disabled={loading || isSubmitting}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
              disabled={loading || isSubmitting}
            >
              {showPassword ? <EyeOff /> : <Eye />}
            </button>
          </div>
        </div>

        {/* 🔒 确认密码输入（仅注册时显示） */}
        {mode === 'register' && (
          <div className="space-y-2">
            <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
              确认密码
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="confirmPassword"
                type="password"
                placeholder="再次输入密码"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="pl-10"
                disabled={loading || isSubmitting}
                required
              />
            </div>
          </div>
        )}

        {/* ⚠️ 错误信息 */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* ✅ 成功信息 */}
        {success && (
          <Alert className="border-green-200 bg-green-50 text-green-800">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {/* 🔘 提交按钮 */}
        <Button
          type="submit"
          className="w-full"
          disabled={loading || isSubmitting}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {mode === 'login' ? '登录中...' : '注册中...'}
            </>
          ) : (
            mode === 'login' ? '登录' : '注册'
          )}
        </Button>
      </form>

      {/* 🔄 切换模式 */}
      <div className="text-center">
        <p className="text-sm text-gray-600">
          {mode === 'login' ? '还没有账户？' : '已有账户？'}
        </p>
        <button
          type="button"
          onClick={toggleMode}
          className="text-blue-600 hover:text-blue-700 font-medium text-sm mt-1"
          disabled={loading || isSubmitting}
        >
          {mode === 'login' ? '立即注册' : '返回登录'}
        </button>
      </div>
    </div>
  )
} 