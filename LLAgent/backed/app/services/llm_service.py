"""LLM服务模块 (兼容阿里云 Dashscope qwen-max 配置)"""

import os
from langchain_openai import ChatOpenAI
from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def get_llm() -> ChatOpenAI:
    """
    获取LLM实例(单例模式)
    
    Returns:
        ChatOpenAI实例
    """
    global _llm_instance
    
    if _llm_instance is None:
        settings = get_settings()
        
        # 优先读取您图片中配置的专属环境变量，其次使用 settings 配置或默认值
        api_key = os.getenv("LLM_API_KEY") or getattr(settings, "llm_api_key", None)
        base_url = os.getenv("LLM_BASE_URL") or getattr(settings, "llm_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        model_id = os.getenv("LLM_MODEL_ID") or getattr(settings, "llm_model_id", "qwen-max")
        
        if not api_key:
            raise ValueError("未检测到 LLM_API_KEY 环境变量，请在 .env 文件中进行配置。")
            
        # 兼容性处理：Dashscope 的兼容 Openai 基础路径可能需要加上 /compatible-mode/v1 后缀
        # 如果您的配置中已经包含，则不做更改；如果不含，则予以规范拼接
        if "dashscope.aliyuncs.com" in base_url and not base_url.endswith("/compatible-mode/v1"):
            base_url = base_url.rstrip("/") + "/compatible-mode/v1"

        # 实例化 LangChain 官方的 ChatOpenAI 客户端并传入百炼平台的配置
        _llm_instance = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=base_url,
            model_name=model_id,
            temperature=0.2,   # 设定较低值以维持行程规划 JSON 输出的严谨度
            streaming=True,
            max_tokens=2000
        )
        
        print(f"✅ LangChain 阿里云 Dashscope 服务初始化成功")
        print(f"   基础路径: {base_url}")
        print(f"   模型: {model_id}")
    
    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None