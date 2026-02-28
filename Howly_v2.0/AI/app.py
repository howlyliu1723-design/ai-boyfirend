import streamlit as st
import datetime
import os
from openai import OpenAI
from config import setup_page, PAGE_CONFIG, SYSTEM_PROMPT_TEMPLATE
from session_manager import (
    save_session, load_sessions, load_session,
    delete_session, create_new_session
)

# 获取当前脚本所在目录，确保图片路径正确
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(CURRENT_DIR, "images", "logo.jpg")


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


def initialize_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "character" not in st.session_state:
        st.session_state.character = ""

    if "session_id" not in st.session_state:
        time_now = datetime.datetime.now()
        st.session_state.session_id = time_now.strftime("%Y-%m-%d_%H-%M-%S")
    if "user_avatar" not in st.session_state:
        st.session_state.user_avatar = "👩"  # 用户头像
    if "ai_avatar" not in st.session_state:
        st.session_state.ai_avatar = "🥰"    # AI头像（赛博昊理）

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.header("我的简单脑袋")

        # 新建会话按钮
        if st.button("新建唠嗑", icon="➕", width="stretch"):
            if st.session_state.messages:  # 如果有聊天记录
                create_new_session()
                st.rerun()
            else:
                st.error("还没和我说话就想找别人了？")

        # 会话历史列表
        st.text("都唠过啥")
        session_list = load_sessions()

        for session in session_list:
            col1, col2 = st.columns([4, 1])

            with col1:
                # 根据当前会话设置按钮样式
                button_type = "primary" if session == st.session_state.get("session_id", "") else "secondary"

                if st.button(session, icon="📂", width="stretch", key=f"load_{session}", type=button_type):
                    if load_session(session):
                        st.rerun()

            with col2:
                if st.button("❌", key=f"delete_{session}", help="删除此会话"):
                    if delete_session(session):
                        st.success(f"会话 {session} 已成功删除")
                        st.rerun()

        # 分隔线和个人信息
        st.text("➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖   ")
        st.subheader("我的帅气大脸", divider="blue")
        st.text("我是赛博昊理")
        st.text("我长这个样子")
        
        # 使用绝对路径加载图片，添加错误处理
        try:
            if os.path.exists(IMAGE_PATH):
                st.image(IMAGE_PATH, caption="赛博昊理", width=200)
            else:
                st.warning("图片文件未找到")
                st.info("📁 期待见到帅气的赛博昊理！")
        except Exception as e:
            st.error(f"图片加载出错: {str(e)}")
            st.info("🤖 但我们的聊天功能完全正常！")

        character = st.text_area("我的性格", placeholder="你想我是什么性格呀", value="")
        if character:
            st.session_state.character = character


def display_chat_history():
    """显示聊天历史"""
    for message in st.session_state.messages:
        if message["role"] == "user":
            # 用户消息 - 使用字符头像
            with st.chat_message("user", avatar=st.session_state.user_avatar):
                st.write(message["content"])
        else:
            # AI消息 - 使用字符头像
            with st.chat_message("assistant", avatar=st.session_state.ai_avatar):
                st.write(message["content"])

def handle_user_input(ai_service):
    """处理用户输入"""
    prompt = st.chat_input("和我说点什么吧~")

    if prompt:
        # 显示用户输入（带字符头像）
        with st.chat_message("user", avatar=st.session_state.user_avatar):
            st.write(prompt)

        # 保存用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 获取AI响应
        response = ai_service.get_response(st.session_state.messages, st.session_state.character)

        # 显示流式响应（带字符头像）
        with st.chat_message("assistant", avatar=st.session_state.ai_avatar):
            response_container = st.empty()
            full_response = ""

            for partial_response in ai_service.process_stream_response(response):
                response_container.write(partial_response)
                full_response = partial_response

        # 保存AI回复
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_session()


def main():
    """主函数"""
    # 设置页面
    setup_page()

    # 初始化会话状态
    initialize_session_state()

    # 初始化AI服务
    ai_service = AIService()

    # 渲染界面
    render_sidebar()
    display_chat_history()
    handle_user_input(ai_service)


if __name__ == "__main__":
    main()











