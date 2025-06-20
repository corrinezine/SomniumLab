-- ==========================================
-- AURA STUDIO 完整数据库设置脚本
-- 在 Supabase SQL 编辑器中执行此脚本
-- ==========================================

-- 1. 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. 创建用户表
CREATE TABLE IF NOT EXISTS users (
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
CREATE TABLE IF NOT EXISTS audio_tracks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 创建计时器类型表
CREATE TABLE IF NOT EXISTS timer_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    default_duration INTEGER NOT NULL,
    description TEXT,
    background_image VARCHAR(500),
    default_audio_track_id INTEGER REFERENCES audio_tracks(id),
    color_theme VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 创建计时器会话表
CREATE TABLE IF NOT EXISTS timer_sessions (
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

-- 6. 创建用户日志表
CREATE TABLE IF NOT EXISTS user_daily_logs (
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

-- 7. 创建索引提高查询性能
CREATE INDEX IF NOT EXISTS idx_timer_sessions_user_started ON timer_sessions (user_id, started_at);
CREATE INDEX IF NOT EXISTS idx_timer_sessions_type ON timer_sessions (timer_type_id);
CREATE INDEX IF NOT EXISTS idx_user_daily_logs_date ON user_daily_logs (log_date);
CREATE INDEX IF NOT EXISTS idx_user_daily_logs_user_id ON user_daily_logs (user_id);

-- 8. 创建更新时间触发器
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

CREATE TRIGGER update_user_daily_logs_updated_at 
    BEFORE UPDATE ON user_daily_logs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 9. 插入初始数据

-- 插入音轨数据
INSERT INTO audio_tracks (name, file_path) VALUES
('定风波', '/audio/邓翊群 - 定风波.mp3'),
('Luv Sic', '/audio/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3'),
('Générique', '/audio/Miles Davis - Générique.mp3')
ON CONFLICT DO NOTHING;

-- 插入计时器类型
INSERT INTO timer_types (name, display_name, default_duration, description, background_image, default_audio_track_id) VALUES
('focus', '聚焦', 90, '聚焦光线、语言或者太空垃圾', '/images/deep-work.png', 1),
('inspire', '播种', 30, '播种灵感、种子或者一个怪念头', '/images/break.png', 2),
('talk', '篝火', 60, '与向导进行沉浸式对话的空间', '/images/roundtable.png', 3)
ON CONFLICT (name) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    default_duration = EXCLUDED.default_duration,
    description = EXCLUDED.description,
    background_image = EXCLUDED.background_image,
    default_audio_track_id = EXCLUDED.default_audio_track_id;

-- 10. 创建每日日志汇总函数
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

-- 11. 设置权限 (注意：根据实际需要调整权限策略)
-- 允许匿名和认证用户查看公共数据
GRANT SELECT ON audio_tracks TO anon, authenticated;
GRANT SELECT ON timer_types TO anon, authenticated;

-- 允许认证用户操作自己的数据
GRANT ALL ON users TO authenticated;
GRANT ALL ON timer_sessions TO authenticated;
GRANT ALL ON user_daily_logs TO authenticated;

-- 允许使用序列
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- 完成提示
SELECT 
    'AURA STUDIO 数据库设置完成！' as message,
    'Tables: ' || string_agg(table_name, ', ') as created_tables
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('users', 'audio_tracks', 'timer_types', 'timer_sessions', 'user_daily_logs'); 