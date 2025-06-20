# 🧪 AURA STUDIO Supabase 测试指南

## 📋 测试前准备

### 1. 创建 Supabase 项目

1. **访问 Supabase**
   - 前往 [https://app.supabase.com/](https://app.supabase.com/)
   - 注册或登录账户

2. **创建新项目**
   ```
   项目名称: aura-studio-test
   数据库密码: [设置一个安全密码]
   地区: 选择距离最近的地区
   ```

### 2. 获取项目配置

项目创建完成后，进入项目设置：

1. **进入 Settings > API**
2. **复制以下信息**：
   - **Project URL**: `https://your-project-id.supabase.co`
   - **API Key (anon/public)**: `eyJhbGciOi...`
   - **API Key (service_role)**: `eyJhbGciOi...` (可选)

### 3. 配置环境变量

在 `backend` 目录下创建 `.env` 文件：

```env
# Supabase 配置
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# 其他现有配置保持不变
ARK_MODEL=deepseek-r1-distill-qwen-32b-250120
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=INFO
```

## 🗄️ 创建数据库表

### 方法1：使用 Supabase SQL 编辑器

1. **进入 SQL Editor**
   - 在 Supabase 控制台左侧菜单选择 "SQL Editor"

2. **执行建表脚本**
   复制以下 SQL 并执行：

```sql
-- 1. 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. 创建用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_username_check CHECK (LENGTH(username) >= 2)
);

-- 3. 创建音轨表
CREATE TABLE audio_tracks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 创建计时器类型表
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

-- 5. 创建计时器会话表
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT timer_sessions_duration_check CHECK (
        ended_at IS NULL OR started_at < ended_at
    )
);

-- 6. 创建用户日志表
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

-- 7. 创建索引
CREATE INDEX idx_timer_sessions_user_started ON timer_sessions (user_id, started_at);
CREATE INDEX idx_timer_sessions_type ON timer_sessions (timer_type_id);
CREATE INDEX idx_user_daily_logs_date ON user_daily_logs (log_date);
CREATE INDEX idx_user_daily_logs_user_id ON user_daily_logs (user_id);
```

### 方法2：分步执行（推荐）

如果一次性执行失败，可以分步执行：

```sql
-- 步骤1: 基础设置
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

```sql
-- 步骤2: 用户表
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
```

继续执行其他表...

## 📊 插入测试数据

```sql
-- 插入音轨数据
INSERT INTO audio_tracks (name, file_path) VALUES
('定风波', '/audio/邓翊群 - 定风波.mp3'),
('Luv Sic', '/audio/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3'),
('Générique', '/audio/Miles Davis - Générique.mp3');

-- 插入计时器类型
INSERT INTO timer_types (name, display_name, default_duration, description, background_image, default_audio_track_id) VALUES
('focus', '聚焦', 5400, '聚焦光线、语言或者太空垃圾', '/images/deep-work.png', 1),
('inspire', '播种', 1800, '播种灵感、种子或者一个怪念头', '/images/break.png', 2),
('talk', '篝火', 3600, '与向导进行沉浸式对话的空间', '/images/roundtable.png', 3);
```

## 🧪 运行测试

### 1. 环境检查测试

```bash
cd backend
python quick_start_supabase.py
```

预期输出：
```
🌟 欢迎使用 AURA STUDIO Supabase 集成模块！

🔍 环境检查演示
----------------------------------------
📋 环境变量状态:
   SUPABASE_URL: ✅ 已配置 (✅ 必需)
   SUPABASE_ANON_KEY: ✅ 已配置 (✅ 必需)
   SUPABASE_SERVICE_ROLE_KEY: ✅ 已配置 (⚠️ 可选)
```

### 2. 完整功能测试

```bash
python test_supabase_integration.py
```

预期输出：
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
   - Luv Sic: /audio/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3
   - Générique: /audio/Miles Davis - Générique.mp3

🔍 正在测试用户操作...
👤 正在创建测试用户: test_20240120_143022@example.com
✅ 用户创建成功: 测试用户 (ID: a1b2c3d4...)
🔐 正在测试用户登录...
✅ 用户登录成功
✅ 错误密码正确被拒绝
✅ 根据ID获取用户成功

🔍 正在测试计时器会话...
👤 创建测试用户成功: 计时器测试用户
⏰ 正在开始计时器会话...
✅ 计时器会话开始成功: e5f6g7h8...
⏹️  正在结束计时器会话...
✅ 计时器会话结束成功
📝 获取到 1 个会话记录
   最新会话: 计划30分钟, 实际25分钟

🔍 正在测试每日日志...
👤 创建测试用户成功: 日志测试用户
📊 正在生成每日日志...
✅ 每日日志生成成功
📝 获取到 1 条日志记录
   今日统计: 3次会话, 75分钟

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

### 3. 交互式演示测试

```bash
python quick_start_supabase.py
```

输入 `y` 进行完整演示，系统会：
- 创建测试用户
- 模拟计时器会话
- 生成日志统计
- 显示完整的使用流程

## 🔍 在 Supabase 控制台验证数据

### 1. 查看数据表

在 Supabase 控制台：
1. 进入 **Table Editor**
2. 查看各个表的数据：
   - `users` - 查看创建的测试用户
   - `timer_sessions` - 查看会话记录
   - `user_daily_logs` - 查看生成的日志

### 2. 验证数据完整性

```sql
-- 查看用户数量
SELECT COUNT(*) as user_count FROM users;

-- 查看会话数据
SELECT 
    u.username,
    tt.display_name as timer_type,
    ts.planned_duration,
    ts.actual_duration,
    ts.completed,
    ts.started_at
FROM timer_sessions ts
JOIN users u ON ts.user_id = u.id
JOIN timer_types tt ON ts.timer_type_id = tt.id
ORDER BY ts.started_at DESC;

-- 查看日志统计
SELECT 
    u.username,
    dl.log_date,
    dl.total_sessions,
    dl.completed_sessions,
    dl.total_focus_time
FROM user_daily_logs dl
JOIN users u ON dl.user_id = u.id
ORDER BY dl.log_date DESC;
```

## ⚠️ 常见问题和解决方案

### 问题1: 连接超时
**症状**: `Supabase 连接健康检查失败`
**解决**:
1. 检查网络连接
2. 确认 SUPABASE_URL 格式正确
3. 验证 API Key 是否有效

### 问题2: 权限错误
**症状**: `permission denied for table users`
**解决**:
1. 确认使用了正确的 API Key
2. 检查 Supabase RLS 策略设置
3. 临时禁用 RLS 进行测试

### 问题3: 表不存在
**症状**: `relation "users" does not exist`
**解决**:
1. 确认已执行完整的建表脚本
2. 检查 SQL 执行是否成功
3. 在 Table Editor 中确认表已创建

### 问题4: 数据类型错误
**症状**: `invalid input syntax for type uuid`
**解决**:
1. 确认 uuid-ossp 扩展已启用
2. 检查 UUID 字段格式
3. 重新执行建表脚本

## 📊 性能测试（可选）

```bash
# 创建性能测试脚本
python -c "
import asyncio
import time
from supabase_integration import get_client

async def performance_test():
    client = await get_client()
    
    # 批量创建用户测试
    start_time = time.time()
    for i in range(10):
        await client.create_user(
            email=f'perf_test_{i}@example.com',
            username=f'用户{i}',
            password='test123'
        )
    end_time = time.time()
    
    print(f'创建10个用户耗时: {end_time - start_time:.2f}秒')

asyncio.run(performance_test())
"
```

## 🎯 测试成功标准

测试通过的标准：
- ✅ 所有 5 个测试模块都显示"通过"
- ✅ 能够成功创建用户和会话
- ✅ 日志统计数据正确生成
- ✅ 在 Supabase 控制台能看到测试数据
- ✅ 没有连接或权限错误

完成测试后，您就可以确信 Supabase 集成模块工作正常，可以开始在实际应用中使用了！ 🎉 