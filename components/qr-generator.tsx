"use client"

import { useState, useEffect } from "react"
import QRCode from "qrcode"
import { Button } from "@/components/ui/button"

interface QRCodeData {
  id: number
  name: string
  url: string
  qrCodeDataURL: string
}

const QRGenerator = () => {
  const [qrCodes, setQRCodes] = useState<QRCodeData[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  // 获取当前域名
  const getBaseURL = () => {
    if (typeof window !== 'undefined') {
      return window.location.origin
    }
    return 'http://localhost:3000' // 开发环境默认值
  }

  // 生成二维码
  const generateQRCodes = async () => {
    setIsGenerating(true)
    const baseURL = getBaseURL()
    
    const cardNames = ['梦境向导1', '梦境向导2', '梦境向导3', '梦境向导4']
    const newQRCodes: QRCodeData[] = []

    try {
      for (let i = 1; i <= 4; i++) {
        const url = `${baseURL}/?card=${i}`
        const qrCodeDataURL = await QRCode.toDataURL(url, {
          width: 300,
          margin: 2,
          color: {
            dark: '#000000',
            light: '#FFFFFF'
          }
        })

        newQRCodes.push({
          id: i,
          name: cardNames[i - 1],
          url: url,
          qrCodeDataURL: qrCodeDataURL
        })
      }

      setQRCodes(newQRCodes)
    } catch (error) {
      console.error('生成二维码失败:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  // 下载二维码
  const downloadQRCode = (qrCode: QRCodeData) => {
    const link = document.createElement('a')
    link.download = `aura-studio-card-${qrCode.id}-qr.png`
    link.href = qrCode.qrCodeDataURL
    link.click()
  }

  // 下载所有二维码
  const downloadAllQRCodes = () => {
    qrCodes.forEach((qrCode, index) => {
      setTimeout(() => {
        downloadQRCode(qrCode)
      }, index * 500) // 延迟下载避免浏览器阻止
    })
  }

  // 复制链接到剪贴板
  const copyToClipboard = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url)
      alert('链接已复制到剪贴板!')
    } catch (error) {
      console.error('复制失败:', error)
      alert('复制失败，请手动复制链接')
    }
  }

  useEffect(() => {
    generateQRCodes()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">AURA STUDIO 二维码管理</h1>
          <p className="text-purple-200 text-lg">
            扫描以下二维码，直接打开对应的梦境卡牌
          </p>
        </div>

        <div className="flex justify-center mb-8">
          <div className="flex gap-4">
            <Button
              onClick={generateQRCodes}
              disabled={isGenerating}
              className="bg-purple-600 hover:bg-purple-700 px-6 py-3"
            >
              {isGenerating ? '生成中...' : '重新生成二维码'}
            </Button>
            
            {qrCodes.length > 0 && (
              <Button
                onClick={downloadAllQRCodes}
                className="bg-indigo-600 hover:bg-indigo-700 px-6 py-3"
              >
                下载所有二维码
              </Button>
            )}
          </div>
        </div>

        {/* 二维码网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {qrCodes.map((qrCode) => (
            <div
              key={qrCode.id}
              className="bg-white/10 backdrop-blur-sm rounded-lg p-6 text-center border border-white/20"
            >
              <h3 className="text-xl font-semibold mb-4 text-purple-200">
                {qrCode.name}
              </h3>
              
              {/* 二维码图片 */}
              <div className="bg-white rounded-lg p-4 mb-4 inline-block">
                <img
                  src={qrCode.qrCodeDataURL}
                  alt={`${qrCode.name} 二维码`}
                  className="w-48 h-48 mx-auto"
                />
              </div>

              {/* 链接显示 */}
              <div className="mb-4">
                <p className="text-sm text-purple-300 mb-2">扫描链接:</p>
                <div className="bg-black/20 rounded px-3 py-2 text-xs break-all">
                  {qrCode.url}
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex flex-col gap-2">
                <Button
                  onClick={() => downloadQRCode(qrCode)}
                  className="bg-green-600 hover:bg-green-700 text-sm"
                >
                  下载二维码
                </Button>
                <Button
                  onClick={() => copyToClipboard(qrCode.url)}
                  className="bg-blue-600 hover:bg-blue-700 text-sm"
                >
                  复制链接
                </Button>
                <Button
                  onClick={() => window.open(qrCode.url, '_blank')}
                  className="bg-purple-600 hover:bg-purple-700 text-sm"
                >
                  测试链接
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* 使用说明 */}
        <div className="mt-12 bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
          <h2 className="text-2xl font-semibold mb-4 text-center">使用说明</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-purple-200">
            <div>
              <h3 className="text-lg font-medium mb-2">🎯 功能说明</h3>
              <ul className="space-y-1 text-sm">
                <li>• 每个二维码对应一张梦境卡牌</li>
                <li>• 扫描后直接打开对应卡牌弹窗</li>
                <li>• 查看完卡牌后返回主页</li>
                <li>• 支持卡牌翻转查看正反面</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-medium mb-2">📱 使用方法</h3>
              <ul className="space-y-1 text-sm">
                <li>• 下载二维码图片并打印</li>
                <li>• 用户使用手机扫描二维码</li>
                <li>• 自动跳转到对应卡牌页面</li>
                <li>• 点击卡牌可以翻转查看内容</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default QRGenerator 