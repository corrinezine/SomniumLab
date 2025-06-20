# AURA STUDIO - Supabase 集成模块使用指南

## 📋 目录
- [模块简介](#模块简介)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [数据库设置](#数据库设置)
- [功能说明](#功能说明)
- [使用示例](#使用示例)
- [测试指南](#测试指南)
- [常见问题](#常见问题)

## 🎯 模块简介

`supabase_integration.py` 是 AURA STUDIO 项目的核心数据库集成模块，提供了与 Supabase 数据库的完整交互功能。

### 主要功能
- 🔐 **用户管理**：注册、登录、密码验证
- ⏰ **计时器会话**：开始、结束、历史记录
- 📊 **日志统计**：每日数据汇总和可视化
- 🎵 **配置管理**：音轨和计时器类型
- 🛠️ **健康检查**：连接状态监控

### 设计特点
- **简单易用**：清晰的 API 接口设计
- **类型安全**：使用 dataclass 定义数据模型
- **错误处理**：完善的异常处理和日志记录
- **异步支持**：基于 async/await 的高性能设计

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `backend` 目录下创建 `.env` 文件：

```env
# Supabase 配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# 其他配置...
```

### 3. 测试连接

```bash
cd backend
python test_supabase_integration.py
```

## ⚙️ 环境配置

### 必需的环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `SUPABASE_URL` | Supabase 项目 URL | ✅ |
| `SUPABASE_ANON_KEY` | Supabase 匿名密钥 | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase 服务角色密钥 | ⚠️ 可选 |

### 获取 Supabase 配置

1. 前往 [Supabase Dashboard](https://app.supabase.com/)
2. 选择你的项目
3. 在 **Settings** > **API** 中找到：
   - Project URL（项目 URL）
   - Project API keys（API 密钥）

## 🗄️ 数据库设置

### 创建数据库表

根据 `database.md` 文档，在 Supabase SQL 编辑器中执行以下 SQL：

```sql
-- 1. 创建用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- 2. 创建音轨表
CREATE TABLE audio_tracks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 创建计时器类型表
CREATE TABLE timer_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    default_duration INTEGER NOT NULL,
    description TEXT,
    background_image VARCHAR(500),
    default_audio_track_id INTEGER REFERENCES audio_tracks(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 创建计时器会话表
CREATE TABLE timer_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    timer_type_id INTEGER NOT NULL REFERENCES timer_types(id),
    audio_track_id INTEGER REFERENCES audio_tracks(id),
    planned_duration INTEGER NOT NULL,
    actual_duration INTEGER,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 创建用户日志表
CREATE TABLE user_daily_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    total_focus_time INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    completed_sessions INTEGER DEFAULT 0,
    deep_work_count INTEGER DEFAULT 0,
    deep_work_time INTEGER DEFAULT 0,
    break_count INTEGER DEFAULT 0,
    break_time INTEGER DEFAULT 0,
    roundtable_count INTEGER DEFAULT 0,
    roundtable_time INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT user_daily_logs_unique_user_date UNIQUE (user_id, log_date)
);
```

### 插入初始数据

```sql
-- 插入音轨数据
INSERT INTO audio_tracks (name, file_path) VALUES
('定风波', '/audio/邓翊群 - 定风波.mp3'),
('Luv Sic', '/audio/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3'),
('Générique', '/audio/Miles Davis - Générique.mp3');

-- 插入计时器类型
INSERT INTO timer_types (name, display_name, default_duration, description, background_image, default_audio_track_id) VALUES
('focus', '聚焦', 90, '聚焦光线、语言或者太空垃圾', '/images/deep-work.png', 1),
('inspire', '播种', 30, '播种灵感、种子或者一个怪念头', '/images/break.png', 2),
('talk', '篝火', 60, '与向导进行沉浸式对话的空间', '/images/roundtable.png', 3);
```

## 📚 功能说明

### 数据模型

#### User（用户）
```python
@dataclass
class User:
    id: str                    # 用户ID
    email: str                 # 邮箱
    username: str              # 用户名
    avatar_url: Optional[str]  # 头像URL
    created_at: Optional[datetime]  # 创建时间
    last_login_at: Optional[datetime]  # 最后登录时间
```

#### TimerSession（计时器会话）
```python
@dataclass
class TimerSession:
    id: str                          # 会话ID
    user_id: str                     # 用户ID
    timer_type_id: int               # 计时器类型ID
    audio_track_id: Optional[int]    # 音轨ID
    planned_duration: int            # 计划时长（秒）
    actual_duration: Optional[int]   # 实际时长（秒）
    started_at: datetime             # 开始时间
    ended_at: Optional[datetime]     # 结束时间
    completed: bool                  # 是否完成
```

#### DailyLog（每日日志）
```python
@dataclass
class DailyLog:
    id: str              # 日志ID
    user_id: str         # 用户ID
    log_date: date       # 日期
    total_focus_time: int    # 总专注时长
    total_sessions: int      # 总会话数
    completed_sessions: int  # 完成的会话数
    # ...其他统计字段
```

### 核心方法

#### 用户管理
- `create_user(email, username, password)` - 创建用户
- `authenticate_user(email, password)` - 用户登录
- `get_user_by_id(user_id)` - 获取用户信息

#### 会话管理
- `start_timer_session(user_id, timer_type_id, planned_duration, audio_track_id)` - 开始会话
- `end_timer_session(session_id, actual_duration, completed)` - 结束会话
- `get_user_sessions(user_id, limit)` - 获取会话历史

#### 日志统计
- `generate_daily_log(user_id, target_date)` - 生成每日日志
- `get_user_daily_logs(user_id, days)` - 获取日志记录

#### 配置管理
- `get_timer_types()` - 获取计时器类型
- `get_audio_tracks()` - 获取音轨列表

## 💻 使用示例

### 基本使用

```python
import asyncio
from supabase_integration import get_client

async def example():
    # 获取客户端
    client = await get_client()
    
    # 创建用户
    user = await client.create_user(
        email="user@example.com",
        username="新用户",
        password="secure_password"
    )
    
    if user:
        print(f"用户创建成功: {user.username}")
        
        # 开始计时器会话
        session_id = await client.start_timer_session(
            user_id=user.id,
            timer_type_id=1,  # 聚焦模式
            planned_duration=90 * 60  # 90分钟
        )
        
        # 模拟会话结束
        if session_id:
            await client.end_timer_session(
                session_id=session_id,
                actual_duration=85 * 60,  # 实际85分钟
                completed=True
            )
            
            # 生成每日日志
            await client.generate_daily_log(user.id)
            
            # 查看日志
            logs = await client.get_user_daily_logs(user.id)
            for log in logs:
                print(f"日期: {log.log_date}, 专注时长: {log.total_focus_time//60}分钟")

# 运行示例
asyncio.run(example())
```

### FastAPI 集成示例

```python
from fastapi import FastAPI, HTTPException
from supabase_integration import get_client

app = FastAPI()

@app.post("/api/users/register")
async def register_user(email: str, username: str, password: str):
    client = await get_client()
    user = await client.create_user(email, username, password)
    
    if user:
        return {"success": True, "user_id": user.id}
    else:
        raise HTTPException(status_code=400, detail="用户创建失败")

@app.post("/api/timer/start")
async def start_timer(user_id: str, timer_type_id: int, planned_duration: int):
    client = await get_client()
    session_id = await client.start_timer_session(
        user_id, timer_type_id, planned_duration
    )
    
    if session_id:
        return {"success": True, "session_id": session_id}
    else:
        raise HTTPException(status_code=400, detail="启动计时器失败")
```

## 🧪 测试指南

### 运行完整测试

```bash
cd backend
python test_supabase_integration.py
```

### 测试内容

测试脚本会验证以下功能：

1. **连接测试** - 验证 Supabase 连接是否正常
2. **配置数据测试** - 检查计时器类型和音轨数据
3. **用户操作测试** - 用户注册、登录、验证
4. **计时器会话测试** - 会话的创建和管理
5. **每日日志测试** - 日志生成和统计功能

### 预期输出

```
🚀 开始 AURA STUDIO Supabase 集成测试
==================================================
✅ 环境变量配置检查通过

🔍 正在测试 Supabase 连接...
✅ Supabase 连接成功！

🔍 正在测试配置数据获取...
📊 找到 3 种计时器类型:
   - 聚焦: 聚焦光线、语言或者太空垃圾
   - 播种: 播种灵感、种子或者一个怪念头
   - 篝火: 与向导进行沉浸式对话的空间
🎵 找到 3 个音轨:
   - 定风波: /audio/邓翊群 - 定风波.mp3
   ...

==================================================
📊 测试结果汇总:
   连接测试: ✅ 通过
   配置数据测试: ✅ 通过
   用户操作测试: ✅ 通过
   计时器会话测试: ✅ 通过
   每日日志测试: ✅ 通过

🎯 总计: 5/5 个测试通过
🎉 所有测试通过！Supabase 集成模块工作正常
```

## ❓ 常见问题

### Q: 如何解决连接超时问题？
A: 检查以下几点：
1. 确认 Supabase 项目状态正常
2. 检查网络连接
3. 验证 URL 和密钥是否正确
4. 查看 Supabase 项目的用量限制

### Q: 用户创建失败怎么办？
A: 可能的原因：
1. 邮箱已经存在
2. 数据库表未正确创建
3. RLS 策略配置问题
4. 密码格式不符合要求

### Q: 会话数据无法保存？
A: 检查：
1. 用户是否存在
2. timer_type_id 是否有效
3. 数据库约束是否满足
4. 权限设置是否正确

### Q: 如何启用调试模式？
A: 在代码中添加：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Q: 性能优化建议？
A: 考虑以下优化：
1. 使用连接池
2. 批量操作替代单次操作
3. 合理使用索引
4. 定期清理历史数据

## 📞 技术支持

如果您在使用过程中遇到问题，请：

1. 检查本文档的常见问题部分
2. 运行测试脚本诊断问题
3. 查看日志输出定位具体错误
4. 参考 Supabase 官方文档

## 🎉 总结

恭喜！您现在已经成功配置了 AURA STUDIO 的 Supabase 集成模块。这个模块为您的应用提供了：

- ✅ 完整的用户管理系统
- ✅ 灵活的计时器会话管理
- ✅ 强大的数据统计功能
- ✅ 易于扩展的架构设计

开始使用这个模块来构建您的灵韵工作间吧！ 🚀✨ 