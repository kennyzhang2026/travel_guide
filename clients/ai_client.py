"""
AI 客户端模块 - 使用 DeepSeek API 生成旅游攻略
"""

import openai
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AIClient:
    """AI 客户端 - 使用 DeepSeek API"""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化 AI 客户端

        Args:
            api_key: DeepSeek API Key
            base_url: API 基础 URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = None

        if api_key:
            self._initialize_client()

    def _initialize_client(self):
        """初始化 OpenAI 兼容客户端"""
        try:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info("AI 客户端 (DeepSeek) 初始化成功")
        except Exception as e:
            logger.error(f"AI 客户端初始化失败: {e}")
            self.client = None

    def generate_guide(self,
                      user_request: Dict[str, Any],
                      weather_info: Optional[str] = None,
                      traffic_info: Optional[str] = None,
                      model: str = "deepseek-chat",
                      temperature: float = 0.7,
                      max_tokens: int = 4000) -> Dict[str, Any]:
        """
        生成旅游攻略

        Args:
            user_request: 用户需求数据
                - destination: 目的地
                - origin: 出发地
                - start_date: 出发日期
                - end_date: 返回日期
                - budget: 预算
                - preferences: 偏好
            weather_info: 天气信息 (可选)
            traffic_info: 交通信息 (可选, v2.2.0)
            model: 使用的模型
            temperature: 温度参数
            max_tokens: 最大生成 token 数

        Returns:
            Dict 包含生成的攻略内容或错误信息
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI 客户端未初始化，请检查 API Key",
                "content": None
            }

        # 构建系统提示词
        system_prompt = self._build_system_prompt()

        # 构建用户消息
        user_message = self._build_user_message(user_request, weather_info, traffic_info)

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            content = response.choices[0].message.content

            logger.info(f"攻略生成成功，token 使用: {response.usage.total_tokens}")

            return {
                "success": True,
                "content": content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except openai.AuthenticationError as e:
            logger.error(f"认证失败: {e}")
            return {"success": False, "error": f"API Key 认证失败", "content": None}
        except openai.RateLimitError as e:
            logger.error(f"请求频率限制: {e}")
            return {"success": False, "error": f"请求频率超限", "content": None}
        except openai.APIConnectionError as e:
            logger.error(f"网络连接错误: {e}")
            return {"success": False, "error": f"网络连接错误", "content": None}
        except Exception as e:
            logger.error(f"生成攻略时出错: {e}")
            return {"success": False, "error": f"未知错误: {str(e)}", "content": None}

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        from utils.prompts import PromptTemplates
        return PromptTemplates.SYSTEM_PROMPT

    def _build_user_message(self, user_request: Dict[str, Any], weather_info: Optional[str] = None, traffic_info: Optional[str] = None) -> str:
        """构建用户消息"""
        destination = user_request.get("destination", "")
        origin = user_request.get("origin", "")
        start_date = user_request.get("start_date", "")
        end_date = user_request.get("end_date", "")
        budget = user_request.get("budget", 0)
        preferences = user_request.get("preferences", "")

        message = f"""请为我的旅行制定一份详细攻略：

**目的地**: {destination}
**出发地**: {origin}
**出发日期**: {start_date}
**返回日期**: {end_date}
**预算**: {budget} 元
**偏好**: {preferences}
"""

        if weather_info:
            message += f"\n**天气信息**:\n{weather_info}\n"

        if traffic_info:
            message += f"\n**交通信息**:\n{traffic_info}\n"

        message += "\n请根据以上信息，为我生成一份详细的旅游攻略。"

        return message

    def chat(self, message: str, system_prompt: Optional[str] = None,
             model: str = "deepseek-chat", **kwargs) -> Dict[str, Any]:
        """
        通用对话接口

        Args:
            message: 用户消息
            system_prompt: 系统提示词 (可选)
            model: 使用的模型
            **kwargs: 其他参数

        Returns:
            Dict 包含响应内容或错误信息
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI 客户端未初始化",
                "content": None
            }

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model
            }

        except Exception as e:
            logger.error(f"对话请求失败: {e}")
            return {"success": False, "error": str(e), "content": None}

    def generate_pitfall_guide(self,
                               destination: str,
                               preferences: str = "",
                               model: str = "deepseek-chat",
                               temperature: float = 0.7,
                               max_tokens: int = 2000) -> Dict[str, Any]:
        """
        生成目的地避坑指南

        Args:
            destination: 目的地城市/地区
            preferences: 用户偏好（可选）
            model: 使用的模型
            temperature: 温度参数
            max_tokens: 最大生成 token 数

        Returns:
            Dict 包含生成的避坑指南或错误信息
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI 客户端未初始化，请检查 API Key",
                "content": None
            }

        # 从 PromptTemplates 获取避坑指南提示词
        from utils.prompts import PromptTemplates
        system_prompt = PromptTemplates.PITFALL_PROMPT

        # 构建用户消息
        user_message = f"请为 {destination} 生成一份详细的旅游避坑指南。"
        if preferences:
            user_message += f"\n\n用户偏好：{preferences}"

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            content = response.choices[0].message.content

            logger.info(f"避坑指南生成成功，token 使用: {response.usage.total_tokens}")

            return {
                "success": True,
                "content": content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except openai.AuthenticationError as e:
            logger.error(f"认证失败: {e}")
            return {"success": False, "error": f"API Key 认证失败", "content": None}
        except openai.RateLimitError as e:
            logger.error(f"请求频率限制: {e}")
            return {"success": False, "error": f"请求频率超限", "content": None}
        except openai.APIConnectionError as e:
            logger.error(f"网络连接错误: {e}")
            return {"success": False, "error": f"网络连接错误", "content": None}
        except Exception as e:
            logger.error(f"生成避坑指南时出错: {e}")
            return {"success": False, "error": f"未知错误: {str(e)}", "content": None}
