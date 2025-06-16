# AURA STUDIO - OpenAI 相关功能技术设计文档（Tech Spec）

## 1. 向导对话 - 获取AI回复

- **接口名称**：获取向导AI回复
- **请求路径和方法**：
  - POST `/api/openai/chat`
- **请求参数说明**：
  | 参数名      | 类型   | 必填 | 说明                 |
  | ----------- | ------ | ---- | -------------------- |
  | guide_id    | string | 是   | 向导角色ID           |
  | messages    | array  | 是   | 聊天上下文消息数组   |
  |   └ role    | string | 是   | 消息角色（user/assistant）|
  |   └ content | string | 是   | 消息内容             |

- **依赖的外部服务**：
  - OpenAI Chat API（如 gpt-3.5-turbo 或 gpt-4）

- **示例请求体**：
```json
{
  "guide_id": "roundtable",
  "messages": [
    {"role": "user", "content": "请帮我脑暴项目"},
    {"role": "assistant", "content": "正在思考中…"}
  ]
}
```

- **示例返回 JSON**：
```json
{
  "reply": "你可以尝试用AI生成动态海报，结合云冈石窟的元素和现代设计风格。需要进一步细化吗？"
}
```

---

## 2. 向导对话 - 获取AI思考中动画（前端本地实现，无需API）
- 该功能为前端动画模拟，不依赖OpenAI，无需API接口。

---

## 3. 其他与OpenAI相关的MVP功能
- 当前MVP阶段，只有向导对话的AI回复依赖OpenAI接口。 