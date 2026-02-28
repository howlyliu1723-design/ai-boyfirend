import os
from openai import OpenAI
import streamlit as st
from config import SYSTEM_PROMPT_TEMPLATE


class AIService:
    def __init__(self):
        """初始化AI服务客户端"""
        self.client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )

    def get_response(self, messages, character=""):
        """获取AI响应"""
        # 构建完整的系统提示词
        system_prompt = SYSTEM_PROMPT_TEMPLATE + character

        # 准备消息历史
        chat_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # 调用AI大模型
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_messages,
            stream=True
        )

        return response

    def process_stream_response(self, response):
        """处理流式响应"""
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                yield full_response
        return full_response
