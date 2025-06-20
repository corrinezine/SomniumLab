-- 可选功能：向导对话记录表
-- 如果需要记录用户与向导的对话历史，可以添加此表

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    guide_id VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    session_id UUID REFERENCES timer_sessions(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chat_messages_content_length CHECK (LENGTH(content) > 0)
);

-- 创建索引
CREATE INDEX idx_chat_messages_user_guide ON chat_messages (user_id, guide_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages (created_at);
CREATE INDEX idx_chat_messages_session ON chat_messages (session_id);

-- RLS策略
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "用户只能查看自己的对话" ON chat_messages FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "用户只能创建自己的对话" ON chat_messages FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 插入示例数据（可选）
/*
INSERT INTO chat_messages (user_id, guide_id, role, content) VALUES
('user-uuid-here', 'roundtable', 'user', '请帮我脑暴项目'),
('user-uuid-here', 'roundtable', 'assistant', '你可以尝试用AI生成动态海报，结合云冈石窟的元素和现代设计风格。需要进一步细化吗？');
*/ 