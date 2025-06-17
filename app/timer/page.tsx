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

        {/* Motivational Text */}
        <h2 className="text-2xl font-bold mb-8 text-center">每天早起干活一小时</h2>

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
    </div>
  )
}

 