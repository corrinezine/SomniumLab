"use client"

/**
 * AURA STUDIO - 全局认证头部组件
 * 
 * 这个组件显示在页面右上角，提供：
 * - 用户未登录时：注册/登录按钮
 * - 用户已登录时：用户信息和登出按钮
 * 
 * 作者：AI 编程导师
 */

import React, { useState } from 'react'
import { useAuth } from './AuthProvider'
import { LoginForm } from './LoginForm'
import { TimerStatsModal } from '@/components/TimerStatsModal'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { User, LogOut, Settings, UserCircle, LogIn, BarChart3 } from 'lucide-react'

export function AuthHeader() {
  const { user, signOut, loading } = useAuth()
  const [showAuthDialog, setShowAuthDialog] = useState(false)
  const [showStatsModal, setShowStatsModal] = useState(false)

  // 🚪 处理登出
  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  // 📱 处理认证对话框关闭
  const handleAuthSuccess = () => {
    setShowAuthDialog(false)
  }

  // 🎯 加载状态
  if (loading) {
    return (
      <div className="fixed top-4 right-4 z-50">
        <div className="animate-pulse">
          <div className="h-10 w-24 bg-white/20 rounded-full"></div>
        </div>
      </div>
    )
  }

  return (
    <>
      {/* 🎯 左上角日志按钮 - 仅在用户登录时显示 */}
      {user && (
        <div className="fixed top-4 left-4 z-50">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowStatsModal(true)}
            className="bg-white/10 border-white/20 text-white hover:bg-white/20 backdrop-blur-sm"
          >
            <BarChart3 className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">日志</span>
            <span className="sm:hidden">📊</span>
          </Button>
        </div>
      )}

      {/* 🎯 固定定位的认证区域 */}
      <div className="fixed top-4 right-4 z-50">
        {user ? (
          // ✅ 已登录状态
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="outline" 
                className="bg-white/10 border-white/20 text-white hover:bg-white/20 backdrop-blur-sm"
              >
                <Avatar className="h-6 w-6 mr-2">
                  <AvatarImage src={user.user_metadata?.avatar_url} />
                  <AvatarFallback className="bg-purple-600 text-white text-xs">
                    {user.email?.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden sm:inline-block">
                  {user.email?.split('@')[0]}
                </span>
                <UserCircle className="h-4 w-4 ml-1 sm:hidden" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              align="end" 
              className="w-56 bg-white/95 backdrop-blur-sm border-white/20"
            >
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {user.user_metadata?.full_name || '用户'}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user.email}
                  </p>
                  <Badge variant="secondary" className="w-fit mt-1">
                    已认证
                  </Badge>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={() => window.location.href = '/auth-test'}
                className="cursor-pointer"
              >
                <Settings className="mr-2 h-4 w-4" />
                <span>用户中心</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={handleSignOut}
                className="cursor-pointer text-red-600 focus:text-red-600"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>登出</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          // 🚪 未登录状态
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAuthDialog(true)}
              className="bg-white/10 border-white/20 text-white hover:bg-white/20 backdrop-blur-sm"
            >
              <LogIn className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">登录</span>
              <span className="sm:hidden">登录</span>
            </Button>
          </div>
        )}
      </div>

      {/* 🎯 认证对话框 */}
      <Dialog open={showAuthDialog} onOpenChange={setShowAuthDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <User className="mr-2 h-5 w-5" />
              欢迎来到 AURA STUDIO
            </DialogTitle>
            <DialogDescription>
              登录或注册以保存您的灵感工作记录
            </DialogDescription>
          </DialogHeader>
          <LoginForm onSuccess={handleAuthSuccess} />
        </DialogContent>
      </Dialog>

      {/* 📊 计时器统计弹窗 */}
      <TimerStatsModal
        isOpen={showStatsModal}
        onClose={() => setShowStatsModal(false)}
      />
    </>
  )
}

// 🎯 只在客户端显示的认证头部（避免SSR问题）
export function ClientAuthHeader() {
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return <AuthHeader />
} 