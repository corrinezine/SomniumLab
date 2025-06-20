# AURA STUDIO - Supabase 权限问题解决指南

## 🔍 问题诊断

从测试结果可以看出：
- ✅ Supabase 连接正常
- ✅ 数据库表存在（users, user_logs, profiles, sessions）
- ❌ 权限不足："User not allowed" 错误

## 🛠️ 解决方案

### 方案 1：在 Supabase 控制台中设置数据库

1. **登录 Supabase 控制台**
   - 访问：https://supabase.com/dashboard
   - 选择您的项目：`jdyogivzmzwdtmcgxdas`

2. **执行数据库设置脚本**
   - 进入 `SQL Editor`
   - 复制 `database-setup.sql` 文件中的内容
   - 粘贴并执行脚本

3. **验证表结构**
   - 进入 `Table Editor`
   - 确认以下表已创建：
     - `profiles` - 用户档案表
     - `user_logs` - 用户日志表

### 方案 2：手动配置权限

#### 2.1 禁用 RLS（临时测试用）
```sql
-- 临时禁用行级安全以进行测试
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_logs DISABLE ROW LEVEL SECURITY;
```

#### 2.2 或者创建正确的 RLS 策略
```sql
-- 为已认证用户创建访问策略
CREATE POLICY "authenticated_users_profiles" ON profiles
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "authenticated_users_logs" ON user_logs
  FOR ALL USING (auth.role() = 'authenticated');
```

### 方案 3：使用 Service Role Key（仅用于服务器端）

如果需要管理员权限，需要：
1. 在 Supabase 控制台获取 `Service Role Key`
2. 在后端代码中使用（**不要在前端使用**）

## 🧪 测试步骤

### 步骤 1：基础测试
1. 访问：http://localhost:3000/debug-auth
2. 点击"测试连接"确保连接正常
3. 点击"📊 检查表结构"查看当前状态

### 步骤 2：用户认证测试
1. 点击"测试注册"创建新用户
2. 点击"测试登录"验证登录功能
3. 点击"检查会话"确认会话状态

### 步骤 3：权限诊断
1. 确保已登录用户
2. 点击"🔐 权限诊断"进行详细权限检查
3. 根据诊断结果调整数据库配置

### 步骤 4：日志记录测试
1. 点击"📝 测试日志记录"验证日志功能
2. 检查是否能成功插入和查询日志

## 🔧 常见问题解决

### 问题 1：表不存在
**症状**：`relation "table_name" does not exist`
**解决**：执行 `database-setup.sql` 脚本创建表

### 问题 2：权限不足
**症状**：`permission denied` 或 `User not allowed`
**解决**：
1. 检查 RLS 策略是否正确
2. 确保用户已登录
3. 验证 API Key 配置

### 问题 3：RLS 策略阻止访问
**症状**：查询返回空结果或权限错误
**解决**：
1. 临时禁用 RLS 进行测试
2. 创建适当的 RLS 策略
3. 确保策略条件正确

## 📋 建议的数据库表结构

### profiles 表
```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  username TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### user_logs 表
```sql
CREATE TABLE user_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  action TEXT NOT NULL,
  details JSONB,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔐 安全最佳实践

1. **启用 RLS**：所有表都应启用行级安全
2. **最小权限原则**：只授予必要的权限
3. **API Key 安全**：
   - 前端只使用 Anon Key
   - 后端可使用 Service Role Key
   - 永远不要在前端暴露 Service Role Key

## 📞 获取帮助

如果问题仍然存在：
1. 检查 Supabase 项目设置
2. 查看 Supabase 日志
3. 参考 Supabase 官方文档
4. 使用"🔐 权限诊断"功能获取详细错误信息

## 🎯 下一步

完成数据库设置后：
1. 重新运行所有测试
2. 验证用户注册/登录流程
3. 确认日志记录功能正常
4. 部署到生产环境前再次测试 