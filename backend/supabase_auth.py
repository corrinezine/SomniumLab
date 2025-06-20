"""
AURA STUDIO - Supabase JWT 认证模块

这个模块提供了完整的 Supabase 用户认证功能，包括：
- JWT Token 验证和解码
- 用户身份提取
- FastAPI 依赖注入
- 认证装饰器

作者：AI 编程导师
设计理念：安全、简单、易于理解
"""

import os
import jwt
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthenticatedUser(BaseModel):
    """认证用户信息模型
    
    这个类定义了从JWT Token中提取的用户信息结构
    包含用户ID、邮箱、认证时间等关键信息
    """
    user_id: str          # Supabase 用户 UUID
    email: str            # 用户邮箱
    aud: str             # 受众（audience）
    exp: int             # 过期时间戳
    iat: int             # 签发时间戳
    iss: str             # 签发者（issuer）
    sub: str             # 主题（subject，通常等于user_id）
    role: str            # 用户角色（通常是 'authenticated'）


class SupabaseAuth:
    """Supabase JWT 认证处理类
    
    这个类负责处理所有与 Supabase JWT 认证相关的操作：
    1. 验证 JWT Token 的有效性
    2. 解码 Token 获取用户信息
    3. 检查 Token 是否过期
    4. 提供 FastAPI 依赖注入功能
    """
    
    def __init__(self):
        """初始化认证处理器
        
        从环境变量中加载必要的配置信息：
        - JWT_SECRET: 用于验证 Token 签名的密钥
        - SUPABASE_URL: 用于验证 Token 签发者
        """
        # 从环境变量获取 JWT 密钥
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        self.supabase_url = os.getenv("SUPABASE_URL")
        
        # 验证必要的配置是否存在
        if not self.jwt_secret:
            raise ValueError("缺少 SUPABASE_JWT_SECRET 环境变量")
        
        if not self.supabase_url:
            raise ValueError("缺少 SUPABASE_URL 环境变量")
        
        # 从 Supabase URL 中提取项目引用（用于验证 Token 受众）
        # 例如：https://abc123.supabase.co -> abc123
        self.project_ref = self.supabase_url.split("//")[1].split(".")[0]
        
        logger.info("Supabase 认证模块初始化成功")
    
    def verify_token(self, token: str) -> Optional[AuthenticatedUser]:
        """验证 JWT Token 并提取用户信息
        
        这个方法执行以下步骤：
        1. 使用 JWT Secret 验证 Token 签名
        2. 检查 Token 是否过期
        3. 验证 Token 的受众和签发者
        4. 提取用户信息并返回
        
        Args:
            token (str): 要验证的 JWT Token
            
        Returns:
            Optional[AuthenticatedUser]: 如果验证成功返回用户信息，否则返回 None
        """
        try:
            # 步骤1: 解码 JWT Token
            # jwt.decode 会自动验证签名、过期时间等
            payload = jwt.decode(
                token,                          # 要解码的 Token
                self.jwt_secret,               # 用于验证签名的密钥
                algorithms=["HS256"],          # Supabase 使用的签名算法
                audience="authenticated",       # 验证受众，Supabase Auth 使用 "authenticated"
                issuer=f"{self.supabase_url}/auth/v1"  # 验证签发者
            )
            
            # 步骤2: 提取用户信息
            # Supabase JWT Token 的标准字段结构
            user_info = AuthenticatedUser(
                user_id=payload.get("sub"),     # sub 字段包含用户 ID
                email=payload.get("email"),     # 用户邮箱
                aud=payload.get("aud"),         # 受众
                exp=payload.get("exp"),         # 过期时间
                iat=payload.get("iat"),         # 签发时间
                iss=payload.get("iss"),         # 签发者
                sub=payload.get("sub"),         # 主题（用户ID）
                role=payload.get("role", "authenticated")  # 用户角色
            )
            
            # 步骤3: 额外的安全检查
            current_time = datetime.now(timezone.utc).timestamp()
            if payload.get("exp", 0) < current_time:
                logger.warning("Token 已过期")
                return None
            
            logger.info(f"Token 验证成功，用户: {user_info.email}")
            return user_info
            
        except jwt.ExpiredSignatureError:
            # Token 已过期
            logger.warning("JWT Token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            # Token 无效（签名错误、格式错误等）
            logger.warning(f"JWT Token 无效: {e}")
            return None
        except Exception as e:
            # 其他异常
            logger.error(f"Token 验证过程中发生错误: {e}")
            return None
    
    def extract_token_from_header(self, authorization: str) -> Optional[str]:
        """从 Authorization 头中提取 JWT Token
        
        标准的 Authorization 头格式是：Bearer <token>
        这个方法负责提取其中的 Token 部分
        
        Args:
            authorization (str): Authorization 头的值
            
        Returns:
            Optional[str]: 提取的 Token，如果格式错误返回 None
        """
        try:
            # 检查是否以 "Bearer " 开头
            if not authorization.startswith("Bearer "):
                logger.warning("Authorization 头格式错误，应该以 'Bearer ' 开头")
                return None
            
            # 提取 Token 部分（去掉 "Bearer " 前缀）
            token = authorization[7:]  # "Bearer " 长度为 7
            
            if not token.strip():
                logger.warning("Authorization 头中 Token 为空")
                return None
            
            return token.strip()
            
        except Exception as e:
            logger.error(f"提取 Token 时发生错误: {e}")
            return None


# 创建全局认证实例
# 这个实例会在整个应用中重复使用
supabase_auth = SupabaseAuth()

# 创建 FastAPI HTTP Bearer 安全方案
# 这个对象用于从请求头中自动提取 Authorization 信息
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """FastAPI 依赖注入函数：获取当前认证用户
    
    这个函数可以作为 FastAPI 路由的依赖项使用
    它会自动：
    1. 从请求头中提取 Authorization 信息
    2. 验证 JWT Token
    3. 返回用户信息或抛出认证异常
    
    使用方法：
    @app.get("/protected")
    async def protected_route(user: AuthenticatedUser = Depends(get_current_user)):
        return {"message": f"Hello {user.email}!"}
    
    Args:
        credentials: FastAPI 自动注入的认证凭据
        
    Returns:
        AuthenticatedUser: 认证成功的用户信息
        
    Raises:
        HTTPException: 认证失败时抛出 401 异常
    """
    # 验证 Token
    user = supabase_auth.verify_token(credentials.credentials)
    
    if user is None:
        # 认证失败，抛出 401 未授权异常
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[AuthenticatedUser]:
    """可选的用户认证依赖
    
    与 get_current_user 不同，这个函数不会在认证失败时抛出异常
    而是返回 None，适用于某些可选认证的路由
    
    Args:
        credentials: 可选的认证凭据
        
    Returns:
        Optional[AuthenticatedUser]: 认证成功返回用户信息，失败返回 None
    """
    if credentials is None:
        return None
    
    return supabase_auth.verify_token(credentials.credentials)


# 便捷函数
def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """验证 JWT Token 的便捷函数
    
    这是一个简化的接口，直接返回 Token 的原始 payload
    适用于需要访问完整 Token 信息的场景
    
    Args:
        token (str): 要验证的 JWT Token
        
    Returns:
        Optional[Dict[str, Any]]: Token 的 payload 信息，验证失败返回 None
    """
    user = supabase_auth.verify_token(token)
    if user:
        return user.dict()
    return None


# 装饰器风格的认证检查
def require_auth(func):
    """认证装饰器（仅作示例，FastAPI 推荐使用依赖注入）
    
    这是一个传统的装饰器风格认证检查
    但在 FastAPI 中，推荐使用上面的依赖注入方式
    """
    async def wrapper(*args, **kwargs):
        # 这里需要从 FastAPI 请求对象中提取 headers
        # 实际使用时推荐使用 Depends(get_current_user)
        return await func(*args, **kwargs)
    return wrapper


# 使用示例和测试函数
async def example_usage():
    """使用示例
    
    展示如何在实际代码中使用这个认证模块
    """
    # 模拟一个 JWT Token（实际使用时从前端获取）
    sample_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    # 验证 Token
    user = supabase_auth.verify_token(sample_token)
    
    if user:
        print(f"认证成功! 用户: {user.email}, ID: {user.user_id}")
    else:
        print("认证失败")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 