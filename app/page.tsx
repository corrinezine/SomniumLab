"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Play, Pause, Volume2, VolumeX } from "lucide-react"
import { callGuideChat, callMultiGuideChat, ChatMessage, APIError, MultiGuideResponse } from "@/lib/api"
import dynamic from 'next/dynamic'
import { useRouter } from 'next/navigation'

// 动态导入组件以避免SSR问题
const ClientOnlyContent = dynamic(() => Promise.resolve(MainContent), {
  ssr: false,
  loading: () => <div className="min-h-screen bg-purple-900 flex items-center justify-center text-white">加载中...</div>
})

// 动态导入二维码扫描组件
const QRScannerComponent = dynamic(() => import('@/components/qr-scanner'), {
  ssr: false,
  loading: () => <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50"><div className="text-white">启动相机中...</div></div>
})

function MainContent() {
  const router = useRouter()
  const [currentView, setCurrentView] = useState<"home" | "guide" | "work">("home")
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [completedPomodoros, setCompletedPomodoros] = useState(0)

  const [timerMinutes, setTimerMinutes] = useState(60)
  const [timerSeconds, setTimerSeconds] = useState(0)
  const [isTimerRunning, setIsTimerRunning] = useState(false)
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null)
  const [showGuideCard, setShowGuideCard] = useState<number | null>(null)
  const [isCardFlipped, setIsCardFlipped] = useState(false)
  const [showQRScanner, setShowQRScanner] = useState(false)

  // 检查URL参数，如果有card参数则自动打开对应卡牌
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const cardParam = urlParams.get('card')
      
      if (cardParam) {
        const cardNumber = parseInt(cardParam)
        if (cardNumber >= 1 && cardNumber <= 4) {
          setShowGuideCard(cardNumber)
          setIsCardFlipped(false)
          
          // 清除URL参数，避免刷新时重复打开
          const newUrl = window.location.pathname
          window.history.replaceState({}, '', newUrl)
        }
      }
    }
  }, [])

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
  const handleGuideClick = (guideIndex: number) => {
    setShowGuideCard(guideIndex)
    setIsCardFlipped(false) // 重置为背面
  }

  // 关闭卡牌弹窗
  const closeGuideCard = () => {
    setShowGuideCard(null)
    setIsCardFlipped(false)
  }

  // 翻转卡牌
  const flipCard = () => {
    setIsCardFlipped(!isCardFlipped)
  }

  // 处理二维码扫描成功
  const handleQRScanSuccess = (cardParam: string) => {
    const cardNumber = parseInt(cardParam)
    if (cardNumber >= 1 && cardNumber <= 4) {
      setShowQRScanner(false)
      setShowGuideCard(cardNumber)
      setIsCardFlipped(false)
      
      // 恢复音乐播放（如果之前在播放）
      if (audio && isPlaying) {
        audio.play().catch(err => console.log("恢复音乐播放失败:", err))
      }
    }
  }

  // 关闭二维码扫描器
  const closeQRScanner = () => {
    setShowQRScanner(false)
    
    // 恢复音乐播放（如果之前在播放）
    if (audio && isPlaying) {
      audio.play().catch(err => console.log("恢复音乐播放失败:", err))
    }
  }

  // 打开二维码扫描器
  const openQRScanner = () => {
    // 暂停音乐播放以避免冲突
    if (audio && isPlaying) {
      audio.pause()
    }
    setShowQRScanner(true)
  }

  // 监听ESC键关闭弹窗
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (showQRScanner) {
          closeQRScanner()
        } else if (showGuideCard !== null) {
          closeGuideCard()
        }
      }
    }

    if (showGuideCard !== null || showQRScanner) {
      document.addEventListener('keydown', handleEscKey)
      // 防止背景滚动
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey)
      document.body.style.overflow = 'unset'
    }
  }, [showGuideCard, showQRScanner])

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
        
        {/* 中间区域：标题和扫一扫按钮 */}
        <div className="flex flex-col items-center gap-2">
          <h1 className="text-2xl font-bold tracking-wider">梦境管理局</h1>
          <div className="flex gap-2">
            <Button
              onClick={openQRScanner}
              className={`backdrop-blur-sm border border-white/30 px-4 py-1 rounded-full text-sm transition-all duration-300 hover:scale-105 ${
                showQRScanner 
                  ? 'bg-green-500/30 hover:bg-green-500/40 text-white animate-pulse' 
                  : 'bg-white/20 hover:bg-white/30 text-white'
              }`}
            >
              {showQRScanner ? '📱 扫描中...' : '📱 扫一扫'}
            </Button>
            <Button
              onClick={() => router.push('/test-timer-logs')}
              className="backdrop-blur-sm border border-orange-300/30 px-3 py-1 rounded-full text-xs transition-all duration-300 hover:scale-105 bg-orange-500/20 hover:bg-orange-500/30 text-orange-100"
            >
              🧪 测试
            </Button>
          </div>
        </div>
        
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
      <div className="flex flex-col items-center justify-center px-6" style={{ 
        minHeight: 'calc(100vh - 120px - 300px)', 
        marginTop: '60px',
        marginBottom: '300px'
      }}>
        {/* Dream Text */}
        <div className="text-center text-white mb-12 px-6 max-w-md mx-auto">
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

        {/* Function Buttons */}
        <div className="flex justify-center items-center gap-16 md:gap-24">
          {/* Focus Timer */}
          <div className="flex flex-col items-center gap-4">
            <Button
              onClick={() => router.push('/timer')}
              className="p-0 bg-transparent border-0 hover:bg-transparent shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center"
            >
              <img 
                src="/images/work.png" 
                alt="聚焦" 
                className="w-[100px] h-[100px] object-contain"
                style={{ width: '100px', height: '100px', maxWidth: '100px', maxHeight: '100px' }}
              />
            </Button>
            <div className="text-center">
              <div className="text-lg font-medium text-white">聚焦</div>
            </div>
          </div>

          {/* Inspire Timer */}
          <div className="flex flex-col items-center gap-4">
            <Button
              onClick={() => router.push('/break')}
              className="p-0 bg-transparent border-0 hover:bg-transparent shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center"
            >
              <img 
                src="/images/break.png" 
                alt="放牧" 
                className="w-[100px] h-[100px] object-contain"
                style={{ width: '100px', height: '100px', maxWidth: '100px', maxHeight: '100px' }}
              />
            </Button>
            <div className="text-center">
              <div className="text-lg font-medium text-white">放牧</div>
            </div>
          </div>

          {/* Talk Timer */}
          <div className="flex flex-col items-center gap-4">
            <Button
              onClick={() => setCurrentView("guide")}
              className="p-0 bg-transparent border-0 hover:bg-transparent shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center"
            >
              <img 
                src="/images/roundtable.png" 
                alt="篝火" 
                className="w-[100px] h-[100px] object-contain"
                style={{ width: '100px', height: '100px', maxWidth: '100px', maxHeight: '100px' }}
              />
            </Button>
            <div className="text-center">
              <div className="text-lg font-medium text-white">篝火</div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Illustration */}
      <div className="absolute bottom-0 left-0 right-0 w-full">
        {/* Bottom Background - Show upper half, hide lower half */}
        <div className="relative w-full h-[200px] overflow-hidden">
          <img
            src="/images/bottom-background.png"
            alt="Bottom background"
            className="w-full h-[400px] object-cover object-top absolute -bottom-[200px]"
          />
        </div>

        {/* Guide Characters positioned above the background */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between items-end px-8 pb-4 z-10">
          {/* Guide 1 */}
          <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110 hover:z-50" onClick={() => handleGuideClick(1)} style={{ zIndex: 10 }}>
            <img src="/images/guide1.png" alt="Guide 1" className="w-[100px] h-auto object-contain" />
          </div>

          {/* Guide 2 */}
          <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110 hover:z-50" onClick={() => handleGuideClick(2)} style={{ zIndex: 10 }}>
            <img src="/images/guide2.png" alt="Guide 2" className="w-[100px] h-auto object-contain" />
          </div>

          {/* Guide 3 */}
          <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110 hover:z-50" onClick={() => handleGuideClick(3)} style={{ zIndex: 10 }}>
            <img src="/images/guide3.png" alt="Guide 3" className="w-[100px] h-auto object-contain" />
          </div>

          {/* Guide 4 */}
          <div className="relative cursor-pointer transition-transform duration-300 hover:scale-110 hover:z-50" onClick={() => handleGuideClick(4)} style={{ zIndex: 10 }}>
            <img src="/images/guide4.png" alt="Guide 4" className="w-[100px] h-auto object-contain" />
          </div>
        </div>
      </div>

      {/* Guide Card Modal */}
      {showGuideCard !== null && (
        <div 
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 modal-overlay p-4"
          onClick={closeGuideCard}
        >
          <div 
            className="relative flex flex-col items-center justify-center modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 关闭按钮 - 顶部居中 */}
            <button
              onClick={(e) => {
                e.stopPropagation()
                closeGuideCard()
              }}
              className="mb-4 w-[25px] h-[25px] hover:scale-110 transition-all duration-200 z-20"
            >
              <img 
                src="/images/button-close.svg" 
                alt="关闭" 
                className="w-full h-full object-contain"
              />
            </button>
            
            {/* 翻转卡牌容器 - 响应式尺寸 */}
            <div 
              className="relative cursor-pointer w-[70vw] md:w-[50vw] lg:w-[40vw] xl:w-[35vw] max-w-md"
              style={{ perspective: "1200px" }}
              onClick={(e) => {
                e.stopPropagation()
                flipCard()
              }}
            >
              {/* 3D翻转卡牌容器 */}
              <div
                className="relative w-full h-auto transition-transform duration-[850ms] ease-out hover:scale-105"
                style={{
                  transformStyle: "preserve-3d",
                  transform: `rotateY(${isCardFlipped ? 180 : 0}deg)`,
                }}
              >
                {/* 卡牌背面 (初始显示) */}
                <div
                  className="w-full h-full"
                  style={{
                    backfaceVisibility: "hidden",
                    transform: "rotateY(0deg)",
                  }}
                >
                  <img 
                    src={`/images/card${showGuideCard}-back.png`}
                    alt={`Guide ${showGuideCard} 卡牌背面`} 
                    className="w-full h-auto object-contain rounded-lg shadow-2xl"
                  />
                </div>
                
                {/* 卡牌正面 (翻转后显示) */}
                <div
                  className="absolute top-0 left-0 w-full h-full"
                  style={{
                    backfaceVisibility: "hidden",
                    transform: "rotateY(180deg)",
                  }}
                >
                  <img 
                    src={`/images/card${showGuideCard}-front.png`}
                    alt={`Guide ${showGuideCard} 卡牌正面`} 
                    className="w-full h-auto object-contain rounded-lg shadow-2xl"
                  />
                </div>
              </div>
            </div>
            
            {/* 提示文字和操作按钮 */}
            {!isCardFlipped ? (
              <div className="mt-4 text-white/70 text-sm text-center">
                点击卡牌翻转
              </div>
            ) : (
              <div className="mt-6 flex gap-4 justify-center">
                {/* 保存至相册 - 主按钮 */}
                <Button
                  onClick={(e) => {
                    e.stopPropagation()
                    // TODO: 实现保存功能
                    console.log('保存至相册')
                  }}
                  className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white px-6 py-2 rounded-lg font-medium shadow-lg transition-all duration-300 hover:scale-105"
                >
                  保存至相册
                </Button>
                
                {/* 回到大厅 - 次要按钮 */}
                <Button
                  onClick={(e) => {
                    e.stopPropagation()
                    closeGuideCard()
                  }}
                  className="bg-white/20 backdrop-blur-sm border border-white/30 hover:bg-white/30 text-white px-6 py-2 rounded-lg font-medium transition-all duration-300 hover:scale-105"
                >
                  回到大厅
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* QR Scanner Modal */}
      {showQRScanner && (
        <QRScannerComponent
          onScanSuccess={handleQRScanSuccess}
          onClose={closeQRScanner}
        />
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
    { id: 1, text: "欢迎来到向导圆桌！我是你的智能向导，专门负责项目咨询和创意指导。请告诉我你需要什么帮助？", isUser: false, time: "" },
  ])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentTime, setCurrentTime] = useState("")

  // 在客户端初始化时间，避免水合错误
  useEffect(() => {
    const updateTime = () => {
      const time = new Date().toLocaleTimeString('en-US', { 
        weekday: 'short', 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
      setCurrentTime(time)
      
      // 更新初始消息的时间
      setMessages(prev => prev.map(msg => 
        msg.id === 1 ? { ...msg, time } : msg
      ))
    }
    
    updateTime()
    // 每分钟更新一次时间
    const interval = setInterval(updateTime, 60000)
    
    return () => clearInterval(interval)
  }, [])

  const sendMultiGuideQuestion = async (question: string, guides: string[]) => {
    if (isLoading) return
    
    const messageTime = new Date().toLocaleTimeString('en-US', { 
      weekday: 'short', 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
    const newUserMessage = { id: Date.now(), text: question, isUser: true, time: messageTime }
    
    // 添加用户消息
    setMessages(prev => [...prev, newUserMessage])
    setIsLoading(true)
    setError(null)

    // 添加"正在思考"的临时消息
    const thinkingMessage = { id: Date.now() + 1, text: "大师们正在思考中...", isUser: false, time: messageTime }
    setMessages(prev => [...prev, thinkingMessage])

    try {
      // 准备API请求数据
      const chatHistory: ChatMessage[] = messages
        .filter(msg => msg.text !== "正在思考中..." && msg.text !== "大师们正在思考中...")
        .map(msg => ({
          role: msg.isUser ? 'user' as const : 'assistant' as const,
          content: msg.text
        }))
      
      // 添加当前用户消息
      chatHistory.push({
        role: 'user',
        content: question
      })

      // 调用多向导API
      const response = await callMultiGuideChat({
        guides: guides,
        messages: chatHistory
      })

      // 移除"正在思考"消息，添加多个AI回复
      setMessages(prev => {
        const withoutThinking = prev.filter(msg => msg.text !== "大师们正在思考中...")
        const replyTime = new Date().toLocaleTimeString('en-US', { 
          weekday: 'short', 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
        
        const newMessages = [...withoutThinking]
        
        // 为每个向导添加回复消息
        response.replies.forEach((reply, index) => {
          newMessages.push({
            id: Date.now() + 2 + index,
            text: `**${reply.guide_name}：**\n\n${reply.reply}`,
            isUser: false,
            time: replyTime
          })
        })
        
        return newMessages
      })

    } catch (error) {
      console.error('多向导API调用失败:', error)
      
      // 移除"正在思考"消息
      setMessages(prev => prev.filter(msg => msg.text !== "大师们正在思考中..."))
      
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
        text: "抱歉，大师们暂时无法回复。请稍后重试。",
        isUser: false,
        time: errorTime
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const sendPresetQuestion = async (question: string) => {
    if (isLoading) return
    
    const messageTime = new Date().toLocaleTimeString('en-US', { 
      weekday: 'short', 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
    const newUserMessage = { id: Date.now(), text: question, isUser: true, time: messageTime }
    
    // 添加用户消息
    setMessages(prev => [...prev, newUserMessage])
    setIsLoading(true)
    setError(null)

    // 添加"正在思考"的临时消息
    const thinkingMessage = { id: Date.now() + 1, text: "正在思考中...", isUser: false, time: messageTime }
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
        content: question
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

  const sendMessage = async () => {
    if (inputText.trim() && !isLoading) {
      const userMessage = inputText.trim()
      const messageTime = new Date().toLocaleTimeString('en-US', { 
        weekday: 'short', 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
      const newUserMessage = { id: Date.now(), text: userMessage, isUser: true, time: messageTime }
      
      // 添加用户消息
      setMessages(prev => [...prev, newUserMessage])
      setInputText("")
      setIsLoading(true)
      setError(null)

      // 添加"正在思考"的临时消息
      const thinkingMessage = { id: Date.now() + 1, text: "正在思考中...", isUser: false, time: messageTime }
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
          className="w-[100px] h-auto p-0 bg-transparent border-0 hover:bg-transparent hover:scale-110 transition-all duration-300"
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
      <div className="text-center text-purple-300 mb-8">{currentTime}</div>

      {/* Messages */}
      <div className="flex-1 px-6 md:px-12 lg:px-20 space-y-4 mb-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? "justify-end" : "justify-start"} items-start gap-3`}
          >
            {!message.isUser && (
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex-shrink-0"></div>
            )}
            <div
              className={`max-w-xs md:max-w-[60%] px-4 py-3 rounded-2xl ${
                message.isUser ? "text-white" : "bg-white/10 backdrop-blur-sm text-white"
              }`}
              style={message.isUser ? { backgroundColor: '#3D2E94' } : {}}
            >
              <div className="whitespace-pre-wrap">
                {message.text.split(/(\*\*.*?\*\*)/).map((part, index) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={index}>{part.slice(2, -2)}</strong>
                  }
                  return part
                })}
              </div>
            </div>
            {message.isUser && (
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-full flex-shrink-0"></div>
            )}
          </div>
        ))}
      </div>

      {/* Preset Questions */}
      {messages.length === 1 && (
        <div className="px-6 md:px-12 lg:px-20 mb-6">
          <div className="text-center text-purple-300 text-sm mb-4">💡 试试这些有趣的问题</div>
          <div className="flex flex-wrap gap-3 justify-center">
            <Button
              onClick={() => sendPresetQuestion("博尔赫斯和卡尔维诺相遇会聊什么？")}
              className="bg-white/10 backdrop-blur-sm text-white border border-white/20 hover:bg-white/20 px-4 py-2 rounded-full text-sm transition-all duration-300 hover:scale-105"
            >
              📚 博尔赫斯和卡尔维诺相遇会聊什么？
            </Button>
            <Button
              onClick={() => sendPresetQuestion("如何设计一个梦境记录应用？")}
              className="bg-white/10 backdrop-blur-sm text-white border border-white/20 hover:bg-white/20 px-4 py-2 rounded-full text-sm transition-all duration-300 hover:scale-105"
            >
              💭 如何设计一个梦境记录应用？
            </Button>
            <Button
              onClick={() => sendPresetQuestion("创意工作室需要什么样的氛围？")}
              className="bg-white/10 backdrop-blur-sm text-white border border-white/20 hover:bg-white/20 px-4 py-2 rounded-full text-sm transition-all duration-300 hover:scale-105"
            >
              🎨 创意工作室需要什么样的氛围？
            </Button>
            <Button
              onClick={() => sendMultiGuideQuestion("什么是真正的创造力？", ["borges", "calvino", "benjamin", "foucault"])}
              className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm text-white border border-purple-300/30 hover:from-purple-500/30 hover:to-pink-500/30 px-4 py-2 rounded-full text-sm transition-all duration-300 hover:scale-105"
            >
              ✨ 大师圆桌：什么是真正的创造力？
            </Button>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="fixed bottom-6 left-6 right-6 md:left-12 md:right-12 lg:left-20 lg:right-20 flex">
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
          className="h-[50px] w-[50px] p-0 bg-transparent border-0 hover:bg-transparent hover:scale-110 transition-all duration-300"
          style={{
            backgroundImage: "url(/images/button-send.svg)",
            backgroundSize: "50px 50px",
            backgroundRepeat: "no-repeat",
            backgroundPosition: "center"
          }}
        >
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
  const router = useRouter()
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
          onClick={() => router.push('/timer')}
          className="bg-gradient-to-br from-white to-gray-200 text-purple-900 hover:from-gray-100 hover:to-gray-300 px-12 py-4 rounded-2xl text-xl font-bold shadow-lg transform hover:scale-105 transition-all duration-300"
          style={{
            clipPath: "polygon(20% 0%, 80% 0%, 100% 20%, 100% 80%, 80% 100%, 20% 100%, 0% 80%, 0% 20%)",
          }}
        >
          开始
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



export default function HomePage() {
  return <ClientOnlyContent />
}
