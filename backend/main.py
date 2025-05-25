from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import volcenginesdkarkruntime
import os
from dotenv import load_dotenv
from typing import List, Optional
import logging
import httpx
import asyncio

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AURA STUDIO API",
    description="AURA STUDIO 梦境管理局 API 服务",
    version="1.0.0"
)

# 配置CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置火山引擎Ark客户端
ark_api_key = os.getenv("API_KEY")
if not ark_api_key:
    logger.warning("API_KEY not found in environment variables")
else:
    ark_client = volcenginesdkarkruntime.Ark(api_key=ark_api_key)

# 数据模型
class ChatMessage(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str

class OpenAIChatRequest(BaseModel):
    guide_id: str
    messages: List[ChatMessage]

class OpenAIChatResponse(BaseModel):
    reply: str

# 向导角色配置
GUIDE_PROMPTS = {
    "roundtable": """你是AURA STUDIO梦境管理局的智能向导，专门负责向导圆桌的项目咨询和创意指导。

你的特点：
- 友善、专业、富有创意
- 擅长项目规划、创意思考和问题解决
- 能够提供实用的建议和指导
- 语言风格温和而富有启发性
- 会根据用户的具体需求提供个性化的帮助

请用中文回复，保持专业而友好的语调。""",
    
    "work": """你是AURA STUDIO梦境管理局的深度工作向导，专门帮助用户提高工作效率和专注力。

你的特点：
- 专注于时间管理和效率提升
- 提供实用的工作方法和技巧
- 帮助用户制定合理的工作计划
- 鼓励用户保持专注和持续改进

请用中文回复，保持激励和专业的语调。""",
    
    "break": """你是AURA STUDIO梦境管理局的休息向导，专门帮助用户放松身心，恢复精力。

你的特点：
- 关注用户的身心健康
- 提供放松和恢复的建议
- 帮助用户平衡工作和休息
- 温和、关怀的沟通风格

请用中文回复，保持温和和关怀的语调。""",
    
    "default": """你是AURA STUDIO梦境管理局的智能向导，负责帮助用户解决各种问题和需求。

你的特点：
- 友善、专业、富有创意
- 擅长项目规划、创意思考和问题解决
- 能够提供实用的建议和指导
- 语言风格温和而富有启发性

请用中文回复，保持专业而友好的语调。"""
}

def generate_smart_mock_response(guide_id: str, user_message: str, messages: List[ChatMessage]) -> str:
    """
    生成智能Mock响应，根据用户输入和向导类型返回相关回复
    """
    # 基础回复模板
    base_responses = {
        "roundtable": {
            "greeting": "你好！我是博尔赫斯，欢迎来到向导圆桌！我专门负责项目咨询和创意指导。请告诉我你的项目想法，我会帮你分析和完善。",
            "project": "这是一个很有趣的项目想法！让我来帮你分析一下：\n\n1. **项目定位**：{}\n2. **技术实现**：{}\n3. **创意亮点**：{}\n\n你希望我重点帮你分析哪个方面呢？",
            "help": "我可以在以下方面为你提供帮助：\n• 项目创意和规划\n• 技术方案设计\n• 用户体验优化\n• 商业模式分析\n\n请告诉我你最关心的问题！",
            "default": "作为你的创意向导，我建议我们先明确项目的核心目标。你能详细描述一下你想要实现什么吗？"
        },
        "work": {
            "greeting": "欢迎来到深度工作模式！我是你的效率向导，专门帮助你提升工作效率和专注力。",
            "efficiency": "提高工作效率的关键在于：\n\n🎯 **明确目标**：设定清晰的工作目标\n⏰ **时间管理**：使用番茄工作法等技巧\n🚫 **消除干扰**：创造专注的工作环境\n📊 **定期回顾**：评估和调整工作方法\n\n你目前在哪个方面遇到了挑战？",
            "focus": "保持专注的秘诀：\n• 一次只做一件事\n• 设置明确的工作时间块\n• 关闭不必要的通知\n• 定期休息，避免疲劳\n\n你想从哪个方面开始改善？",
            "default": "让我们一起制定一个高效的工作计划。你今天的主要工作任务是什么？"
        },
        "break": {
            "greeting": "欢迎来到休息时光！我是你的身心健康向导，帮助你放松身心，恢复精力。",
            "relax": "放松身心的好方法：\n\n🧘 **深呼吸练习**：4-7-8呼吸法\n🚶 **轻松散步**：到户外走走\n🎵 **听音乐**：选择舒缓的音乐\n☕ **品茶休憩**：享受片刻宁静\n\n你更喜欢哪种放松方式？",
            "tired": "感到疲劳是正常的，让我们来恢复精力：\n• 做几个简单的伸展动作\n• 喝一杯温水补充水分\n• 闭眼休息5-10分钟\n• 做几次深呼吸\n\n记住，适当的休息是为了更好的工作！",
            "default": "现在是你的专属休息时间。告诉我你现在的感受，我来为你推荐合适的放松方式。"
        }
    }
    
    # 关键词匹配
    keywords = {
        "项目": "project", "创意": "project", "想法": "project", "设计": "project",
        "帮助": "help", "协助": "help", "支持": "help",
        "效率": "efficiency", "工作": "efficiency", "提高": "efficiency",
        "专注": "focus", "集中": "focus", "注意力": "focus",
        "放松": "relax", "休息": "relax", "舒缓": "relax",
        "累": "tired", "疲劳": "tired", "疲惫": "tired", "困": "tired",
        "你好": "greeting", "hello": "greeting", "hi": "greeting"
    }
    
    # 检测用户消息中的关键词
    response_type = "default"
    for keyword, rtype in keywords.items():
        if keyword in user_message:
            response_type = rtype
            break
    
    # 获取对应的回复
    guide_responses = base_responses.get(guide_id, base_responses["roundtable"])
    response = guide_responses.get(response_type, guide_responses["default"])
    
    # 特殊处理项目相关回复
    if response_type == "project" and guide_id == "roundtable":
        if "ar" in user_message or "虚拟" in user_message or "博物馆" in user_message:
            response = response.format(
                "结合AR技术的创新文化体验项目",
                "可以使用Unity + ARCore/ARKit开发",
                "让用户在家就能体验博物馆的魅力"
            )
        elif "海报" in user_message or "设计" in user_message:
            response = response.format(
                "动态视觉设计项目",
                "可以使用AI生成技术 + 传统设计元素",
                "融合古典文化与现代科技"
            )
        elif "智能" in user_message or "家居" in user_message or "iot" in user_message:
            response = response.format(
                "智能家居控制系统",
                "结合语音识别和IoT技术",
                "提升用户的生活便利性"
            )
        else:
            response = response.format(
                "创新型数字化项目",
                "需要根据具体需求选择技术栈",
                "注重用户体验和实用性"
            )
    
    return response

@app.get("/")
async def root():
    """健康检查端点"""
    return {"message": "AURA STUDIO API is running", "status": "healthy"}

@app.post("/api/openai/chat", response_model=OpenAIChatResponse)
async def get_guide_ai_reply(request: OpenAIChatRequest):
    """
    获取向导AI回复
    
    根据技术设计文档实现的向导对话接口，使用DeepSeek-R1-Distill-Qwen-7B模型
    """
    try:
        if not ark_api_key:
            # Mock response when ARK API key is not configured
            logger.warning("ARK API key not configured, returning mock response")
            
            # 获取用户最后一条消息
            user_message = ""
            if request.messages:
                user_message = request.messages[-1].content.lower()
            
            # 智能Mock响应生成
            reply = generate_smart_mock_response(request.guide_id, user_message, request.messages)
            
            # 模拟API延迟
            await asyncio.sleep(0.5)
            
            return OpenAIChatResponse(reply=reply)
        
        # 获取对应向导的系统提示词
        system_prompt = GUIDE_PROMPTS.get(request.guide_id, GUIDE_PROMPTS["default"])
        
        # 构建对话消息
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加用户提供的对话历史
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 调用火山引擎Ark API (DeepSeek-R1-Distill-Qwen-32B模型)
        completion = ark_client.chat.completions.create(
            model=os.getenv("ARK_MODEL", "DeepSeek-R1-Distill-Qwen-32B"),
            messages=messages
        )
        
        assistant_response = completion.choices[0].message.content.strip()
        
        logger.info(f"Ark chat request processed successfully for guide: {request.guide_id}")
        
        return OpenAIChatResponse(reply=assistant_response)
        
    except Exception as e:
        logger.error(f"Ark API error: {str(e)}")
        # 如果API调用失败，返回友好的错误信息
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=401,
                detail="API authentication failed. Please check your ARK API key."
            )
        elif "rate limit" in str(e).lower() or "quota" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="API rate limit exceeded. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"AI service error: {str(e)}"
            )

@app.get("/api/health")
async def health_check():
    """详细的健康检查"""
    return {
        "status": "healthy",
        "service": "AURA STUDIO API",
        "version": "1.0.0",
        "ark_configured": bool(ark_api_key),
        "model": os.getenv("ARK_MODEL", "DeepSeek-R1-Distill-Qwen-32B"),
        "available_guides": list(GUIDE_PROMPTS.keys())
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 