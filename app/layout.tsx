import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { ClientAuthHeader } from '@/components/auth/AuthHeader'
import { Toaster } from 'sonner'

export const metadata: Metadata = {
  title: 'AURA STUDIO - 灵韵工作室',
  description: '沉浸式灵感启发和创作体验平台',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <AuthProvider>
          {/* 🎯 全局认证头部 */}
          <ClientAuthHeader />
          {/* 📄 页面内容 */}
          {children}
          {/* Toast 通知 */}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  )
}
