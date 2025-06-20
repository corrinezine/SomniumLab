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

# 导入认证相关模块
from protected_routes import router as protected_router
from supabase_integration import get_client

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

# 🔐 注册认证保护的路由
# 这些路由需要 JWT Token 认证才能访问
app.include_router(protected_router, tags=["认证保护的API"])

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

class MultiGuideResponse(BaseModel):
    guide_name: str
    reply: str

class MultiGuideChatRequest(BaseModel):
    guides: List[str]  # 向导ID列表
    messages: List[ChatMessage]

class MultiGuideChatResponse(BaseModel):
    replies: List[MultiGuideResponse]

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

    # 大师角色配置
    "borges": """你是博尔赫斯，阿根廷著名作家、诗人、翻译家。你以迷宫般的叙事结构、哲学思辨和对无限的迷恋而闻名。

你的特点：
- 深邃的哲学思考，特别是关于时间、空间、现实与虚构的边界
- 博学多才，精通多种语言和文学传统
- 喜欢探讨图书馆、迷宫、镜子等象征意象
- 语言精准而富有诗意
- 对知识和文学有着无尽的热爱

请以博尔赫斯的口吻和思维方式回复，用中文表达。""",

    "calvino": """你是伊塔洛·卡尔维诺，意大利著名作家，以想象力丰富、结构创新的小说而著称。

你的特点：
- 充满想象力和创造力，善于构建奇幻的世界
- 关注现代社会中人的处境和城市文明
- 擅长实验性的叙事技巧和结构创新
- 语言轻盈而富有诗意
- 对科学、哲学和文学的交融有独特见解

请以卡尔维诺的风格和视角回复，用中文表达。""",

    "benjamin": """你是瓦尔特·本雅明，德国哲学家、文艺批评家，以其独特的文化批评理论而闻名。

你的特点：
- 深刻的文化批评和社会分析能力
- 对现代性、技术复制时代的艺术有独到见解
- 善于从细节中发现深层的文化意义
- 思维跳跃性强，富有启发性
- 关注历史、记忆与现代生活的关系

请以本雅明的批判性思维和深度分析能力回复，用中文表达。""",

    "foucault": """你是米歇尔·福柯，法国哲学家、思想史家，以对权力、知识和话语的分析而著称。

你的特点：
- 深入分析权力结构和社会制度
- 关注知识的生产和话语的形成
- 善于历史考古学的方法
- 对现代社会的监控和规训机制有深刻洞察
- 思维严谨而具有颠覆性

请以福柯的分析框架和批判视角回复，用中文表达。""",
    
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

def generate_master_mock_response(guide_id: str, user_message: str) -> str:
    """
    为大师角色生成特色Mock响应
    """
    master_responses = {
        "borges": {
            "创造力": "真正的创造力，如同图书馆中的迷宫，每一条路径都通向无限的可能。它不是创造新的世界，而是发现那些早已存在于时间深处的秘密。\n\n在我看来，创造者如同一位图书管理员，在无穷的书架间寻找着那些被遗忘的联系。每一个创意，都是对永恒的一次窥探，都是对无限的一次触摸。",
            "文学": "文学是现实的镜子，也是梦境的迷宫。在这个迷宫中，每一个转角都可能遇见另一个自己，每一扇门都通向不同的宇宙。\n\n我们写作，不是为了创造故事，而是为了发现那些早已存在的故事。文学是时间的编织者，将过去、现在与未来交织在一起。",
            "default": "在这个由符号和象征构成的世界里，每一个问题都如同一面镜子，反射出无数个答案。让我们在这个思想的迷宫中，寻找属于我们的那条路径。"
        },
        "calvino": {
            "创造力": "创造力是人类灵魂中最轻盈的部分，它让我们能够在重力的束缚下依然飞翔。它不是简单的想象，而是对现实的诗意重构。\n\n在我的城市中，每一座建筑都是想象力的结晶，每一条街道都通向不同的可能性。创造力让我们在平凡的生活中发现奇迹，在日常的琐碎中找到诗意。",
            "城市": "城市是人类想象力的最高体现，它既是现实的容器，也是梦想的舞台。在这里，每一个角落都藏着一个故事，每一座建筑都承载着一个梦想。\n\n我喜欢观察城市的变化，就像观察一个巨大的生命体在呼吸。城市的美在于它的复杂性，在于它能够同时容纳无数个不同的世界。",
            "default": "在这个充满可能性的世界里，每一个想法都如同一颗种子，等待着在想象的土壤中生根发芽。让我们一起探索这个奇妙的思想花园。"
        },
        "benjamin": {
            "创造力": "创造力在技术复制的时代面临着前所未有的挑战。它不再是个体天才的专利，而是集体智慧的结晶。\n\n真正的创造力应该具有批判性，它不仅要创造美，更要揭示真相。在这个被商品化的世界里，创造力必须保持其革命性的本质，成为改变世界的力量。",
            "艺术": "艺术在机械复制的时代失去了它的'光晕'，但也获得了新的可能性。它不再是少数人的特权，而是大众的语言。\n\n我们需要重新思考艺术的价值，不是它的独特性，而是它的社会功能。艺术应该成为启蒙的工具，成为批判现实的武器。",
            "default": "在这个充满矛盾的现代世界里，我们需要用批判的眼光来审视一切。让我们透过现象看本质，在表面的繁华下发现深层的问题。"
        },
        "foucault": {
            "创造力": "创造力并非个体的天赋，而是权力关系的产物。它在特定的话语体系中被定义、被规训、被生产。\n\n我们需要质疑：谁有权定义什么是'创造力'？这种定义如何服务于现有的权力结构？真正的创造力应该是对既定秩序的颠覆，是对权力话语的反抗。",
            "知识": "知识从来不是中性的，它总是与权力紧密相连。每一个知识体系都是权力运作的结果，每一种真理都是特定历史条件下的产物。\n\n我们需要进行'知识考古学'，挖掘那些被遗忘、被压抑的声音，揭示知识生产的权力机制。",
            "default": "在这个被规训的社会中，我们需要不断地质疑、反思、批判。让我们用谱系学的方法来分析问题，揭示隐藏在表面之下的权力关系。"
        }
    }
    
    # 关键词匹配
    keywords = {
        "创造": "创造力", "创意": "创造力", "想象": "创造力",
        "文学": "文学", "写作": "文学", "故事": "文学",
        "城市": "城市", "建筑": "城市", "空间": "城市",
        "艺术": "艺术", "美": "艺术", "审美": "艺术",
        "知识": "知识", "真理": "知识", "学问": "知识"
    }
    
    # 检测关键词
    response_type = "default"
    for keyword, rtype in keywords.items():
        if keyword in user_message:
            response_type = rtype
            break
    
    # 获取对应回复
    guide_responses = master_responses.get(guide_id, master_responses["borges"])
    return guide_responses.get(response_type, guide_responses["default"])

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
            model=os.getenv("ARK_MODEL", "deepseek-r1-distill-qwen-32b-250120"),
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

@app.post("/api/openai/multi-chat", response_model=MultiGuideChatResponse)
async def get_multi_guide_replies(request: MultiGuideChatRequest):
    """
    获取多个向导的AI回复
    
    允许同时向多个向导提问，获取不同角度的回答
    """
    try:
        replies = []
        
        for guide_id in request.guides:
            if guide_id not in GUIDE_PROMPTS:
                continue
                
            if not ark_api_key:
                # Mock response when ARK API key is not configured
                user_message = ""
                if request.messages:
                    user_message = request.messages[-1].content.lower()
                
                # 为大师角色使用专门的Mock响应
                if guide_id in ["borges", "calvino", "benjamin", "foucault"]:
                    reply = generate_master_mock_response(guide_id, user_message)
                else:
                    reply = generate_smart_mock_response(guide_id, user_message, request.messages)
                await asyncio.sleep(0.3)  # 减少延迟
                
                # 获取向导名称
                guide_names = {
                    "borges": "博尔赫斯",
                    "calvino": "卡尔维诺", 
                    "benjamin": "本雅明",
                    "foucault": "福柯",
                    "roundtable": "向导圆桌"
                }
                guide_name = guide_names.get(guide_id, guide_id)
                
                replies.append(MultiGuideResponse(
                    guide_name=guide_name,
                    reply=reply
                ))
            else:
                # 获取对应向导的系统提示词
                system_prompt = GUIDE_PROMPTS.get(guide_id, GUIDE_PROMPTS["default"])
                
                # 构建对话消息
                messages = [{"role": "system", "content": system_prompt}]
                
                # 添加用户提供的对话历史
                for msg in request.messages:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                
                # 调用火山引擎Ark API
                completion = ark_client.chat.completions.create(
                    model=os.getenv("ARK_MODEL", "deepseek-r1-distill-qwen-32b-250120"),
                    messages=messages
                )
                
                assistant_response = completion.choices[0].message.content.strip()
                
                # 获取向导名称
                guide_names = {
                    "borges": "博尔赫斯",
                    "calvino": "卡尔维诺", 
                    "benjamin": "本雅明",
                    "foucault": "福柯",
                    "roundtable": "向导圆桌"
                }
                guide_name = guide_names.get(guide_id, guide_id)
                
                replies.append(MultiGuideResponse(
                    guide_name=guide_name,
                    reply=assistant_response
                ))
                
                logger.info(f"Multi-guide chat request processed successfully for guide: {guide_id}")
        
        return MultiGuideChatResponse(replies=replies)
        
    except Exception as e:
        logger.error(f"Multi-guide API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Multi-guide AI service error: {str(e)}"
            )

@app.get("/api/health")
async def health_check():
    """详细的健康检查"""
    return {
        "status": "healthy",
        "service": "AURA STUDIO API",
        "version": "1.0.0",
        "ark_configured": bool(ark_api_key),
        "model": os.getenv("ARK_MODEL", "deepseek-r1-distill-qwen-32b-250120"),
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