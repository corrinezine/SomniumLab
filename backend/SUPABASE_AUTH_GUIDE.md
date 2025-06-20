# 🔐 AURA STUDIO Supabase 认证集成使用指南

## 📖 概述

本指南将详细介绍如何使用 AURA STUDIO 项目中集成的 Supabase 用户认证功能。该认证系统提供了完整的前后端一体化解决方案，包括用户注册、登录、JWT Token 验证等功能。

---

## 🏗️ 系统架构

### 认证流程图
```
前端 (Next.js) ←→ Supabase Auth ←→ 后端 (FastAPI)
     ↓                ↓               ↓
  用户界面        JWT Token        数据验证
  状态管理        自动刷新        权限控制
```

### 核心组件
1. **前端认证提供者** (`components/auth/AuthProvider.tsx`)
2. **登录表单组件** (`components/auth/LoginForm.tsx`)
3. **后端认证模块** (`backend/supabase_auth.py`)
4. **受保护路由** (`backend/protected_routes.py`)
5. **API 客户端** (`lib/api-client.ts`)

---

## 🚀 快速开始

### 1. 环境配置

#### 后端环境变量 (`backend/.env`)
```bash
# Supabase 配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret

# 其他配置...
```

#### 前端环境变量 (根目录 `.env.local`)
```bash
# Supabase 配置
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# API 配置
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. 启动服务

#### 后端服务
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端服务
```bash
npm run dev
# 或
pnpm dev
```

### 3. 访问测试页面
打开浏览器访问：`http://localhost:3000/auth-test`

---

## 💻 前端使用指南

### 基础使用

#### 1. 包装应用程序
```tsx
// app/layout.tsx 或其他根组件
import { AuthProvider } from '@/components/auth/AuthProvider'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
```

#### 2. 使用认证状态
```tsx
import { useAuth } from '@/components/auth/AuthProvider'

function MyComponent() {
  const { user, loading, signIn, signOut } = useAuth()

  if (loading) return <div>加载中...</div>
  
  if (!user) {
    return <div>请先登录</div>
  }

  return (
    <div>
      <h1>欢迎，{user.email}!</h1>
      <button onClick={signOut}>登出</button>
    </div>
  )
}
```

#### 3. 受保护的页面
```tsx
import { ProtectedRoute } from '@/components/auth/AuthProvider'
import { LoginForm } from '@/components/auth/LoginForm'

export default function ProtectedPage() {
  return (
    <ProtectedRoute 
      fallback={<LoginForm />}
    >
      <div>这是受保护的内容</div>
    </ProtectedRoute>
  )
}
```

### 高级使用

#### 1. 调用受保护的 API
```tsx
import { useAuthenticatedApi } from '@/lib/api-client'

function Dashboard() {
  const api = useAuthenticatedApi()
  
  const loadUserData = async () => {
    try {
      // 自动添加认证头
      const profile = await api.getUserProfile()
      const sessions = await api.getTimerSessions()
      
      console.log('用户资料:', profile)
      console.log('计时器会话:', sessions)
    } catch (error) {
      console.error('加载失败:', error)
    }
  }

  return (
    <div>
      <button onClick={loadUserData}>加载数据</button>
    </div>
  )
}
```

#### 2. 手动验证 Token
```tsx
import { useAuth } from '@/components/auth/AuthProvider'

function TokenInfo() {
  const { token, user } = useAuth()
  
  const checkToken = async () => {
    if (!token) {
      console.log('没有 Token')
      return
    }
    
    // 手动验证 Token
    const response = await fetch('/api/health/auth', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      console.log('Token 有效')
    } else {
      console.log('Token 无效')
    }
  }

  return (
    <div>
      <p>Token: {token ? '存在' : '不存在'}</p>
      <button onClick={checkToken}>验证 Token</button>
    </div>
  )
}
```

---

## 🔧 后端使用指南

### 创建受保护的路由

#### 1. 基础认证路由
```python
from fastapi import APIRouter, Depends
from supabase_auth import get_current_user, AuthenticatedUser

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """需要认证的端点"""
    return {
        "message": f"Hello {current_user.email}!",
        "user_id": current_user.user_id
    }
```

#### 2. 可选认证路由
```python
from supabase_auth import get_optional_user

@router.get("/optional-auth")
async def optional_auth_endpoint(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """可选认证的端点"""
    if current_user:
        return {"message": f"认证用户: {current_user.email}"}
    else:
        return {"message": "匿名访问"}
```

#### 3. 手动验证 Token
```python
from supabase_auth import supabase_auth

@router.post("/manual-verify")
async def manual_verify(request: Request):
    """手动验证 Token"""
    # 从请求头获取 Token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(401, "缺少认证头")
    
    token = supabase_auth.extract_token_from_header(auth_header)
    if not token:
        raise HTTPException(401, "Token 格式错误")
    
    user = supabase_auth.verify_token(token)
    if not user:
        raise HTTPException(401, "Token 无效")
    
    return {"user": user.dict()}
```

### 集成数据库操作

#### 1. 用户相关操作
```python
from supabase_integration import get_client

@router.get("/user-sessions")
async def get_user_sessions(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取用户的计时器会话"""
    client = await get_client()
    sessions = await client.get_user_sessions(current_user.user_id)
    
    return {"sessions": sessions}

@router.post("/start-session")
async def start_timer_session(
    session_data: dict,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """开始新的计时器会话"""
    client = await get_client()
    session_id = await client.start_timer_session(
        user_id=current_user.user_id,
        **session_data
    )
    
    return {"session_id": session_id}
```

---

## 🛠️ 常见使用场景

### 1. 用户注册登录流程

#### 前端实现
```tsx
import { useAuth } from '@/components/auth/AuthProvider'

function AuthFlow() {
  const { signUp, signIn, user } = useAuth()
  
  const handleRegister = async (email: string, password: string) => {
    const result = await signUp(email, password)
    
    if (result.success) {
      if (result.needsEmailConfirmation) {
        alert('请查看邮箱确认注册')
      } else {
        alert('注册成功!')
      }
    } else {
      alert(`注册失败: ${result.error}`)
    }
  }
  
  const handleLogin = async (email: string, password: string) => {
    const result = await signIn(email, password)
    
    if (result.success) {
      alert('登录成功!')
    } else {
      alert(`登录失败: ${result.error}`)
    }
  }
  
  return (
    <div>
      {user ? (
        <p>已登录: {user.email}</p>
      ) : (
        <div>
          <button onClick={() => handleRegister('test@example.com', 'password123')}>
            测试注册
          </button>
          <button onClick={() => handleLogin('test@example.com', 'password123')}>
            测试登录
          </button>
        </div>
      )}
    </div>
  )
}
```

### 2. 计时器会话管理

#### 前端组件
```tsx
import { useAuthenticatedApi } from '@/lib/api-client'

function TimerManager() {
  const api = useAuthenticatedApi()
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  
  const startSession = async () => {
    const response = await api.startTimerSession({
      timer_type_id: 1,
      planned_duration: 90,
      audio_track_id: 1
    })
    
    if (response.success) {
      setCurrentSession(response.data)
      alert('会话开始!')
    }
  }
  
  const endSession = async (sessionId: string, actualDuration: number) => {
    const response = await api.endTimerSession(sessionId, {
      actual_duration: actualDuration,
      completed: true
    })
    
    if (response.success) {
      setCurrentSession(null)
      loadSessions() // 重新加载会话列表
      alert('会话结束!')
    }
  }
  
  const loadSessions = async () => {
    const response = await api.getTimerSessions(10)
    if (response.success) {
      setSessions(response.data.sessions)
    }
  }
  
  return (
    <div>
      <button onClick={startSession}>开始计时</button>
      <div>
        <h3>历史会话</h3>
        {sessions.map(session => (
          <div key={session.id}>
            会话 {session.id}: {session.planned_duration}分钟
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 3. 每日统计查看

#### 前端组件
```tsx
function DailyStats() {
  const api = useAuthenticatedApi()
  const [logs, setLogs] = useState([])
  
  useEffect(() => {
    loadDailyLogs()
  }, [])
  
  const loadDailyLogs = async () => {
    const response = await api.getDailyLogs(7) // 最近7天
    if (response.success) {
      setLogs(response.data.logs)
    }
  }
  
  return (
    <div>
      <h3>每日统计</h3>
      {logs.map(log => (
        <div key={log.log_date} className="stat-card">
          <h4>{log.log_date}</h4>
          <p>总会话: {log.total_sessions}次</p>
          <p>完成: {log.completed_sessions}次</p>
          <p>总时长: {Math.round(log.total_focus_time / 60)}小时</p>
          <p>聚焦: {log.deep_work_count}次</p>
          <p>播种: {log.break_count}次</p>
          <p>篝火: {log.roundtable_count}次</p>
        </div>
      ))}
    </div>
  )
}
```

---

## 🔍 调试和测试

### 1. 检查认证状态
```tsx
import { useAuth } from '@/components/auth/AuthProvider'

function AuthDebug() {
  const { user, session, token, loading } = useAuth()
  
  return (
    <div>
      <h3>认证调试信息</h3>
      <p>加载状态: {loading ? '是' : '否'}</p>
      <p>用户存在: {user ? '是' : '否'}</p>
      <p>会话存在: {session ? '是' : '否'}</p>
      <p>Token 存在: {token ? '是' : '否'}</p>
      
      {user && (
        <div>
          <h4>用户信息</h4>
          <pre>{JSON.stringify(user, null, 2)}</pre>
        </div>
      )}
      
      {token && (
        <div>
          <h4>Token 信息</h4>
          <p>Token 长度: {token.length}</p>
          <p>Token 前缀: {token.substring(0, 20)}...</p>
        </div>
      )}
    </div>
  )
}
```

### 2. 测试 API 连接
```tsx
function ApiTest() {
  const api = useAuthenticatedApi()
  
  const testApis = async () => {
    console.log('=== API 测试开始 ===')
    
    try {
      // 测试认证健康检查
      const health = await api.checkAuthHealth()
      console.log('认证健康检查:', health)
      
      // 测试获取用户资料
      const profile = await api.getUserProfile()
      console.log('用户资料:', profile)
      
      // 测试获取计时器类型
      const timerTypes = await api.getTimerTypes()
      console.log('计时器类型:', timerTypes)
      
      console.log('=== API 测试完成 ===')
    } catch (error) {
      console.error('API 测试失败:', error)
    }
  }
  
  return (
    <button onClick={testApis}>测试 API 连接</button>
  )
}
```

---

## ⚠️ 常见问题和解决方案

### 1. Token 验证失败
**问题**: `JWT Token 无效` 或 `401 Unauthorized`

**可能原因**:
- JWT Secret 配置错误
- Token 已过期
- Token 格式不正确

**解决方案**:
```bash
# 检查环境变量
echo $SUPABASE_JWT_SECRET

# 重新获取 Token
# 前端清除本地存储后重新登录
localStorage.removeItem('supabase_token')
```

### 2. CORS 错误
**问题**: 前端无法访问后端 API

**解决方案**:
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 确保包含前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 认证状态不同步
**问题**: 前端认证状态与后端不一致

**解决方案**:
```tsx
// 手动刷新认证状态
const { refreshToken } = useAuth()
await refreshToken()

// 或重新验证 Token
const api = useAuthenticatedApi()
const health = await api.checkAuthHealth()
```

### 4. 环境变量缺失
**问题**: `缺少 SUPABASE_JWT_SECRET 环境变量`

**解决方案**:
1. 检查 `.env` 文件是否存在
2. 确认环境变量名称正确
3. 重启后端服务

---

## 📚 API 参考

### 认证相关端点

| 端点 | 方法 | 描述 | 认证要求 |
|------|------|------|----------|
| `/api/profile` | GET | 获取用户资料 | 必须 |
| `/api/health/auth` | GET | 认证健康检查 | 必须 |
| `/api/timer/sessions` | GET | 获取用户会话 | 必须 |
| `/api/timer/start` | POST | 开始计时器会话 | 必须 |
| `/api/timer/sessions/{id}/end` | PATCH | 结束计时器会话 | 必须 |
| `/api/logs/daily` | GET | 获取每日日志 | 必须 |
| `/api/config/timer-types` | GET | 获取计时器类型 | 可选 |

### 前端 Hook 和组件

| 名称 | 类型 | 描述 |
|------|------|------|
| `useAuth()` | Hook | 获取认证状态和方法 |
| `useAuthenticatedApi()` | Hook | 获取认证 API 客户端 |
| `AuthProvider` | 组件 | 认证状态提供者 |
| `ProtectedRoute` | 组件 | 受保护路由包装器 |
| `LoginForm` | 组件 | 登录注册表单 |

---

## 🎯 总结

AURA STUDIO 的 Supabase 认证集成提供了完整的用户认证解决方案：

1. **前端**: React Context + Supabase Auth SDK
2. **后端**: FastAPI + JWT 验证
3. **数据库**: Supabase 用户表 + 自定义业务表
4. **安全**: JWT Token + RLS 策略

这个系统确保了：
- 🔐 安全的用户认证
- 🔄 自动 Token 刷新
- 🛡️ 受保护的 API 端点
- 📱 响应式用户界面
- 🚀 易于扩展和维护

现在您可以开始在 AURA STUDIO 项目中使用完整的用户认证功能了！ 