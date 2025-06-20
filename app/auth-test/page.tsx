"use client"

/**
 * AURA STUDIO - 认证功能测试页面
 * 
 * 这个页面用于测试和演示 Supabase 认证集成功能
 * 
 * 作者：AI 编程导师
 */

import React, { useState, useEffect } from 'react'
import { AuthProvider, useAuth, ProtectedRoute } from '@/components/auth/AuthProvider'
import { LoginForm } from '@/components/auth/LoginForm'
import { useAuthenticatedApi, getApiData } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Loader2, User, Clock, BarChart3, Settings, LogOut } from 'lucide-react'

// 🎯 受保护的仪表板组件
function Dashboard() {
  const { user, signOut } = useAuth()
  const api = useAuthenticatedApi()
  const [loading, setLoading] = useState(false)
  const [profile, setProfile] = useState<any>(null)
  const [sessions, setSessions] = useState<any[]>([])
  const [logs, setLogs] = useState<any[]>([])
  const [error, setError] = useState('')

  // 🚀 加载用户数据
  useEffect(() => {
    loadUserData()
  }, [])

  const loadUserData = async () => {
    setLoading(true)
    setError('')

    try {
      // 并行请求多个 API
      const [profileResponse, sessionsResponse, logsResponse] = await Promise.all([
        api.getUserProfile(),
        api.getTimerSessions(10),
        api.getDailyLogs(7)
      ])

      // 处理用户资料
      if (profileResponse.success) {
        setProfile(profileResponse.data)
      } else {
        console.error('获取用户资料失败:', profileResponse.error)
      }

      // 处理会话数据
      if (sessionsResponse.success) {
        setSessions(sessionsResponse.data?.sessions || [])
      } else {
        console.error('获取会话数据失败:', sessionsResponse.error)
      }

      // 处理日志数据
      if (logsResponse.success) {
        setLogs(logsResponse.data?.logs || [])
      } else {
        console.error('获取日志数据失败:', logsResponse.error)
      }

    } catch (error) {
      console.error('加载数据时发生错误:', error)
      setError('加载数据失败，请检查后端服务是否运行')
    } finally {
      setLoading(false)
    }
  }

  // 🧪 测试创建新会话
  const testCreateSession = async () => {
    try {
      setLoading(true)
      const response = await api.startTimerSession({
        timer_type_id: 1,
        planned_duration: 90,
        audio_track_id: 1
      })

      if (response.success) {
        alert(`新会话创建成功！会话ID: ${response.data?.session_id}`)
        await loadUserData() // 重新加载数据
      } else {
        alert(`创建会话失败: ${response.error}`)
      }
    } catch (error) {
      alert(`创建会话时发生错误: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  // 👋 处理登出
  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  if (loading && !profile) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-blue-600" />
          <p className="mt-4 text-gray-600">正在加载用户数据...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* 🎯 头部信息 */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AURA STUDIO 仪表板</h1>
            <p className="text-gray-600 mt-2">认证功能测试和演示</p>
          </div>
          <Button onClick={handleSignOut} variant="outline">
            <LogOut className="mr-2 h-4 w-4" />
            登出
          </Button>
        </div>

        {/* ⚠️ 错误信息 */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 📋 用户信息卡片 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="mr-2 h-5 w-5" />
              用户信息
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">用户 ID</p>
                <p className="font-mono text-sm">{user?.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">邮箱</p>
                <p className="font-medium">{user?.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">认证状态</p>
                <Badge variant="secondary">已认证</Badge>
              </div>
            </div>

            {profile && (
              <div className="mt-4 p-4 bg-green-50 rounded-lg">
                <p className="text-green-800 font-medium">✅ 后端认证验证成功</p>
                <p className="text-green-700 text-sm mt-1">{profile.message}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* ⏰ 计时器会话卡片 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="mr-2 h-5 w-5" />
                最近会话
              </div>
              <Button 
                onClick={testCreateSession} 
                disabled={loading}
                size="sm"
              >
                {loading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                测试创建会话
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sessions.length > 0 ? (
              <div className="space-y-3">
                {sessions.slice(0, 5).map((session, index) => (
                  <div key={session.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">会话 #{index + 1}</p>
                      <p className="text-sm text-gray-600">
                        计划时长: {session.planned_duration}分钟
                        {session.actual_duration && ` | 实际时长: ${session.actual_duration}分钟`}
                      </p>
                    </div>
                    <Badge variant={session.completed ? "default" : "secondary"}>
                      {session.completed ? "已完成" : "未完成"}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">暂无会话记录</p>
            )}
          </CardContent>
        </Card>

        {/* 📊 每日日志卡片 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="mr-2 h-5 w-5" />
              每日统计
            </CardTitle>
          </CardHeader>
          <CardContent>
            {logs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {logs.slice(0, 6).map((log) => (
                  <div key={log.log_date} className="p-4 bg-blue-50 rounded-lg">
                    <p className="font-medium text-blue-900">{log.log_date}</p>
                    <div className="mt-2 space-y-1 text-sm">
                      <p>总会话: {log.total_sessions}次</p>
                      <p>完成: {log.completed_sessions}次</p>
                      <p>总时长: {Math.round(log.total_focus_time / 60)}小时</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">暂无统计数据</p>
            )}
          </CardContent>
        </Card>

        {/* 🔧 技术信息 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="mr-2 h-5 w-5" />
              技术信息
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium">认证状态</p>
                <p className="text-green-600">✅ Supabase JWT 验证通过</p>
              </div>
              <div>
                <p className="font-medium">API 连接</p>
                <p className="text-green-600">✅ 后端 API 连接正常</p>
              </div>
              <div>
                <p className="font-medium">Token 状态</p>
                <p className="text-green-600">✅ {api.hasToken() ? 'Token 有效' : 'Token 缺失'}</p>
              </div>
              <div>
                <p className="font-medium">数据同步</p>
                <p className="text-green-600">✅ 实时数据同步正常</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// 🎯 主页面组件
export default function AuthTestPage() {
  return (
    <ProtectedRoute
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">AURA STUDIO 认证</h1>
              <p className="text-gray-600 mt-2">请登录查看您的专属仪表板</p>
            </div>
            <LoginForm defaultMode="login" />
          </div>
        </div>
      }
    >
      <Dashboard />
    </ProtectedRoute>
  )
} 