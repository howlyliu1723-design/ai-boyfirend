import os
import json
import streamlit as st

# 使用相对路径，适配云端环境
SESSION_DIR = "session"


def save_session():
    """保存当前会话到文件"""
    try:
        if st.session_state.session_id:
            session_data = {
                "session_id": st.session_state.session_id,
                "character": st.session_state.character,
                "messages": st.session_state.messages
            }

            # 创建会话目录（带异常处理）
            if not os.path.exists(SESSION_DIR):
                os.makedirs(SESSION_DIR, exist_ok=True)

            # 保存会话数据到JSON文件
            with open(f"{SESSION_DIR}/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # 在云端环境中可能出现权限问题，这里静默处理
        pass


def load_sessions():
    """加载所有会话列表"""
    try:
        session_list = []
        if os.path.exists(SESSION_DIR):
            for filename in os.listdir(SESSION_DIR):
                if filename.endswith(".json"):
                    session_name = filename[:-5]  # 去掉.json扩展名
                    session_list.append(session_name)
        return session_list
    except Exception as e:
        # 如果无法访问文件系统，返回空列表
        return []


def load_session(session_name):
    """加载指定会话"""
    try:
        session_file = f"{SESSION_DIR}/{session_name}.json"
        if os.path.exists(session_file):
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.session_id = session_data["session_id"]
                st.session_state.character = session_data["character"]
                st.session_state.messages = session_data["messages"]
                return True
    except Exception as e:
        st.error(f"加载会话失败: {e}")
    return False


def delete_session(session_name):
    """删除指定会话"""
    try:
        file_path = f"{SESSION_DIR}/{session_name}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            st.warning(f"会话文件 {session_name} 不存在")
    except Exception as e:
        st.error(f"删除会话失败: {str(e)}")
    return False


def create_new_session():
    """创建新会话"""
    import datetime
    try:
        # 保存当前会话
        save_session()

        # 创建新会话
        st.session_state.messages = []
        time_now = datetime.datetime.now()
        st.session_state.session_id = time_now.strftime("%Y-%m-%d_%H-%M-%S")
        save_session()
    except Exception as e:
        # 静默处理异常
        pass
