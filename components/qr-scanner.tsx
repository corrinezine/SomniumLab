"use client"

import { useEffect, useRef, useState } from "react"
import QrScanner from "qr-scanner"

interface QRScannerProps {
  onScanSuccess: (result: string) => void
  onClose: () => void
}

const QRScannerComponent = ({ onScanSuccess, onClose }: QRScannerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [scanner, setScanner] = useState<QrScanner | null>(null)
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  const [error, setError] = useState<string>("")
  const [scanSuccess, setScanSuccess] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string>("")
  const [showFileUpload, setShowFileUpload] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!videoRef.current) return

    // 添加视频错误监听器，静默处理play()相关错误
    const handleVideoError = (event: Event) => {
      console.log("📺 视频事件:", event.type)
    }
    
    const videoElement = videoRef.current
    videoElement.addEventListener('error', handleVideoError)
    videoElement.addEventListener('abort', handleVideoError)

    const initScanner = async () => {
      try {
        console.log("🎥 开始初始化扫描器...")
        

        // 检查是否为localhost环境
        const isLocalhost = window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' ||
                           window.location.hostname.startsWith('192.168.')
        
        // 检查是否为HTTPS
        const isHttps = window.location.protocol === 'https:'
        
        console.log("🌐 环境检查:", { 
          hostname: window.location.hostname, 
          protocol: window.location.protocol,
          isLocalhost, 
          isHttps 
        })

        // 如果不是HTTPS且不是localhost，显示文件上传选项
        if (!isHttps && !isLocalhost) {
          setShowFileUpload(true)
          setError(`相机API需要HTTPS连接\n\n请选择以下方式之一：\n1. 点击下方"上传二维码图片"按钮\n2. 访问 https://localhost:8443\n3. 部署到HTTPS服务器`)
          return
        }

        // 检查是否支持相机
        const hasCamera = await QrScanner.hasCamera()
        console.log("📷 相机支持检查:", hasCamera)
        
        if (!hasCamera) {
          setShowFileUpload(true)
          setError("设备没有可用的摄像头\n\n请使用文件上传功能：")
          return
        }

        
        
        // 获取可用的相机设备 - 使用正确的API
        const cameras = await QrScanner.listCameras(true)
        console.log("📷 可用相机设备:", cameras)
        
        // 更智能地查找后置相机
        const backCamera = cameras.find(camera => {
          const label = camera.label.toLowerCase()
          const deviceId = camera.id ? camera.id.toLowerCase() : ''
          
          // 检查多种后置相机的标识
          const isBackCamera = 
            label.includes('back') ||
            label.includes('rear') || 
            label.includes('environment') ||
            label.includes('facing back') ||
            label.includes('后置') ||
            label.includes('背面') ||
            deviceId.includes('back') ||
            deviceId.includes('rear') ||
            deviceId.includes('environment')
          
          console.log(`📷 相机检查: ${camera.label} (ID: ${camera.id}) - 是后置相机: ${isBackCamera}`)
          return isBackCamera
        })
        
        // 如果没找到后置相机，尝试选择非前置相机
        const selectedCamera = backCamera || cameras.find(camera => {
          const label = camera.label.toLowerCase()
          const isNotFrontCamera = !label.includes('front') && !label.includes('user') && !label.includes('前置')
          console.log(`📷 备选相机: ${camera.label} - 非前置相机: ${isNotFrontCamera}`)
          return isNotFrontCamera
        })
        
        console.log("📷 最终选择的相机:", selectedCamera)
        console.log("📷 是否找到后置相机:", !!backCamera)
        
        // 设置相机状态信息
        const cameraType = backCamera ? "后置相机" : selectedCamera ? "前置相机" : "默认相机"
        console.log("📷 使用相机类型:", cameraType)

        // 创建扫描器配置 - 使用新的API格式
        const scannerConfig = {
          highlightScanRegion: false,
          highlightCodeOutline: false,
          maxScansPerSecond: 5,
          preferredCamera: selectedCamera?.id || 'environment', // 使用id属性
          returnDetailedScanResult: true as const, // 启用详细扫描结果
        }

        console.log("📷 扫描器配置:", scannerConfig)

        // 创建扫描器
        const qrScanner = new QrScanner(
          videoRef.current!,
          (result: QrScanner.ScanResult) => {
            console.log("✅ 扫描结果:", result)
            // 新API返回对象，包含data属性
            handleScanResult(result.data)
          },
          scannerConfig
        )

        setScanner(qrScanner)
        
        
        // 启动扫描
        await qrScanner.start()
        console.log("✅ 相机启动成功")
        
        // 确保视频元素正确播放 - 改进处理逻辑
        if (videoRef.current) {
          try {
            // 等待一小段时间让QrScanner完成初始化
            await new Promise(resolve => setTimeout(resolve, 100))
            await videoRef.current.play()
          } catch (playError) {
            console.log("⚠️ 视频播放中断，这是正常的", playError)
            // 这个错误通常是正常的，QrScanner会自己处理视频播放
            // 不抛出错误，继续执行
          }
        }
        
        setHasPermission(true)
        
        
        // 设置30秒超时
        timeoutRef.current = setTimeout(() => {
          console.log("⏰ 扫描超时，自动关闭")
          onClose()
        }, 15000)
        
      } catch (err) {
        console.error("❌ 启动扫描器失败:", err)
        
        let errorMessage = "启动相机时发生未知错误"
        
        if (err instanceof Error) {
          console.log("错误详情:", {
            name: err.name,
            message: err.message,
            stack: err.stack
          })
          
          switch (err.name) {
            case 'NotAllowedError':
              setShowFileUpload(true)
              errorMessage = "需要相机权限才能扫描二维码\n\n解决方案：\n1. 点击地址栏的相机图标允许权限\n2. 刷新页面重试\n3. 或使用下方文件上传功能"
              break
            case 'NotFoundError':
              setShowFileUpload(true)
              errorMessage = "未找到可用的摄像头设备\n\n请使用文件上传功能："
              break
            case 'NotReadableError':
              setShowFileUpload(true)
              errorMessage = "相机正被其他应用使用\n\n请：\n1. 关闭其他使用相机的应用\n2. 或使用下方文件上传功能"
              break
            case 'OverconstrainedError':
              errorMessage = "相机配置不支持\n正在尝试使用默认配置..."
              // 尝试使用更宽松的配置重新启动
              setTimeout(() => retryWithFallback(), 1000)
              return
            case 'SecurityError':
              setShowFileUpload(true)
              errorMessage = "相机访问被安全策略阻止\n\n需要HTTPS连接：\n1. 访问 https://localhost:8443\n2. 或使用下方文件上传功能"
              break
            case 'AbortError':
              // 检查是否是play()相关的错误
              if (err.message && (err.message.includes('play()') || err.message.includes('interrupted'))) {
                console.log("⚠️ 视频播放被中断，尝试自动修复...")
                // 使用智能重试机制
                setTimeout(() => retryWithVideoFix(), 100)
                return
              } else {
                setShowFileUpload(true)
                errorMessage = "相机启动失败\n\n请使用文件上传功能："
              }
              break
            default:
              setShowFileUpload(true)
              errorMessage = `相机启动失败: ${err.message}\n\n请使用文件上传功能：`
          }
        }
        
        setError(errorMessage)
        setHasPermission(false)
        
      }
    }

    // 备用方案：使用更宽松的配置重试
    const retryWithFallback = async () => {
      try {
        console.log("🔄 尝试备用配置...")
        setDebugInfo("使用备用配置重试...")
        
        // 在备用配置中也尝试获取相机列表
        const cameras = await QrScanner.listCameras(true)
        const backCamera = cameras.find(camera => {
          const label = camera.label.toLowerCase()
          return label.includes('back') || label.includes('rear') || label.includes('environment')
        })
        
        console.log("🔄 备用配置选择的相机:", backCamera)
        
        const qrScanner = new QrScanner(
          videoRef.current!,
          (result: QrScanner.ScanResult) => {
            console.log("✅ 扫描结果 (备用):", result)
            handleScanResult(result.data)
          },
          {
            highlightScanRegion: false,
            highlightCodeOutline: false,
            maxScansPerSecond: 3,
            preferredCamera: backCamera?.id || 'environment', // 在备用配置中也优先使用后置相机
            returnDetailedScanResult: true as const,
          }
        )

        setScanner(qrScanner)
        await qrScanner.start()
        console.log("✅ 备用配置启动成功")
        setHasPermission(true)
        
        setError("")
        
      } catch (fallbackErr) {
        console.error("❌ 备用配置也失败:", fallbackErr)
        setShowFileUpload(true)
        setError("所有相机配置都失败\n\n请使用文件上传功能：")
        setHasPermission(false)
        
      }
    }

    // 智能重试机制：专门处理视频播放中断问题
    const retryWithVideoFix = async () => {
      try {
        console.log("🔄 尝试修复视频播放...")
        
        // 短暂等待后重试
        await new Promise(resolve => setTimeout(resolve, 500))
        
        if (videoRef.current && scanner) {
          // 确保扫描器状态正常
          setHasPermission(true)
          console.log("✅ 视频播放修复完成")
          
          // 重新设置超时
          timeoutRef.current = setTimeout(() => {
            console.log("⏰ 扫描超时，自动关闭")
            onClose()
          }, 15000)
        }
        
      } catch (retryError) {
        console.log("❌ 视频修复失败，尝试备用配置")
        retryWithFallback()
      }
    }

    initScanner()

    // 清理函数
    return () => {
      console.log("🧹 清理扫描器资源...")
      
      // 移除视频事件监听器
      if (videoElement) {
        videoElement.removeEventListener('error', handleVideoError)
        videoElement.removeEventListener('abort', handleVideoError)
      }
      
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      if (scanner) {
        scanner.stop()
        scanner.destroy()
      }
    }
  }, [])

  const handleScanResult = (data: string) => {
    try {
      console.log("🔍 处理扫描结果:", data)
      
      // 清除超时定时器
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      
      // 停止扫描
      if (scanner) {
        scanner.stop()
      }
      
      // 检查是否是有效的URL
      const url = new URL(data)
      const cardParam = url.searchParams.get('card')
      
      if (cardParam && ['1', '2', '3', '4'].includes(cardParam)) {
        console.log("🎴 检测到有效卡牌参数:", cardParam)
        // 显示扫描成功提示
        setScanSuccess(true)
        
        // 1.5秒后打开卡牌
        setTimeout(() => {
          onScanSuccess(cardParam)
        }, 1500)
      } else {
        // 如果不是有效的卡牌链接，尝试直接跳转
        console.log("🔗 不是卡牌链接，尝试跳转:", data)
        setScanSuccess(true)
        setTimeout(() => {
          window.open(data, '_blank')
          onClose()
        }, 1500)
      }
    } catch (err) {
      console.error("❌ 解析扫描结果失败:", err)
      // 如果不是有效URL，显示扫描内容
      alert(`扫描结果: ${data}`)
      onClose()
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      console.log("📁 开始扫描文件:", file.name)
      setDebugInfo("正在扫描图片...")
      
      // 使用QrScanner扫描图片文件
      const result = await QrScanner.scanImage(file, {
        returnDetailedScanResult: true,
      })
      
      console.log("✅ 文件扫描结果:", result)
      handleScanResult(result.data)
      
    } catch (err) {
      console.error("❌ 文件扫描失败:", err)
      setError("图片中未找到二维码\n\n请确保：\n1. 图片清晰\n2. 二维码完整\n3. 选择正确的图片文件")
      
    }
  }

  const handleClose = () => {
    console.log("👋 用户关闭扫描器")
    if (scanner) {
      scanner.stop()
    }
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
      {/* 关闭按钮 */}
      <button
        onClick={handleClose}
        className="absolute top-6 right-6 text-white text-xl hover:scale-110 transition-all duration-200 z-20"
      >
        ✕ 关闭
      </button>

      {/* 扫描界面 */}
      <div className="relative w-full h-full">
        {/* 视频预览 - 全屏 */}
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          playsInline
          muted
          autoPlay={false}
          controls={false}
          preload="none"
          onLoadStart={() => console.log("📺 视频开始加载")}
          onCanPlay={() => console.log("📺 视频可以播放")}
          onPlay={() => console.log("📺 视频开始播放")}
          onPause={() => console.log("📺 视频暂停")}
          onError={(e) => console.log("📺 视频错误:", e)}
          onAbort={() => console.log("📺 视频加载中止")}
        />

        {/* 隐藏的文件输入 */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          className="hidden"
        />

        {/* 扫描成功提示 */}
        {scanSuccess && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
            <div className="bg-green-500/90 text-white p-8 rounded-lg text-center">
              <div className="text-6xl mb-4">✓</div>
              <h3 className="text-2xl font-bold mb-2">扫描成功</h3>
              <p className="text-lg">正在打开卡牌...</p>
            </div>
          </div>
        )}

        {/* 指示文字 */}
        {!scanSuccess && !error && hasPermission && (
          <div className="absolute bottom-20 left-0 right-0 text-center z-10">
            <div className="bg-black/50 backdrop-blur-sm rounded-lg mx-4 p-4">
              <h3 className="text-white text-lg font-medium mb-2">扫描二维码</h3>
              <p className="text-white/80 text-sm">
                扫描 AURA STUDIO 二维码获取专属卡牌
              </p>
            </div>
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
            <div className="bg-red-500/90 text-white p-6 rounded-lg text-center mx-4 max-w-sm">
              <p className="text-lg mb-4 whitespace-pre-line">{error}</p>
              
              {/* 文件上传按钮 */}
              {showFileUpload && (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-300 hover:scale-105 mb-3 w-full"
                >
                  📁 上传二维码图片
                </button>
              )}
              
              <button
                onClick={handleClose}
                className="bg-white/20 hover:bg-white/30 text-white border border-white/30 px-4 py-2 rounded w-full"
              >
                确定
              </button>
            </div>
          </div>
        )}

        {/* 权限请求提示 */}
        {hasPermission === null && !error && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
            <div className="text-white text-center">
              <div className="animate-spin w-12 h-12 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-lg mb-2">正在启动相机...</p>
              {debugInfo && (
                <p className="text-white/70 text-sm">{debugInfo}</p>
              )}
              <p className="text-white/50 text-xs mt-4">
                如果长时间无响应，请检查相机权限设置
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default QRScannerComponent 