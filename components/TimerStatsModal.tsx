"use client"

/**
 * AURA STUDIO - 计时器使用统计弹窗组件
 * 
 * 显示用户所有计时器类型的使用统计信息：
 * - 使用次数
 * - 总时长
 * - 完成次数
 * - 平均时长
 * 
 * 作者：AI 编程导师
 */

import React, { useEffect, useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Clock, Target, CheckCircle, TrendingUp, RefreshCw } from 'lucide-react'

// 📊 计时器统计数据类型
interface TimerStats {
  timer_type: {
    id: number
    name: string
    display_name: string
    description: string
    background_image: string
  }
  usage_count: number
  completed_count: number
  total_duration: number
  avg_duration: number
  total_duration_formatted: string
}

interface TimerStatsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function TimerStatsModal({ isOpen, onClose }: TimerStatsModalProps) {
  const { user } = useAuth()
  const [stats, setStats] = useState<TimerStats[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 🎯 加载用户计时器统计数据
  const loadTimerStats = async () => {
    if (!user?.id) {
      console.warn('🚫 [TimerStats] 无法加载统计数据：用户未登录')
      return
    }

    console.log('🔄 [TimerStats] 开始加载用户统计数据...', {
      userId: user.id,
      email: user.email,
      timestamp: new Date().toLocaleTimeString()
    })

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`http://localhost:8000/api/user/timer-stats/${user.id}`)
      const data = await response.json()

      if (data.success) {
        // 计算数据变化
        const previousStats = stats
        const newStats = data.data
        
        console.log('✅ [TimerStats] 统计数据加载成功！', {
          timestamp: new Date().toLocaleTimeString(),
          userId: user.id,
          dataCount: newStats.length
        })

        // 详细打印每个计时器类型的统计
        newStats.forEach((stat: any, index: number) => {
          const prevStat = previousStats[index]
          const isUpdated = prevStat && (
            prevStat.usage_count !== stat.usage_count ||
            prevStat.completed_count !== stat.completed_count ||
            prevStat.total_duration !== stat.total_duration
          )

          console.log(`📊 [TimerStats] ${stat.timer_type.display_name} 统计${isUpdated ? ' 🔄 已更新' : ''}:`, {
            使用次数: stat.usage_count + (prevStat ? ` (${prevStat.usage_count > stat.usage_count ? '-' : '+'}${Math.abs(stat.usage_count - prevStat.usage_count)})` : ''),
            完成次数: stat.completed_count + (prevStat ? ` (${prevStat.completed_count > stat.completed_count ? '-' : '+'}${Math.abs(stat.completed_count - prevStat.completed_count)})` : ''),
            总时长: stat.total_duration_formatted + (prevStat ? ` (${prevStat.total_duration > stat.total_duration ? '-' : '+'}${Math.abs(stat.total_duration - prevStat.total_duration)}秒)` : ''),
            完成率: `${stat.completion_rate}%`,
            平均时长: stat.avg_duration_formatted
          })
        })

        // 计算总体变化
        const totalSessions = newStats.reduce((sum: number, stat: any) => sum + stat.usage_count, 0)
        const totalCompleted = newStats.reduce((sum: number, stat: any) => sum + stat.completed_count, 0)
        const totalDuration = newStats.reduce((sum: number, stat: any) => sum + stat.total_duration, 0)
        
        const prevTotalSessions = previousStats.reduce((sum, stat) => sum + stat.usage_count, 0)
        const prevTotalCompleted = previousStats.reduce((sum, stat) => sum + stat.completed_count, 0)
        const prevTotalDuration = previousStats.reduce((sum, stat) => sum + stat.total_duration, 0)

        if (previousStats.length > 0) {
          console.log('📈 [TimerStats] 总体数据变化:', {
            总会话数: `${totalSessions} (${totalSessions > prevTotalSessions ? '+' : ''}${totalSessions - prevTotalSessions})`,
            完成会话: `${totalCompleted} (${totalCompleted > prevTotalCompleted ? '+' : ''}${totalCompleted - prevTotalCompleted})`,
            总时长变化: `${totalDuration - prevTotalDuration}秒`,
            整体完成率: `${totalCompleted > 0 ? Math.round((totalCompleted / totalSessions) * 100) : 0}%`
          })
        }

        setStats(newStats)
      } else {
        console.error('❌ [TimerStats] 获取统计数据失败:', data.message || '未知错误')
        setError('获取统计数据失败')
      }
    } catch (err) {
      console.error('❌ [TimerStats] 加载计时器统计网络错误:', err)
      setError('网络错误，请稍后重试')
    } finally {
      setLoading(false)
      console.log('🏁 [TimerStats] 统计数据加载完成')
    }
  }

  // 📈 当弹窗打开时加载数据
  useEffect(() => {
    if (isOpen && user) {
      loadTimerStats()
    }
  }, [isOpen, user])

  // 🔄 自动刷新机制：每30秒自动刷新一次数据（仅在弹窗打开时）
  useEffect(() => {
    if (!isOpen || !user) return

    const interval = setInterval(() => {
      loadTimerStats()
    }, 30000) // 30秒自动刷新

    return () => clearInterval(interval)
  }, [isOpen, user])

  // 🎨 格式化时长显示 - 精确到MM:SS
  const formatDuration = (seconds: number): string => {
    if (seconds === 0) return '00:00'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = seconds % 60
    
    if (hours > 0) {
      // 超过1小时显示为 H小时MM分
      return `${hours}小时${minutes.toString().padStart(2, '0')}分`
    } else if (minutes > 0) {
      // 1分钟到1小时显示为 MM:SS
      return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
    } else {
      // 小于1分钟显示为 0:SS
      return `0:${remainingSeconds.toString().padStart(2, '0')}`
    }
  }

  // ⏱️ 格式化时长显示（用于总时长概览）
  const formatDurationOverview = (seconds: number): string => {
    if (seconds === 0) return '0分钟'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (hours > 0) {
      return `${hours}小时${minutes}分钟`
    } else if (minutes > 0) {
      return `${minutes}分钟`
    } else {
      return '不到1分钟'
    }
  }

  // 📊 计算完成率
  const getCompletionRate = (completed: number, total: number): number => {
    if (total === 0) return 0
    return Math.round((completed / total) * 100)
  }

  // 🎯 获取统计图标
  const getTimerIcon = (timerName: string) => {
    switch (timerName) {
      case 'focus':
        return '🎯'
      case 'inspire':
        return '🌱'
      case 'talk':
        return '🔥'
      default:
        return '⏰'
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center text-xl">
              <TrendingUp className="mr-2 h-5 w-5" />
              我的计时器使用统计
            </DialogTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={loadTimerStats}
              disabled={loading}
              className="flex items-center gap-1"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              刷新
            </Button>
          </div>
          <DialogDescription>
            查看您在 AURA STUDIO 中各类计时器的使用情况 · 数据每30秒自动更新
          </DialogDescription>
        </DialogHeader>

        {/* 🔄 加载状态 */}
        {loading && (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">正在加载统计数据...</span>
          </div>
        )}

        {/* ⚠️ 错误信息 */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 📊 统计数据展示 */}
        {!loading && !error && stats.length > 0 && (
          <div className="space-y-4">
            {/* 📈 总体统计概览 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">总体概览</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {stats.reduce((sum, stat) => sum + stat.usage_count, 0)}
                    </div>
                    <div className="text-sm text-gray-600">总会话数</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {stats.reduce((sum, stat) => sum + stat.completed_count, 0)}
                    </div>
                    <div className="text-sm text-gray-600">完成会话</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {formatDurationOverview(stats.reduce((sum, stat) => sum + stat.total_duration, 0))}
                    </div>
                    <div className="text-sm text-gray-600">总专注时长</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {stats.reduce((sum, stat) => sum + stat.completed_count, 0) > 0
                        ? getCompletionRate(
                            stats.reduce((sum, stat) => sum + stat.completed_count, 0),
                            stats.reduce((sum, stat) => sum + stat.usage_count, 0)
                          )
                        : 0}%
                    </div>
                    <div className="text-sm text-gray-600">整体完成率</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 📋 各计时器类型详细统计 */}
            <div className="space-y-3">
              {stats.map((stat) => (
                <Card key={stat.timer_type.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      {/* 🎯 计时器基本信息 */}
                      <div className="flex items-center space-x-3">
                        <div className="text-3xl">
                          {getTimerIcon(stat.timer_type.name)}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">
                            {stat.timer_type.display_name}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {stat.timer_type.description}
                          </p>
                        </div>
                      </div>

                      {/* 📊 统计数据 */}
                      <div className="text-right">
                        <Badge
                          variant={stat.usage_count > 0 ? "default" : "secondary"}
                          className="mb-2"
                        >
                          {stat.usage_count > 0 ? '已使用' : '未使用'}
                        </Badge>
                      </div>
                    </div>

                    {/* 📈 详细数据展示 */}
                    {stat.usage_count > 0 && (
                      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        <div className="flex items-center">
                          <Target className="h-4 w-4 mr-1 text-blue-500" />
                          <div>
                            <div className="font-medium">{stat.usage_count}</div>
                            <div className="text-gray-600">使用次数</div>
                          </div>
                        </div>
                        
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-1 text-green-500" />
                          <div>
                            <div className="font-medium">{stat.completed_count}</div>
                            <div className="text-gray-600">完成次数</div>
                          </div>
                        </div>
                        
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1 text-purple-500" />
                          <div>
                            <div className="font-medium">{formatDuration(stat.total_duration)}</div>
                            <div className="text-gray-600">总时长</div>
                          </div>
                        </div>
                        
                        <div className="flex items-center">
                          <TrendingUp className="h-4 w-4 mr-1 text-orange-500" />
                          <div>
                            <div className="font-medium">
                              {getCompletionRate(stat.completed_count, stat.usage_count)}%
                            </div>
                            <div className="text-gray-600">完成率</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 🎯 未使用状态 */}
                    {stat.usage_count === 0 && (
                      <div className="mt-4 text-center text-gray-500">
                        <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">还没有使用过这种计时器</p>
                        <p className="text-xs">开始您的第一次专注时光吧！</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* 📭 无数据状态 */}
        {!loading && !error && stats.length === 0 && (
          <div className="text-center py-8">
            <Clock className="h-16 w-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">还没有使用记录</h3>
            <p className="text-gray-600">
              开始使用 AURA STUDIO 的计时器，记录您的专注时光吧！
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
} 