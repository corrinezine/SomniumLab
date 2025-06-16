/** @type {import('next').NextConfig} */
const nextConfig = {
  // 开发环境配置
  experimental: {
    // 其他实验性功能
  },
  // 生产环境会自动使用HTTPS，这里配置开发环境
  async rewrites() {
    return []
  },
}

module.exports = nextConfig 