"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

export default function TimerPage() {
  const router = useRouter()
  
  // 默认90分钟 = 5400秒
  const DEFAULT_TIME = 90 * 60
  
  // 计时器状态
  const [timeLeft, setTimeLeft] = useState(DEFAULT_TIME) // 剩余时间（秒）
  const [isRunning, setIsRunning] = useState(false) // 是否正在运行
  const [isPaused, setIsPaused] = useState(false) // 是否暂停
  const [completedPomodoros, setCompletedPomodoros] = useState(0) // 完成的番茄钟
  
  // 音乐播放状态
  const [isPlaying, setIsPlaying] = useState(false)
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null)
  
  // 任务编辑状态
  const [taskTitle, setTaskTitle] = useState("每天早起干活一小时")
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTitle, setEditingTitle] = useState("")

  // 飘散文字动画状态
  const floatingText = "我们必须观察生命与事物如何运动，以及它们如何反射在我们身上"
  const [textCharacters, setTextCharacters] = useState<Array<{
    char: string
    id: number
    initialX: number
    initialY: number
    targetX: number
    targetY: number
  }>>([])
  const [animationFrame, setAnimationFrame] = useState(0)

  // 漂浮动画循环
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
      // 计算最终文字的布局位置（在work.png上方）
      const charsPerLine = 20 // 每行大约20个字符
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
    const totalMinutes = Math.floor(timeLeft / 60)
    const seconds = timeLeft % 60
    return `${totalMinutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }, [timeLeft])

  // 完成状态
  const [isCompleted, setIsCompleted] = useState(false)

  // 计算文字汇聚进度（0-1）
  const gatheringProgress = useMemo(() => {
    if (isCompleted) return 1 // 点击完成按钮后立即汇聚
    if (!isRunning && timeLeft === DEFAULT_TIME) return 0 // 未开始
    return Math.min((DEFAULT_TIME - timeLeft) / DEFAULT_TIME, 1) // 0到1的进度
  }, [timeLeft, isRunning, isCompleted])

  // 计算图标透明度（基于进度和完成状态）
  const iconOpacity = useMemo(() => {
    if (isCompleted) return 1 // 完成时100%
    if (!isRunning && timeLeft === DEFAULT_TIME) return 0.3 // 未开始时30%
    // 计时进行中：从30%到100%线性变化
    const progress = (DEFAULT_TIME - timeLeft) / DEFAULT_TIME
    return 0.3 + (progress * 0.7) // 30% + 70% * progress
  }, [timeLeft, isRunning, isCompleted, DEFAULT_TIME])

  // 计时器核心逻辑
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(prevTime => {
          if (prevTime <= 1) {
            // 计时结束
            setIsRunning(false)
            setCompletedPomodoros(prev => prev + 1)
            alert("时间到！专注时间完成！")
            return DEFAULT_TIME // 重置到初始时间
          }
          return prevTime - 1
        })
      }, 1000)
    } else if (!isRunning && interval) {
      clearInterval(interval)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isRunning, timeLeft, DEFAULT_TIME])

  // 开始计时
  const startTimer = () => {
    setIsRunning(true)
    setIsPaused(false)
    setIsCompleted(false) // 重置完成状态，让文字重新散开
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

  // 完成番茄钟
  const completePomodoro = () => {
    setIsCompleted(true) // 立即触发汇聚完成，保持不变
    setCompletedPomodoros(completedPomodoros + 1)
    setTimeLeft(DEFAULT_TIME)
    setIsRunning(false)
    setIsPaused(false)
    // 移除自动重置，保持汇聚状态
  }

  // 返回主页
  const goHome = () => {
    router.push("/")
  }

  // 音乐播放控制
  const toggleBGM = () => {
    if (!audio) {
      const newAudio = new Audio('/邓翊群 - 定风波.mp3')
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
        <h1 className="text-2xl font-bold">深度工作</h1>
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
            src="/images/work.png" 
            alt="深度工作计时器" 
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
          onClick={isRunning ? completePomodoro : (isPaused ? resumeTimer : startTimer)}
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

      {/* Completed Pomodoros - 完全相同的布局 */}
      <div className="flex justify-center gap-4 pb-8">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="w-12 h-12 flex items-center justify-center"
          >
            <img 
              src="/images/work.png" 
              alt="完成的番茄钟" 
              className={`w-12 h-12 object-contain transition-opacity duration-300 ${
                i < completedPomodoros ? "opacity-100" : "opacity-30"
              }`}
            />
          </div>
        ))}
      </div>

      {/* 飘散文字动画区域 - 只在汇聚未完成时显示 */}
      {gatheringProgress < 0.95 && (
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-10">
          {textCharacters.map((charData) => {
            // 计算当前字符的位置（基于汇聚进度）
            const currentX = charData.initialX + (charData.targetX - charData.initialX) * gatheringProgress
            const currentY = charData.initialY + (charData.targetY - charData.initialY) * gatheringProgress
            
            // 添加轻微的漂浮偏移（在计时器运行时），确保不会漂浮到UI元素区域
            let floatOffsetX = isRunning ? Math.sin(animationFrame * 0.01 + charData.id) * 2 : 0
            let floatOffsetY = isRunning ? Math.cos(animationFrame * 0.008 + charData.id) * 1.5 : 0
            
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
            if (gatheringProgress === 0) color = 'rgba(252, 160, 121, 0.3)' // 未开始时30%
            else if (isRunning && gatheringProgress < 0.9) color = 'rgba(252, 160, 121, 0.3)' // 运行时30%
            else if (gatheringProgress > 0.8) color = 'rgba(252, 160, 121, 0.6)' // 接近完成时60%
            
            return (
              <div
                key={charData.id}
                className="absolute text-lg transition-all duration-500 ease-out"
                style={{
                  transform: `translate(${currentX + floatOffsetX}px, ${currentY + floatOffsetY}px)`,
                  color: color,
                  transition: 'transform 1s ease-out, color 0.5s ease-out'
                }}
              >
                {charData.char}
              </div>
            )
          })}
        </div>
      )}

      {/* 汇聚完成后的最终文字显示区域 */}
      {gatheringProgress >= 0.95 && (
        <div 
          className="fixed left-1/2 transform -translate-x-1/2 pointer-events-none z-20"
          style={{ top: `140px` }}
        >
          <div className="text-xl font-medium text-center leading-relaxed max-w-2xl px-8" style={{ color: 'rgba(252, 160, 121, 0.6)' }}>
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

 