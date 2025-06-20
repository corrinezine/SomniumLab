"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/components/auth/AuthProvider"
import { TimerStatsModal } from "@/components/TimerStatsModal"
import { toast } from "sonner"

interface TimerSession {
  id: string
  timer_type_id: number
  started_at: string
  completed_at?: string
  planned_duration: number
  actual_duration?: number
}

interface TimerType {
  id: number
  name: string
  description: string
}

export default function TestTimerLogsPage() {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [showStatsModal, setShowStatsModal] = useState(false)
  const [currentSession, setCurrentSession] = useState<TimerSession | null>(null)
  const [timerTypes, setTimerTypes] = useState<TimerType[]>([])
  const [testResults, setTestResults] = useState<string[]>([])

  // 获取计时器类型列表
  useEffect(() => {
    fetchTimerTypes()
  }, [])

  const fetchTimerTypes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/timer/types')
      if (response.ok) {
        const result = await response.json()
        if (result.success && Array.isArray(result.data)) {
          setTimerTypes(result.data)
          addTestResult(`✅ 成功获取计时器类型: ${result.data.map((t: TimerType) => t.name).join(', ')}`)
        } else {
          addTestResult(`❌ 获取计时器类型失败: 数据格式错误`)
        }
      } else {
        addTestResult(`❌ 获取计时器类型失败: ${response.status}`)
      }
    } catch (error) {
      addTestResult(`❌ 获取计时器类型错误: ${error}`)
    }
  }

  const addTestResult = (result: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`])
  }

  const clearTestResults = () => {
    setTestResults([])
  }

  // 开始计时器会话
  const startTimerSession = async (timerTypeId: number, duration: number = 15) => {
    if (!user) {
      toast.error("请先登录")
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/timer/start?user_id=${user.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          timer_type_id: timerTypeId,
          planned_duration: duration * 60 // 转换为秒
        })
      })

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          const session = result.data
          setCurrentSession({
            id: session.session_id,
            timer_type_id: session.timer_type_id,
            started_at: session.started_at,
            planned_duration: session.planned_duration,
            actual_duration: undefined,
            completed_at: undefined
          })
          addTestResult(`✅ 成功开始计时器会话 (类型: ${timerTypeId}, 时长: ${duration}分钟)`)
          addTestResult(`   会话ID: ${session.session_id}`)
          toast.success("计时器会话已开始")
        } else {
          addTestResult(`❌ 开始计时器失败: ${result.message || '未知错误'}`)
          toast.error("开始计时器失败")
        }
      } else {
        const error = await response.text()
        addTestResult(`❌ 开始计时器失败: ${response.status} - ${error}`)
        toast.error("开始计时器失败")
      }
    } catch (error) {
      addTestResult(`❌ 开始计时器错误: ${error}`)
      toast.error("网络错误")
    } finally {
      setIsLoading(false)
    }
  }

  // 完成计时器会话
  const completeTimerSession = async () => {
    if (!currentSession) {
      toast.error("没有正在进行的会话")
      return
    }

    if (!user) {
      toast.error("请先登录")
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/timer/complete?user_id=${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: currentSession.id
        })
      })

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          const completedSession = result.data
          addTestResult(`✅ 成功完成计时器会话`)
          addTestResult(`   实际时长: ${Math.round((completedSession.actual_duration || 0) / 60)}分钟`)
          setCurrentSession(null)
          toast.success("计时器会话已完成")
        } else {
          addTestResult(`❌ 完成计时器失败: ${result.message || '未知错误'}`)
          toast.error("完成计时器失败")
        }
      } else {
        const error = await response.text()
        addTestResult(`❌ 完成计时器失败: ${response.status} - ${error}`)
        toast.error("完成计时器失败")
      }
    } catch (error) {
      addTestResult(`❌ 完成计时器错误: ${error}`)
      toast.error("网络错误")
    } finally {
      setIsLoading(false)
    }
  }

  // 获取当前会话
  const getCurrentSession = async () => {
    if (!user) {
      toast.error("请先登录")
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/timer/current/${user.id}`)
      
      if (response.ok) {
        const session = await response.json()
        if (session) {
          setCurrentSession(session)
          addTestResult(`✅ 找到当前会话: ${session.id}`)
        } else {
          setCurrentSession(null)
          addTestResult(`ℹ️ 当前没有进行中的会话`)
        }
      } else {
        addTestResult(`❌ 获取当前会话失败: ${response.status}`)
      }
    } catch (error) {
      addTestResult(`❌ 获取当前会话错误: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }

  // 测试统计API
  const testStatsAPI = async () => {
    if (!user) {
      toast.error("请先登录")
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/user/timer-stats/${user.id}`)
      
      if (response.ok) {
        const result = await response.json()
        if (result.success && result.data) {
          addTestResult(`✅ 成功获取统计数据:`)
          result.data.forEach((stat: any) => {
            const timerName = stat.timer_type?.display_name || stat.timer_type?.name || '未知类型'
            const usageCount = stat.usage_count || 0
            const completedCount = stat.completed_count || 0
            const totalMinutes = Math.round((stat.total_duration || 0) / 60)
            addTestResult(`   ${timerName}: 使用${usageCount}次, 完成${completedCount}次, 总时长${totalMinutes}分钟`)
          })
          toast.success("统计数据获取成功")
        } else {
          addTestResult(`❌ 获取统计数据失败: ${result.message || '数据格式错误'}`)
          toast.error("获取统计数据失败")
        }
      } else {
        addTestResult(`❌ 获取统计数据失败: ${response.status}`)
        toast.error("获取统计数据失败")
      }
    } catch (error) {
      addTestResult(`❌ 获取统计数据错误: ${error}`)
      toast.error("网络错误")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* 页面标题 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-center">
              🧪 计时器日志测试中心
            </CardTitle>
            <CardDescription className="text-center">
              快速测试计时器功能和日志记录系统
            </CardDescription>
          </CardHeader>
        </Card>

        {/* 用户信息 */}
        <Card>
          <CardHeader>
            <CardTitle>用户信息</CardTitle>
          </CardHeader>
          <CardContent>
            {user ? (
              <div className="space-y-2">
                <p><strong>用户ID:</strong> {user.id}</p>
                <p><strong>邮箱:</strong> {user.email}</p>
                <p><strong>用户名:</strong> {user.user_metadata?.username || '未设置'}</p>
              </div>
            ) : (
              <p className="text-red-500">❌ 未登录，请先登录后再测试</p>
            )}
          </CardContent>
        </Card>

        {/* 快速测试按钮 */}
        <Card>
          <CardHeader>
            <CardTitle>快速测试</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <Button 
                onClick={() => startTimerSession(1, 1)} 
                disabled={isLoading || !user}
                variant="outline"
              >
                开始聚焦计时 (1分钟)
              </Button>
              
              <Button 
                onClick={() => startTimerSession(2, 1)} 
                disabled={isLoading || !user}
                variant="outline"
              >
                开始播种计时 (1分钟)
              </Button>
              
              <Button 
                onClick={() => startTimerSession(3, 1)} 
                disabled={isLoading || !user}
                variant="outline"
              >
                开始篝火计时 (1分钟)
              </Button>
              
              <Button 
                onClick={completeTimerSession} 
                disabled={isLoading || !currentSession}
                variant="default"
              >
                完成当前会话
              </Button>
              
              <Button 
                onClick={getCurrentSession} 
                disabled={isLoading || !user}
                variant="secondary"
              >
                检查当前会话
              </Button>
              
              <Button 
                onClick={testStatsAPI} 
                disabled={isLoading || !user}
                variant="secondary"
              >
                测试统计API
              </Button>
            </div>

            <div className="flex gap-4">
              <Button 
                onClick={() => setShowStatsModal(true)} 
                disabled={!user}
                className="flex-1"
              >
                📊 打开统计弹窗
              </Button>
              
              <Button 
                onClick={clearTestResults} 
                variant="outline"
                className="flex-1"
              >
                清空测试日志
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 当前会话状态 */}
        {currentSession && (
          <Card>
            <CardHeader>
              <CardTitle>当前会话</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p><strong>会话ID:</strong> {currentSession.id}</p>
                <p><strong>计时器类型:</strong> {currentSession.timer_type_id}</p>
                <p><strong>开始时间:</strong> {new Date(currentSession.started_at).toLocaleString()}</p>
                <p><strong>计划时长:</strong> {Math.round(currentSession.planned_duration / 60)}分钟</p>
                {currentSession.completed_at && (
                  <>
                    <p><strong>完成时间:</strong> {new Date(currentSession.completed_at).toLocaleString()}</p>
                    <p><strong>实际时长:</strong> {Math.round((currentSession.actual_duration || 0) / 60)}分钟</p>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 测试结果日志 */}
        <Card>
          <CardHeader>
            <CardTitle>测试日志</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
              {testResults.length === 0 ? (
                <p className="text-gray-500">暂无测试日志</p>
              ) : (
                <div className="space-y-1 font-mono text-sm">
                  {testResults.map((result, index) => (
                    <div key={index} className="whitespace-pre-wrap">
                      {result}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 使用说明 */}
        <Card>
          <CardHeader>
            <CardTitle>使用说明</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p>• <strong>开始计时:</strong> 点击对应的计时器类型按钮开始1分钟的测试会话</p>
              <p>• <strong>完成会话:</strong> 点击"完成当前会话"按钮来结束正在进行的会话</p>
              <p>• <strong>检查会话:</strong> 查看是否有正在进行的会话</p>
              <p>• <strong>测试统计:</strong> 直接调用统计API查看数据</p>
              <p>• <strong>统计弹窗:</strong> 测试前端统计弹窗组件</p>
              <p>• <strong>测试流程:</strong> 开始会话 → 等待或立即完成 → 查看统计 → 重复测试</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 统计弹窗 */}
      {showStatsModal && (
        <TimerStatsModal
          isOpen={showStatsModal}
          onClose={() => setShowStatsModal(false)}
        />
      )}
    </div>
  )
} 