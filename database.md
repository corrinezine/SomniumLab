# AURA STUDIO 数据库设计文档

## 一、核心表设计

基于PRD需求，设计以下**5个核心表**支持AURA STUDIO MVP功能：

| 表名 | 作用 | 关键功能 |
|------|------|----------|
| `users` | 用户管理 | 用户注册、登录 |
| `timer_types` | 计时器类型 | 三种计时器配置 |
| `audio_tracks` | 音轨管理 | 背景音乐存储 |
| `timer_sessions` | 计时器会话 | **核心表**：记录使用详情 |
| `user_daily_logs` | 用户日志 | 每日数据汇总 |

## 二、简化表结构

### 2.1 用户表 (users)
```sql
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

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2.2 音轨表 (audio_tracks) - 简化版
```sql
CREATE TABLE audio_tracks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 只插入实际存在的音频文件
INSERT INTO audio_tracks (name, file_path) VALUES
('定风波', '/audio/邓翊群 - 定风波.mp3'),
('Luv Sic', '/audio/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3'),
('Générique', '/audio/Miles Davis - Générique.mp3');
```

### 2.3 计时器类型表 (timer_types) - 简化版
```sql
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

-- 插入三种计时器类型
INSERT INTO timer_types (name, display_name, default_duration, description, background_image, default_audio_track_id) VALUES
('focus', '聚焦', 90, '聚焦光线、语言或者太空垃圾', '/images/deep-work.png', 1),
('inspire', '播种', 30, '播种灵感、种子或者一个怪念头', '/images/break.png', 2),
('talk', '篝火', 60, '与向导进行沉浸式对话的空间', '/images/roundtable.png', 3);
```

### 2.4 计时器会话表 (timer_sessions) - 简化版
```sql
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
    ),
    CONSTRAINT timer_sessions_completion_check CHECK (
        (completed = FALSE) OR (completed = TRUE AND ended_at IS NOT NULL)
    )
);

-- 关键索引 (避免使用函数表达式)
CREATE INDEX idx_timer_sessions_user_started ON timer_sessions (user_id, started_at);
CREATE INDEX idx_timer_sessions_type ON timer_sessions (timer_type_id);
```

### 2.5 用户日志表 (user_daily_logs)
```sql
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
    
    CONSTRAINT user_daily_logs_sessions_check CHECK (completed_sessions <= total_sessions),
    CONSTRAINT user_daily_logs_unique_user_date UNIQUE (user_id, log_date)
);

-- 创建索引
CREATE INDEX idx_user_daily_logs_date ON user_daily_logs (log_date);
CREATE INDEX idx_user_daily_logs_user_id ON user_daily_logs (user_id);

-- 创建更新时间触发器
CREATE TRIGGER update_user_daily_logs_updated_at 
    BEFORE UPDATE ON user_daily_logs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```



## 三、简化的存储过程

### 3.1 每日日志汇总函数
```sql
CREATE OR REPLACE FUNCTION generate_daily_log(target_user_id UUID, target_date DATE)
RETURNS VOID AS $$
DECLARE
    session_stats RECORD;
BEGIN
    -- 计算当日统计数据
    SELECT 
        COUNT(*) as total_sessions,
        COUNT(*) FILTER (WHERE completed = TRUE) as completed_sessions,
        COALESCE(SUM(actual_duration) FILTER (WHERE completed = TRUE), 0) as total_focus_time,
        COUNT(*) FILTER (WHERE tt.name = 'focus') as deep_work_count,
        COALESCE(SUM(actual_duration) FILTER (WHERE tt.name = 'focus' AND completed = TRUE), 0) as deep_work_time,
        COUNT(*) FILTER (WHERE tt.name = 'inspire') as break_count,
        COALESCE(SUM(actual_duration) FILTER (WHERE tt.name = 'inspire' AND completed = TRUE), 0) as break_time,
        COUNT(*) FILTER (WHERE tt.name = 'talk') as roundtable_count,
        COALESCE(SUM(actual_duration) FILTER (WHERE tt.name = 'talk' AND completed = TRUE), 0) as roundtable_time
    INTO session_stats
    FROM timer_sessions ts
    JOIN timer_types tt ON ts.timer_type_id = tt.id
    WHERE ts.user_id = target_user_id 
      AND DATE(ts.started_at) = target_date;

    -- 插入或更新日志记录
    INSERT INTO user_daily_logs (
        user_id, log_date, total_focus_time, total_sessions, completed_sessions,
        deep_work_count, deep_work_time, break_count, break_time, 
        roundtable_count, roundtable_time
    ) VALUES (
        target_user_id, target_date, session_stats.total_focus_time, 
        session_stats.total_sessions, session_stats.completed_sessions,
        session_stats.deep_work_count, session_stats.deep_work_time,
        session_stats.break_count, session_stats.break_time,
        session_stats.roundtable_count, session_stats.roundtable_time
    )
    ON CONFLICT (user_id, log_date) 
    DO UPDATE SET
        total_focus_time = EXCLUDED.total_focus_time,
        total_sessions = EXCLUDED.total_sessions,
        completed_sessions = EXCLUDED.completed_sessions,
        deep_work_count = EXCLUDED.deep_work_count,
        deep_work_time = EXCLUDED.deep_work_time,
        break_count = EXCLUDED.break_count,
        break_time = EXCLUDED.break_time,
        roundtable_count = EXCLUDED.roundtable_count,
        roundtable_time = EXCLUDED.roundtable_time,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
```



## 四、RLS (行级安全) 策略

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 启用RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE timer_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_daily_logs ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的数据
CREATE POLICY "用户只能查看自己的信息" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "用户只能更新自己的信息" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "用户只能查看自己的会话" ON timer_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "用户只能创建自己的会话" ON timer_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "用户只能更新自己的会话" ON timer_sessions FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "用户只能查看自己的日志" ON user_daily_logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "用户只能创建自己的日志" ON user_daily_logs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "用户只能更新自己的日志" ON user_daily_logs FOR UPDATE USING (auth.uid() = user_id);

-- 公共数据表允许所有认证用户读取
CREATE POLICY "所有用户可查看计时器类型" ON timer_types FOR SELECT TO authenticated USING (true);
CREATE POLICY "所有用户可查看音轨" ON audio_tracks FOR SELECT TO authenticated USING (true);
```

## 五、前端可视化配置

将复杂的模板配置移到前端代码中：

```typescript
// 前端配置文件 - timerConfig.ts
export const TIMER_CONFIG = {
  types: {
    focus: {
      icon: '🔥',
      name: '聚焦',
      description: '聚焦光线、语言或者太空垃圾'
    },
    inspire: {
      icon: '⭐',
      name: '播种',
      description: '播种灵感、种子或者一个怪念头'
    },
    talk: {
      icon: '🌙',
      name: '篝火',
      description: '与向导进行沉浸式对话的空间'
    }
  },
  colors: {
    primary: '#2D1B69',
    secondary: '#4A90E2',
    accent: '#8E6A5B'
  }
};
```

## 六、使用示例

### 6.1 生成每日日志
```sql
-- 为用户生成今日日志
SELECT generate_daily_log(
    'user-uuid-here'::UUID, 
    CURRENT_DATE
);
```

### 6.2 查询每日统计
```sql
-- 查询用户本周专注时长
SELECT 
    log_date,
    total_focus_time,
    total_sessions
FROM user_daily_logs 
WHERE user_id = $1 
  AND log_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY log_date DESC;
```

## 七、简化设计优势

### 已移除的复杂功能：
1. ❌ `visualization_templates` 表 - 完全删除
2. ❌ 复杂的JSONB字段 - 简化为基础字段
3. ❌ 过度的生产力等级系统 - 简化为基础成就
4. ❌ 不必要的音轨分类 - 只保留核心音轨
5. ❌ 复杂的一致性评分算法 - 简化为直观计数
6. ❌ 过多的索引 - 只保留关键索引

### MVP核心功能：
1. ✅ 用户注册登录
2. ✅ 三种计时器类型：聚焦(focus)、播种(inspire)、篝火(talk)
3. ✅ 基础音轨选择
4. ✅ 会话记录追踪
5. ✅ 每日数据汇总与日志卡片

## 八、实施建议

1. **先部署简化版**：快速上线核心功能
2. **逐步迭代**：根据用户反馈添加功能
3. **数据驱动**：基于实际使用数据决定是否需要复杂功能
4. **保持简洁**：MVP阶段避免过度设计

## 九、后续规划 - 周报可视化系统

### 9.1 用户周报表 (user_weekly_reports)

**功能说明**：存储每周可视化报告数据，支持灵韵之旅的周度回顾

```sql
CREATE TABLE user_weekly_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    focus_lights INTEGER DEFAULT 0,      -- 聚焦次数 🔥
    inspire_stars INTEGER DEFAULT 0,     -- 播种次数 ⭐
    talk_moons INTEGER DEFAULT 0,        -- 篝火次数 🌙
    weekly_achievement TEXT,             -- 周成就描述
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT weekly_reports_date_check CHECK (week_start_date <= week_end_date),
    CONSTRAINT weekly_reports_unique_user_week UNIQUE (user_id, week_start_date)
);

CREATE INDEX idx_weekly_reports_user_week ON user_weekly_reports (user_id, week_start_date);

-- RLS策略
ALTER TABLE user_weekly_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "用户只能查看自己的周报" ON user_weekly_reports FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "用户只能创建自己的周报" ON user_weekly_reports FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### 9.2 周报生成函数

```sql
CREATE OR REPLACE FUNCTION generate_weekly_report(target_user_id UUID, target_week_start DATE)
RETURNS UUID AS $$
DECLARE
    report_id UUID;
    week_end_date DATE;
    focus_count INTEGER;
    inspire_count INTEGER;
    talk_count INTEGER;
    achievement_text TEXT;
BEGIN
    week_end_date := target_week_start + INTERVAL '6 days';
    
    -- 计算周统计数据
    SELECT 
        COUNT(*) FILTER (WHERE tt.name = 'focus' AND ts.completed = TRUE),
        COUNT(*) FILTER (WHERE tt.name = 'inspire' AND ts.completed = TRUE),
        COUNT(*) FILTER (WHERE tt.name = 'talk' AND ts.completed = TRUE)
    INTO focus_count, inspire_count, talk_count
    FROM timer_sessions ts
    JOIN timer_types tt ON ts.timer_type_id = tt.id
    WHERE ts.user_id = target_user_id 
      AND DATE(ts.started_at) BETWEEN target_week_start AND week_end_date;
    
    -- 生成成就文字
    achievement_text := CASE 
        WHEN focus_count >= 5 THEN '聚焦达人 🔥 - 本周专注如火，照亮创作之路'
        WHEN inspire_count >= 3 THEN '灵感播种者 ⭐ - 创意的种子已经播撒'
        WHEN talk_count >= 2 THEN '篝火智者 🌙 - 与向导的对话满载智慧'
        ELSE '灵韵新芽 🌱 - 每一次尝试都是成长的开始'
    END;
    
    -- 插入周报记录
    INSERT INTO user_weekly_reports (
        user_id, week_start_date, week_end_date,
        focus_lights, inspire_stars, talk_moons,
        weekly_achievement, generated_at
    ) VALUES (
        target_user_id, target_week_start, week_end_date,
        focus_count, inspire_count, talk_count,
        achievement_text, NOW()
    )
    ON CONFLICT (user_id, week_start_date) 
    DO UPDATE SET
        focus_lights = EXCLUDED.focus_lights,
        inspire_stars = EXCLUDED.inspire_stars,
        talk_moons = EXCLUDED.talk_moons,
        weekly_achievement = EXCLUDED.weekly_achievement,
        generated_at = NOW()
    RETURNING id INTO report_id;
    
    RETURN report_id;
END;
$$ LANGUAGE plpgsql;
```

### 9.3 前端可视化配置

```typescript
// 前端配置文件 - weeklyVisualization.ts
export const WEEKLY_VISUALIZATION_CONFIG = {
  icons: {
    focus: '🔥',
    inspire: '⭐',
    talk: '🌙'
  },
  messages: {
    greeting: '本周您的灵韵之旅 ✨',
    achievements: {
      focus_master: '聚焦达人 🔥 - 本周专注如火，照亮创作之路',
      inspire_seeker: '灵感播种者 ⭐ - 创意的种子已经播撒',
      talk_sage: '篝火智者 🌙 - 与向导的对话满载智慧',
      aura_beginner: '灵韵新芽 🌱 - 每一次尝试都是成长的开始'
    },
    patterns: {
      focus: (count: number) => '🔥'.repeat(Math.min(count, 7)),
      inspire: (count: number) => '⭐'.repeat(Math.min(count, 7)),
      talk: (count: number) => '🌙'.repeat(Math.min(count, 5))
    }
  },
  colors: {
    primary: '#2D1B69',
    secondary: '#4A90E2',
    accent: '#8E6A5B',
    background: '#F8F9FA'
  }
};
```

### 9.4 周报查询示例

```sql
-- 获取用户最近4周的可视化数据
SELECT 
    week_start_date,
    focus_lights,
    inspire_stars,
    talk_moons,
    weekly_achievement
FROM user_weekly_reports 
WHERE user_id = $1 
  AND week_start_date >= CURRENT_DATE - INTERVAL '28 days'
ORDER BY week_start_date DESC;

-- 生成用户周报
SELECT generate_weekly_report(
    'user-uuid-here'::UUID, 
    DATE_TRUNC('week', CURRENT_DATE)::DATE
);
```

### 9.5 实施考虑

**优先级**：V2.0 版本
**依赖**：需要稳定的日报系统作为基础
**价值**：增强用户粘性，提供长期成就感

---

**数据库设计完成**  
**版本**：v1.0-MVP  
**适用于**：AURA STUDIO MVP (专注日报功能)  
**设计理念**：简单、实用、易维护 