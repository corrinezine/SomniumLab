"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { useAuth } from '@/components/auth/AuthProvider'

interface TimerSession {
  session_id: string  // 修正：API返回的是session_id，且是字符串
  timer_type_id: number
  planned_duration: number
  elapsed_time?: number
  started_at: string
}

export default function BreakPage() {
  const router = useRouter()
  const { user } = useAuth()
  
  // 计时器状态 - 90分钟倒计时
  const DEFAULT_TIME = 90 * 60 // 90分钟转换为秒
  const [timeLeft, setTimeLeft] = useState(DEFAULT_TIME)
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [completedBreaks, setCompletedBreaks] = useState(0)
  
  // 计时器会话状态
  const [currentSession, setCurrentSession] = useState<TimerSession | null>(null)
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null)

  // 音乐播放状态
  const [isPlaying, setIsPlaying] = useState(true) // 改为默认播放状态
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null)
  
  // 任务编辑状态
  const [taskTitle, setTaskTitle] = useState("放松身心，享受片刻宁静")
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTitle, setEditingTitle] = useState("")

  // 飘散文字动画状态
  const floatingText = "将一个想法带入现实，它可能看起来变小了似的，从无形到有形。"
  const [textCharacters, setTextCharacters] = useState<Array<{
    char: string
    id: number
    initialX: number
    initialY: number
    targetX: number
    targetY: number
  }>>([])
  const [animationFrame, setAnimationFrame] = useState(0)

  // 漂浮动画循环 - 只在计时器运行时
  useEffect(() => {
    if (!isRunning) return
    
    const animate = () => {
      setAnimationFrame(prev => prev + 1)
      if (isRunning) {
        requestAnimationFrame(animate)
      }
    }
    
    const id = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(id)
  }, [isRunning])

  // 初始化音频
  useEffect(() => {
    const audioElement = new Audio('/Miles Davis - Générique.mp3')
    audioElement.loop = true
    audioElement.volume = 0.3 // 设置音量为30%
    setAudio(audioElement)

    // 进入页面时自动播放音乐
    const playAudio = async () => {
      try {
        await audioElement.play()
        setIsPlaying(true)
      } catch (error) {
        console.log('自动播放被浏览器阻止，需要用户交互后播放:', error)
        setIsPlaying(false)
      }
    }
    playAudio()

    return () => {
      audioElement.pause()
      audioElement.src = ''
    }
  }, [])

    // 初始化文字字符位置
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    const centerX = window.innerWidth / 2
    // 新策略：基于header下方40px的固定定位，避免折行导致的重叠问题
    const centerY = 100 + 40 // header高度估算(100px) + 40px间距
    
    // 定义安全显示区域，避开UI元素
    const safeZones = [
      // 左上角区域 (避开logo)
      { x: 0, y: 0, width: window.innerWidth * 0.25, height: window.innerHeight * 0.3 },
      // 右上角区域 (避开音乐控制)
      { x: window.innerWidth * 0.75, y: 0, width: window.innerWidth * 0.25, height: window.innerHeight * 0.3 },
      // 左下角区域
      { x: 0, y: window.innerHeight * 0.7, width: window.innerWidth * 0.3, height: window.innerHeight * 0.3 },
      // 右下角区域
      { x: window.innerWidth * 0.7, y: window.innerHeight * 0.7, width: window.innerWidth * 0.3, height: window.innerHeight * 0.3 }
    ]
    
    const getRandomSafePosition = () => {
      const zone = safeZones[Math.floor(Math.random() * safeZones.length)]
      return {
        x: zone.x + Math.random() * zone.width,
        y: zone.y + Math.random() * zone.height
      }
    }
    
    const chars = floatingText.split('').map((char, index) => {
      // 计算最终文字的布局位置（在break.png上方）
      const charsPerLine = 18 // 每行大约18个字符
      const lineIndex = Math.floor(index / charsPerLine)
      const charInLine = index % charsPerLine
      
      const targetX = centerX - (charsPerLine * 12) / 2 + charInLine * 12 // 字符间距12px
      const targetY = centerY + lineIndex * 30 // 行间距30px
      
      const safePos = getRandomSafePosition()
      
      return {
        char,
        id: index,
        initialX: safePos.x,
        initialY: safePos.y,
        targetX: targetX,
        targetY: targetY
      }
    })
    setTextCharacters(chars)
  }, [])

  // 格式化时间显示为 MM:SS 格式
  const formatTimeDisplay = useCallback(() => {
    const minutes = Math.floor(timeLeft / 60)
    const seconds = timeLeft % 60
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
  }, [timeLeft])

  // 完成状态
  const [isCompleted, setIsCompleted] = useState(false)
  
  // 完成动画状态
  const [isCompletionAnimating, setIsCompletionAnimating] = useState(false)

  // 计算文字汇聚进度（0-1）
  const gatheringProgress = useMemo(() => {
    if (isCompleted) return 1 // 完成后保持汇聚状态
    if (isCompletionAnimating) return 1 // 完成动画时立即汇聚
    if (!isRunning && timeLeft === DEFAULT_TIME) return 0 // 未开始
    return Math.min((DEFAULT_TIME - timeLeft) / DEFAULT_TIME, 1) // 0到1的进度
  }, [timeLeft, isRunning, isCompleted, isCompletionAnimating])

  // 优雅的缓动函数 - 为汇聚动画添加更自然的过渡
  const easeInOutCubic = (t: number) => {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
  }

  // 应用缓动函数的汇聚进度
  const smoothGatheringProgress = useMemo(() => {
    return easeInOutCubic(gatheringProgress)
  }, [gatheringProgress])

  // 计时器逻辑
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prevTime) => {
          if (prevTime <= 1) {
            setIsRunning(false)
            setIsPaused(false)
            completeBreak()
            return 0
          }
          return prevTime - 1
        })
      }, 1000)
    }

    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [isRunning, timeLeft])

  // 开始计时器会话
  const startTimerSession = async () => {
    try {
      // 使用当前登录用户ID，如果未登录则使用测试用户ID
      const userId = user?.id || "78888489-6410-4888-aceb-b2ed98fc45f8" // 备用测试用户
      
      const response = await fetch(`http://localhost:8000/api/timer/start?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          timer_type_id: 2, // inspire类型的ID
          planned_duration: Math.round(timeLeft) // 计划时长（秒）
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ 放牧会话开始:', result)
        // 将API返回的数据转换为TimerSession格式
        const sessionData: TimerSession = {
          session_id: result.data.session_id,
          timer_type_id: result.data.timer_type_id,
          planned_duration: result.data.planned_duration,
          started_at: result.data.started_at
        }
        setCurrentSession(sessionData)
        setSessionStartTime(new Date())
      } else {
        console.error('❌ 开始放牧会话失败:', response.status)
      }
    } catch (error) {
      console.error('❌ 开始放牧会话错误:', error)
    }
  }

  // 完成计时器会话
  const completeTimerSession = async () => {
    if (!currentSession || !sessionStartTime) return
    
    try {
      // 使用当前登录用户ID，如果未登录则使用测试用户ID
      const userId = user?.id || "78888489-6410-4888-aceb-b2ed98fc45f8" // 备用测试用户
      const actualDuration = Math.round((Date.now() - sessionStartTime.getTime()) / 1000)
      
      const response = await fetch(`http://localhost:8000/api/timer/complete?user_id=${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: currentSession.session_id || currentSession,
          actual_duration: actualDuration
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ 放牧会话完成:', result)
        setCurrentSession(null)
        setSessionStartTime(null)
      } else {
        console.error('❌ 完成放牧会话失败:', response.status)
      }
    } catch (error) {
      console.error('❌ 完成放牧会话错误:', error)
    }
  }

  // 开始计时
  const startTimer = () => {
    setIsRunning(true)
    setIsPaused(false)
    setIsCompleted(false) // 重置完成状态，让文字重新散开
    startTimerSession() // 启动后端会话
  }

  // 暂停计时
  const pauseTimer = () => {
    setIsRunning(false)
    setIsPaused(true)
  }

  // 继续计时
  const resumeTimer = () => {
    setIsRunning(true)
    setIsPaused(false)
  }

  // 完成休息
  const completeBreak = () => {
    setIsCompletionAnimating(true) // 开始优雅的完成动画
    
    // 完成后端会话
    completeTimerSession()
    
    // 延迟设置完成状态，创造流畅的动画效果
    setTimeout(() => {
      setIsCompleted(true) // 立即触发汇聚完成，保持不变
      setCompletedBreaks(completedBreaks + 1)
      setTimeLeft(DEFAULT_TIME)
      setIsRunning(false)
      setIsPaused(false)
      setIsCompletionAnimating(false)
    }, 800) // 800ms的优雅过渡时间
    // 移除自动重置，保持汇聚状态
  }

  // 返回主页
  const goHome = () => {
    router.push("/")
  }

  // 音乐播放控制
  const toggleBGM = () => {
    if (!audio) {
      const newAudio = new Audio('/Miles Davis - Générique.mp3')
      newAudio.loop = true
      newAudio.volume = 0.5
      setAudio(newAudio)
      newAudio.play()
      setIsPlaying(true)
    } else {
      if (isPlaying) {
        audio.pause()
        setIsPlaying(false)
      } else {
        audio.play()
        setIsPlaying(true)
      }
    }
  }

  // 清理音频资源
  useEffect(() => {
    return () => {
      if (audio) {
        audio.pause()
        audio.src = ''
      }
    }
  }, [audio])

  // 任务编辑功能
  const openEditModal = () => {
    setEditingTitle(taskTitle)
    setShowEditModal(true)
  }

  const closeEditModal = () => {
    setShowEditModal(false)
    setEditingTitle("")
  }

  const saveTaskTitle = () => {
    if (editingTitle.trim() && editingTitle.trim().length <= 15) {
      setTaskTitle(editingTitle.trim())
      closeEditModal()
    }
  }

  const handleEditKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      saveTaskTitle()
    } else if (e.key === 'Escape') {
      closeEditModal()
    }
  }

  // 计算图标透明度（基于进度和完成状态）
  const iconOpacity = useMemo(() => {
    if (isCompleted) return 1 // 完成时100%
    if (!isRunning && timeLeft === DEFAULT_TIME) return 0.3 // 未开始时30%
    // 计时进行中：从30%到100%线性变化
    const progress = (DEFAULT_TIME - timeLeft) / DEFAULT_TIME
    return 0.3 + (progress * 0.7) // 30% + 70% * progress
  }, [timeLeft, isRunning, isCompleted, DEFAULT_TIME])

  // 初始化音频
  useEffect(() => {
    const audioElement = new Audio('/Miles Davis - Générique.mp3')
    audioElement.loop = true
    audioElement.volume = 0.3 // 设置音量为30%
    setAudio(audioElement)

    // 进入页面时自动播放音乐
    const playAudio = async () => {
      try {
        await audioElement.play()
        setIsPlaying(true)
      } catch (error) {
        console.log('自动播放被浏览器阻止，需要用户交互后播放:', error)
        setIsPlaying(false)
      }
    }
    playAudio()

    return () => {
      audioElement.pause()
      audioElement.src = ''
    }
  }, [])

  return (
    <div
      className="min-h-screen text-white flex flex-col"
      style={{
        backgroundImage: "url(/images/background.png)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Header - 完全相同的布局 */}
      <div className="flex justify-between items-center p-6">
        {/* Logo - clickable to go back */}
        <Button
          onClick={goHome}
          variant="ghost"
          className="w-[100px] h-auto p-0 bg-transparent border-0 hover:bg-transparent hover:scale-110 transition-all duration-300"
        >
          <img 
            src="/images/logo.png" 
            alt="AURA STUDIO Logo" 
            className="w-[100px] h-auto object-contain"
          />
        </Button>
        <h1 className="text-2xl font-bold">午间休息</h1>
        {/* Sound Control */}
        <div className="flex items-center gap-2">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={toggleBGM}
            className="w-[100px] h-auto p-0 bg-transparent border-0 hover:bg-transparent hover:scale-110 transition-all duration-300"
          >
            <img 
              src="/images/vinyl.png" 
              alt="Sound Control" 
              className={`w-[100px] h-auto object-contain transition-transform duration-300 ${
                isPlaying ? 'animate-slow-spin' : ''
              }`}
            />
          </Button>
        </div>
      </div>

      {/* Main Timer Area - 完全相同的布局 */}
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        {/* Timer Icon */}
        <div className="w-32 h-32 flex items-center justify-center mb-8">
          <img 
            src="/images/break.png" 
            alt="午间休息计时器" 
            className={`w-32 h-32 object-contain transition-opacity duration-300 ${
              iconOpacity < 1 ? 'opacity-30' : ''
            }`}
            style={{ opacity: iconOpacity }}
          />
        </div>

        {/* Motivational Text with Edit Button */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <h2 className="text-2xl font-bold text-center">{taskTitle}</h2>
          <button
            onClick={openEditModal}
            className="p-1 hover:bg-white/10 rounded-lg transition-all duration-200 hover:scale-110"
          >
            <img 
              src="/images/button-edit.svg" 
              alt="编辑任务" 
              className="w-5 h-5 opacity-70 hover:opacity-100 transition-opacity duration-200"
            />
          </button>
        </div>

        {/* Timer Display - 完全相同的样式 */}
        <div className="text-6xl font-mono font-bold mb-12">
          {formatTimeDisplay()}
        </div>

        {/* Start Button - 完全相同的样式和形状 */}
        <Button
          onClick={isRunning ? completeBreak : (isPaused ? resumeTimer : startTimer)}
          className="bg-gradient-to-br from-white to-gray-200 text-purple-900 hover:from-gray-100 hover:to-gray-300 px-12 py-4 rounded-2xl text-xl font-bold shadow-lg transform hover:scale-105 transition-all duration-300"
          style={{
            clipPath: "polygon(20% 0%, 80% 0%, 100% 20%, 100% 80%, 80% 100%, 20% 100%, 0% 80%, 0% 20%)",
          }}
        >
          {isRunning ? "完成" : (isPaused ? "继续" : "开始")}
        </Button>

        {/* Pause Button - 只在计时器运行时显示 */}
        {isRunning && (
          <Button
            onClick={pauseTimer}
            variant="ghost"
            className="mt-4 text-white/70 hover:text-white hover:bg-white/10 px-6 py-2 rounded-lg text-sm transition-all duration-200"
          >
            暂停
          </Button>
        )}
      </div>

      {/* Completed Breaks - 完全相同的布局 */}
      <div className="flex justify-center gap-4 pb-8">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="w-12 h-12 flex items-center justify-center"
          >
            <img 
              src="/images/break.png" 
              alt="完成的休息" 
              className={`w-12 h-12 object-contain transition-opacity duration-300 ${
                i < completedBreaks ? "opacity-100" : "opacity-30"
              }`}
            />
          </div>
        ))}
      </div>

      {/* 飘散文字动画区域 - 只在汇聚未完成时显示 */}
      {smoothGatheringProgress < 0.95 && (
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-10">
          {textCharacters.map((charData) => {
            // 计算当前字符的位置（基于汇聚进度）
            const currentX = charData.initialX + (charData.targetX - charData.initialX) * smoothGatheringProgress
            const currentY = charData.initialY + (charData.targetY - charData.initialY) * smoothGatheringProgress
            
            // 添加轻微的漂浮偏移（在计时器运行时），增加移动幅度
            let floatOffsetX = isRunning ? Math.sin(animationFrame * 0.01 + charData.id) * 4 : 0 // 增加到4px
            let floatOffsetY = isRunning ? Math.cos(animationFrame * 0.008 + charData.id) * 3 : 0 // 增加到3px
            
            // 边界检查，防止漂浮到UI元素区域
            const finalX = currentX + floatOffsetX
            const finalY = currentY + floatOffsetY
            
            // 避开中心UI区域 (图标、标题、计时器、按钮区域)
            if (typeof window !== 'undefined') {
              const centerUIZone = {
                left: window.innerWidth * 0.2,
                right: window.innerWidth * 0.8,
                top: window.innerHeight * 0.25,
                bottom: window.innerHeight * 0.75
              }
              
              if (finalX > centerUIZone.left && finalX < centerUIZone.right && 
                  finalY > centerUIZone.top && finalY < centerUIZone.bottom) {
                floatOffsetX *= 0.3 // 减小漂浮幅度
                floatOffsetY *= 0.3
              }
            }
            
            // 动态颜色和透明度：使用#FCA079橙色系
            let color = 'rgba(252, 160, 121, 0.3)' // 默认30%透明度
            if (smoothGatheringProgress === 0) color = 'rgba(252, 160, 121, 0.3)' // 未开始时30%
            else if (isRunning && smoothGatheringProgress < 0.9) color = 'rgba(252, 160, 121, 0.3)' // 运行时30%
            else if (smoothGatheringProgress > 0.8) color = 'rgba(252, 160, 121, 0.6)' // 接近完成时60%
            
            return (
              <div
                key={charData.id}
                className="absolute text-base font-normal tracking-wider select-none pointer-events-none"
                style={{
                  left: `${currentX + floatOffsetX}px`,
                  top: `${currentY + floatOffsetY}px`,
                  color: color,
                  fontFamily: '江西拙楷, serif',
                  transform: 'translate(-50%, -50%)',
                  transition: isCompletionAnimating ? 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)' : 'color 0.3s ease',
                  zIndex: 15
                }}
              >
                {charData.char}
              </div>
            )
          })}
        </div>
      )}

      {/* 汇聚完成后的最终文字显示区域 */}
      {smoothGatheringProgress >= 0.95 && (
        <div 
          className="fixed left-1/2 transform -translate-x-1/2 pointer-events-none z-20 animate-fade-in"
          style={{ 
            top: `140px`,
            animation: 'fadeIn 1s ease-out forwards'
          }}
        >
          <div 
            className="text-xl font-medium text-center leading-relaxed max-w-2xl px-8" 
            style={{ 
              color: 'rgba(252, 160, 121, 0.6)',
              fontFamily: '江西拙楷, serif'
            }}
          >
            {floatingText}
          </div>
        </div>
      )}

      {/* 任务编辑弹窗 */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50" onClick={closeEditModal}>
          <div 
            className="bg-white rounded-xl p-6 w-[400px] max-w-[90vw] shadow-2xl" 
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">编辑任务</h3>
            <input
              type="text"
              value={editingTitle}
              onChange={(e) => setEditingTitle(e.target.value)}
              onKeyDown={handleEditKeyPress}
              placeholder="输入任务内容（最多15字）"
              maxLength={15}
              autoFocus
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-center"
            />
            <div className="text-right text-sm text-gray-500 mt-2">
              {editingTitle.length}/15
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={closeEditModal}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200"
              >
                取消
              </button>
              <button
                onClick={saveTaskTitle}
                disabled={!editingTitle.trim() || editingTitle.trim().length > 15}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 