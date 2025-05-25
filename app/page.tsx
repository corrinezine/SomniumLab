"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Play, Pause, Volume2, VolumeX } from "lucide-react"
import { callGuideChat, ChatMessage, APIError } from "@/lib/api"

export default function HomePage() {
  const [currentView, setCurrentView] = useState<"home" | "guide" | "work" | "break">("home")
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [completedPomodoros, setCompletedPomodoros] = useState(0)
  const [completedBreaks, setCompletedBreaks] = useState(0)
  const [timerMinutes, setTimerMinutes] = useState(60)
  const [timerSeconds, setTimerSeconds] = useState(0)
  const [isTimerRunning, setIsTimerRunning] = useState(false)
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null)
  const [showEasterEgg, setShowEasterEgg] = useState(false)

  const toggleBGM = () => {
    if (!audio) {
      const newAudio = new Audio('/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3')
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

  const toggleMute = () => {
    setIsMuted(!isMuted)
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

  // 处理guide点击事件
  const handleGuideClick = () => {
    setShowEasterEgg(true)
  }

  // 关闭彩蛋弹窗
  const closeEasterEgg = () => {
    setShowEasterEgg(false)
  }

  // 监听ESC键关闭弹窗
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && showEasterEgg) {
        closeEasterEgg()
      }
    }

    if (showEasterEgg) {
      document.addEventListener('keydown', handleEscKey)
      // 防止背景滚动
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey)
      document.body.style.overflow = 'unset'
    }
  }, [showEasterEgg])

  if (currentView === "guide") {
    return (
      <GuideRoundtable
        onBack={() => setCurrentView("home")}
        isPlaying={isPlaying}
        toggleBGM={toggleBGM}
        isMuted={isMuted}
        toggleMute={toggleMute}
      />
    )
  }

  if (currentView === "work") {
    return (
      <DeepWork
        onBack={() => setCurrentView("home")}
        isPlaying={isPlaying}
        toggleBGM={toggleBGM}
        isMuted={isMuted}
        toggleMute={toggleMute}
        completedPomodoros={completedPomodoros}
        setCompletedPomodoros={setCompletedPomodoros}
      />
    )
  }

  if (currentView === "break") {
    return (
      <BreakTime
        onBack={() => setCurrentView("home")}
        isPlaying={isPlaying}
        toggleBGM={toggleBGM}
        isMuted={isMuted}
        toggleMute={toggleMute}
        completedBreaks={completedBreaks}
        setCompletedBreaks={setCompletedBreaks}
      />
    )
  }

  return (
    <div
      className="min-h-screen text-white relative"
      style={{
        backgroundImage: "url(/images/background.png)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Header */}
      <div className="flex justify-between items-center p-6 relative z-10">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <img 
            src="/images/logo.png" 
            alt="AURA STUDIO Logo" 
            className="w-[100px] h-auto object-contain"
          />
        </div>
        <h1 className="text-2xl font-bold tracking-wider">AURA STUDIO</h1>
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

      {/* Main Content */}
      <div className="flex flex-col items-center justify-center px-6 mt-16">
        {/* Function Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-16 mb-16 justify-items-center">
          {/* Deep Work */}
          <div className="flex flex-col items-center gap-4">
            <Button
              onClick={() => setCurrentView("work")}
              className="w-[100px] h-[100px] p-0 bg-transparent border-0 shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center"
            >
              <img 
                src="/images/work.png" 
                alt="深度工作" 
                className="w-[100px] h-[100px] object-contain"
              />
            </Button>
            <div className="text-center">
              <div className="text-lg font-medium text-white">深度工作</div>
              <div className="text-sm text-white/50">{completedPomodoros}次</div>
            </div>
          </div>

          {/* Lunch Break */}
          <div className="flex flex-col items-center gap-4">
            <Button
              onClick={() => setCurrentView("break")}
              className="w-[100px] h-[100px] p-0 bg-transparent border-0 shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center"
            >
              <img 
                src="/images/break.png" 
                alt="午间休息" 
                className="w-[100px] h-[100px] object-contain"
              />
            </Button>
            <div className="text-center">
              <div className="text-lg font-medium text-white">午间休息</div>
              <div className="text-sm text-white/50">{completedBreaks}次</div>
            </div>
          </div>

          {/* Guide Roundtable */}
          <div className="flex flex-col items-center gap-4">
            <Button
              onClick={() => setCurrentView("guide")}
              className="w-[100px] h-[100px] p-0 bg-transparent border-0 shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center"
            >
              <img 
                src="/images/roundtable.png" 
                alt="向导圆桌" 
                className="w-[100px] h-[100px] object-contain"
              />
            </Button>
            <div className="text-center">
              <div className="text-lg font-medium text-white">向导圆桌</div>
              <div className="text-sm text-white/50">0次</div>
            </div>
          </div>
        </div>

        {/* Dream Text */}
        <div className="text-center text-white mb-16 px-6 max-w-md mx-auto">
          
          <br />
          <p className="text-base leading-relaxed text-purple-200">
            当你抵达北纬39°54', 东经116°23'<br />
            梦境管理局的入口将显现于此
          </p>
          <br />
          <p className="text-base leading-relaxed text-purple-200">
            那些散落的梦境碎片，等待与你相遇<br />
            引导者将带您经历一段奇幻的旅程
          </p>
        </div>

        {/* Bottom Illustration */}
        <div className="absolute bottom-0 left-0 right-0 w-full overflow-hidden">
          {/* Bottom Background - Show upper half, hide lower half */}
          <div className="relative w-full h-[200px]">
            <img
              src="/images/bottom-background.png"
              alt="Bottom background"
              className="w-full h-[400px] object-cover object-top absolute -bottom-[200px]"
            />

            {/* Guide Characters positioned above the background */}
            <div className="absolute bottom-0 left-0 right-0 flex justify-between items-end px-8 pb-4 z-10">
              {/* Guide 1 */}
              <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110" onClick={handleGuideClick}>
                <img src="/images/guide1.png" alt="Guide 1" className="w-[100px] h-auto object-contain" />
              </div>

              {/* Guide 2 */}
              <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110" onClick={handleGuideClick}>
                <img src="/images/guide2.png" alt="Guide 2" className="w-[100px] h-auto object-contain" />
              </div>

              {/* Guide 3 */}
              <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110" onClick={handleGuideClick}>
                <img src="/images/guide3.png" alt="Guide 3" className="w-[100px] h-auto object-contain" />
              </div>

              {/* Guide 4 */}
              <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110" onClick={handleGuideClick}>
                <img src="/images/guide4.png" alt="Guide 4" className="w-[100px] h-auto object-contain" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Easter Egg Modal */}
      {showEasterEgg && (
        <div 
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 modal-overlay p-4"
          onClick={closeEasterEgg}
        >
          <div 
            className="relative max-w-lg max-h-[70vh] modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <img 
              src="/images/彩蛋.png" 
              alt="彩蛋" 
              className="w-full h-auto object-contain rounded-lg shadow-2xl"
            />
            <button
              onClick={closeEasterEgg}
              className="absolute top-3 right-3 w-10 h-10 bg-white hover:bg-gray-100 rounded-full flex items-center justify-center text-gray-600 text-2xl font-bold transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-110"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function GuideRoundtable({
  onBack,
  isPlaying,
  toggleBGM,
  isMuted,
  toggleMute,
}: {
  onBack: () => void
  isPlaying: boolean
  toggleBGM: () => void
  isMuted: boolean
  toggleMute: () => void
}) {
  const [messages, setMessages] = useState([
    { id: 1, text: "欢迎来到向导圆桌！我是你的智能向导，专门负责项目咨询和创意指导。请告诉我你需要什么帮助？", isUser: false, time: "Wed 8:21 AM" },
  ])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = async () => {
    if (inputText.trim() && !isLoading) {
      const userMessage = inputText.trim()
      const currentTime = new Date().toLocaleTimeString('en-US', { 
        weekday: 'short', 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
      const newUserMessage = { id: Date.now(), text: userMessage, isUser: true, time: currentTime }
      
      // 添加用户消息
      setMessages(prev => [...prev, newUserMessage])
      setInputText("")
      setIsLoading(true)
      setError(null)

      // 添加"正在思考"的临时消息
      const thinkingMessage = { id: Date.now() + 1, text: "正在思考中...", isUser: false, time: currentTime }
      setMessages(prev => [...prev, thinkingMessage])

      try {
        // 准备API请求数据
        const chatHistory: ChatMessage[] = messages
          .filter(msg => msg.text !== "正在思考中...")
          .map(msg => ({
            role: msg.isUser ? 'user' as const : 'assistant' as const,
            content: msg.text
          }))
        
        // 添加当前用户消息
        chatHistory.push({
          role: 'user',
          content: userMessage
        })

        // 调用API
        const response = await callGuideChat({
          guide_id: 'roundtable',
          messages: chatHistory
        })

        // 移除"正在思考"消息，添加AI回复
        setMessages(prev => {
          const withoutThinking = prev.filter(msg => msg.text !== "正在思考中...")
          const replyTime = new Date().toLocaleTimeString('en-US', { 
            weekday: 'short', 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          })
          return [...withoutThinking, {
            id: Date.now() + 2,
            text: response.reply,
            isUser: false,
            time: replyTime
          }]
        })

      } catch (error) {
        console.error('API调用失败:', error)
        
        // 移除"正在思考"消息
        setMessages(prev => prev.filter(msg => msg.text !== "正在思考中..."))
        
        // 设置错误信息
        if (error instanceof APIError) {
          setError(error.message)
        } else {
          setError('发送消息失败，请稍后重试')
        }
        
        // 添加错误提示消息
        const errorTime = new Date().toLocaleTimeString('en-US', { 
          weekday: 'short', 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
        setMessages(prev => [...prev, {
          id: Date.now() + 2,
          text: "抱歉，我暂时无法回复。请稍后重试。",
          isUser: false,
          time: errorTime
        }])
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div
      className="min-h-screen text-white"
      style={{
        backgroundImage: "url(/images/background.png)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Header */}
      <div className="flex justify-between items-center p-6">
        {/* Logo - clickable to go back */}
        <Button
          onClick={onBack}
          variant="ghost"
          className="w-[100px] h-auto p-0 bg-transparent border-0 hover:scale-105 transition-all duration-300"
        >
          <img 
            src="/images/logo.png" 
            alt="AURA STUDIO Logo" 
            className="w-[100px] h-auto object-contain"
          />
        </Button>
        <h1 className="text-2xl font-bold">向导圆桌</h1>
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

      {/* Time */}
      <div className="text-center text-purple-300 mb-8">Wed 8:21 AM</div>

      {/* Messages */}
      <div className="flex-1 px-6 space-y-4 mb-24">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? "justify-end" : "justify-start"} items-start gap-3`}
          >
            {!message.isUser && (
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex-shrink-0"></div>
            )}
            <div
              className={`max-w-xs px-4 py-3 rounded-2xl ${
                message.isUser ? "bg-purple-600 text-white" : "bg-white/10 backdrop-blur-sm text-white"
              }`}
            >
              {message.text}
            </div>
            {message.isUser && (
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-full flex-shrink-0"></div>
            )}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="fixed bottom-6 left-6 right-6 flex gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            placeholder="请输入"
            className="w-full px-4 py-3 bg-white/10 backdrop-blur-sm rounded-full text-white placeholder-purple-300 border border-white/20 focus:outline-none focus:border-white/40"
          />
        </div>
        <Button
          onClick={sendMessage}
          className="w-12 h-12 bg-purple-600 hover:bg-purple-700 rounded-full flex items-center justify-center"
        >
          <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
          </div>
        </Button>
      </div>
    </div>
  )
}

function DeepWork({
  onBack,
  isPlaying,
  toggleBGM,
  isMuted,
  toggleMute,
  completedPomodoros,
  setCompletedPomodoros,
}: {
  onBack: () => void
  isPlaying: boolean
  toggleBGM: () => void
  isMuted: boolean
  toggleMute: () => void
  completedPomodoros: number
  setCompletedPomodoros: (count: number) => void
}) {
  const [minutes, setMinutes] = useState(60)
  const [seconds, setSeconds] = useState(0)
  const [isRunning, setIsRunning] = useState(false)

  const startTimer = () => {
    setIsRunning(true)
    // Timer logic would go here
  }

  const completePomodoro = () => {
    setCompletedPomodoros(completedPomodoros + 1)
    setMinutes(60)
    setSeconds(0)
    setIsRunning(false)
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
      {/* Header */}
      <div className="flex justify-between items-center p-6">
        {/* Logo - clickable to go back */}
        <Button
          onClick={onBack}
          variant="ghost"
          className="w-[100px] h-auto p-0 bg-transparent border-0 hover:scale-105 transition-all duration-300"
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

      {/* Main Timer Area */}
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

        {/* Timer Display */}
        <div className="text-6xl font-mono font-bold mb-12">
          {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}:00
        </div>

        {/* Start Button */}
        <Button
          onClick={isRunning ? completePomodoro : startTimer}
          className="bg-gradient-to-br from-white to-gray-200 text-purple-900 hover:from-gray-100 hover:to-gray-300 px-12 py-4 rounded-2xl text-xl font-bold shadow-lg transform hover:scale-105 transition-all duration-300"
          style={{
            clipPath: "polygon(20% 0%, 80% 0%, 100% 20%, 100% 80%, 80% 100%, 20% 100%, 0% 80%, 0% 20%)",
          }}
        >
          {isRunning ? "完成" : "开始"}
        </Button>
      </div>

      {/* Completed Pomodoros */}
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

function BreakTime({
  onBack,
  isPlaying,
  toggleBGM,
  isMuted,
  toggleMute,
  completedBreaks,
  setCompletedBreaks,
}: {
  onBack: () => void
  isPlaying: boolean
  toggleBGM: () => void
  isMuted: boolean
  toggleMute: () => void
  completedBreaks: number
  setCompletedBreaks: (count: number) => void
}) {
  const [minutes, setMinutes] = useState(15)
  const [seconds, setSeconds] = useState(0)
  const [isRunning, setIsRunning] = useState(false)

  const startTimer = () => {
    setIsRunning(true)
    // Timer logic would go here
  }

  const completeBreak = () => {
    setCompletedBreaks(completedBreaks + 1)
    setMinutes(15)
    setSeconds(0)
    setIsRunning(false)
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
      {/* Header */}
      <div className="flex justify-between items-center p-6">
        {/* Logo - clickable to go back */}
        <Button
          onClick={onBack}
          variant="ghost"
          className="w-[100px] h-auto p-0 bg-transparent border-0 hover:scale-105 transition-all duration-300"
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

      {/* Main Timer Area */}
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        {/* Timer Icon */}
        <div className="w-32 h-32 flex items-center justify-center mb-8">
          <img 
            src="/images/break.png" 
            alt="午间休息计时器" 
            className="w-32 h-32 object-contain"
          />
        </div>

        {/* Motivational Text */}
        <h2 className="text-2xl font-bold mb-8 text-center">放松身心，享受片刻宁静</h2>

        {/* Timer Display */}
        <div className="text-6xl font-mono font-bold mb-12">
          {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}:00
        </div>

        {/* Start Button */}
        <Button
          onClick={isRunning ? completeBreak : startTimer}
          className="bg-gradient-to-br from-white to-gray-200 text-purple-900 hover:from-gray-100 hover:to-gray-300 px-12 py-4 rounded-2xl text-xl font-bold shadow-lg transform hover:scale-105 transition-all duration-300"
          style={{
            clipPath: "polygon(20% 0%, 80% 0%, 100% 20%, 100% 80%, 80% 100%, 20% 100%, 0% 80%, 0% 20%)",
          }}
        >
          {isRunning ? "完成" : "开始"}
        </Button>
      </div>

      {/* Completed Breaks */}
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
    </div>
  )
}
