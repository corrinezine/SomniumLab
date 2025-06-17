"use client"

import { useState, useEffect, useCallback } from "react"
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

  // 格式化时间显示为 MM:SS 格式
  const formatTimeDisplay = useCallback(() => {
    const totalMinutes = Math.floor(timeLeft / 60)
    const seconds = timeLeft % 60
    return `${totalMinutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }, [timeLeft])

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
    setCompletedPomodoros(completedPomodoros + 1)
    setTimeLeft(DEFAULT_TIME)
    setIsRunning(false)
    setIsPaused(false)
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
            className="w-32 h-32 object-contain"
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

 