"use client"

import Link from 'next/link'

export default function TestScanPage() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">
            二维码扫描测试页面
          </h1>
          <p className="text-gray-600">
            长按保存下方二维码图片，然后使用扫一扫功能上传图片测试
          </p>
          <Link 
            href="/" 
            className="inline-block mt-4 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            返回主页
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {[1, 2, 3, 4].map((cardNumber) => (
            <div key={cardNumber} className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold text-center mb-4">
                卡牌 {cardNumber} 二维码
              </h3>
              <div className="flex justify-center mb-4">
                <img 
                  src={`/qr/card${cardNumber}.png`}
                  alt={`Card ${cardNumber} QR Code`}
                  className="w-48 h-48 border border-gray-300 rounded"
                />
              </div>
              <div className="text-center text-sm text-gray-600">
                <p>扫描此二维码打开卡牌 {cardNumber}</p>
                <p className="text-xs mt-2">
                  http://localhost:3004/?card={cardNumber}
                </p>
              </div>
              
              {/* 直接访问链接按钮 */}
              <div className="mt-4 text-center">
                <a 
                  href={`/?card=${cardNumber}`}
                  className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                >
                  直接打开卡牌 {cardNumber}
                </a>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-800 mb-3">
            📝 测试说明
          </h3>
          <ol className="list-decimal list-inside text-yellow-700 space-y-2">
            <li>在手机上长按二维码图片保存到相册</li>
            <li>返回主页，点击"📱 扫一扫"按钮</li>
            <li>如果相机无法启动，点击"上传二维码图片"按钮</li>
            <li>选择刚才保存的二维码图片</li>
            <li>成功扫描后会自动打开对应的卡牌</li>
          </ol>
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-3">
            🔗 HTTPS 访问方式
          </h3>
          <div className="text-blue-700 space-y-2">
            <p><strong>当前服务地址：</strong></p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>HTTP: <code className="bg-blue-100 px-2 py-1 rounded">http://localhost:3004</code></li>
              <li>HTTPS: <code className="bg-blue-100 px-2 py-1 rounded">https://localhost:8443</code> (需要代理)</li>
            </ul>
            <p className="text-sm mt-3">
              💡 <strong>提示：</strong> 在HTTPS环境下相机功能工作更稳定
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 