# app/main.py
from typing import Iterator, List, Optional
import streamlit as st
from textwrap import dedent
import os
from agno.agent import Agent, RunResponse
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType

# --------- 加载API密钥 ---------
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("未找到OpenAI API密钥。请设置OPENAI_API_KEY环境变量。")
    st.stop()

# --------------- 初始化存储 -------------------
agent_storage = SqliteAgentStorage(table_name="recipe_agent", db_file="tmp/agents.db")

# --------------- 标题和信息部分 -------------------
st.title("🧑🍳 AI泰式烹饪助手代理（带有RAG、网络和记忆功能）")
st.write("您的个人泰式料理专家，带有对话记忆功能！")

# --------------- 会话管理 -------------------
def init_session():
    st.session_state.session_id = None
    st.session_state.user_id = "streamlit_user"
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    init_session()

# --------------- 侧边栏控件 -------------------
with st.sidebar:
    st.subheader("会话管理")
    
    # 新会话按钮
    if st.button("开始新会话"):
        init_session()
        st.rerun()
    
    # 会话选择器
    # existing_sessions = agent_storage.get_all_session_ids(st.session_state.user_id)
    existing_sessions = agent_storage.get_all_session_ids(st.session_state.user_id)
    selected_session = st.selectbox(
        "继续已有会话",
        options=existing_sessions,
        index=0 if not existing_sessions else None
    )
    
    if selected_session and selected_session != st.session_state.session_id:
        st.session_state.session_id = selected_session
        st.session_state.chat_history = agent_storage.get_all_sessions(
            user_id=st.session_state.user_id,
            # session_id=selected_session
        )
        st.rerun()

    st.markdown("---")
    st.subheader("尝试这些查询：")
    st.markdown("""
    - 如何制作正宗的泰式炒河粉？
    - 红咖喱和绿咖喱有什么区别？
    - 高良姜的替代品有哪些？
    - 冬阴功汤的历史？
    - 泰式厨房必备食材？
    """)

# --------------- 代理初始化 -------------------
agent = Agent(
    user_id=st.session_state.user_id,
    session_id=st.session_state.session_id,
    model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),
    instructions=dedent("""\
        您是一位充满热情的泰式料理专家！🧑‍🍳
        结合烹饪指导和食品历史专业知识。

        回答策略：
        1. 首先查看食谱知识库
        2. 使用网络搜索获取：
           - 食材替代品
           - 历史背景
           - 额外提示

        回复格式：
        🌶️ 以相关表情符号开始
        📖 结构化部分：
        - 背景
        - 主要内容
        - 专业提示
        - 鼓励性结论

        对于食谱包括：
        📝 配料及替代品
        🔢 编号步骤
        💡 成功技巧

        以下列内容结束：
        - '烹饪愉快！ขอให้อร่อย!'\
    """),
    storage=agent_storage,
    knowledge=PDFUrlKnowledgeBase(
        urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="recipe_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small", api_key=openai_api_key),
        ),
    ),
    tools=[DuckDuckGoTools()],
    # 在回复中显示工具调用
    show_tool_calls=True,
    # 要向代理提供聊天历史记录
    # 我们可以：
    # 1. 提供代理一个读取聊天历史记录的工具
    read_chat_history=True,
    # 2. 自动将聊天历史记录添加到发送给模型的消息中
    add_history_to_messages=True,
    # 添加到消息中的历史回复数量
    num_history_responses=3,
    markdown=True,
)

# --------------- 用户输入处理 -------------------
prompt = st.chat_input("提出您的泰式烹饪问题...")

if prompt:
    # 将用户消息添加到历史记录
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成并显示回复
    with st.chat_message("assistant"):
        with st.spinner("👩🍳 正在为您准备答案..."):
            response = agent.run(prompt, stream=False)
            
            # 如果是新会话，更新会话ID
            if st.session_state.session_id is None:
                st.session_state.session_id = agent.session_id
                
            # 将回复存储在历史记录中
            st.session_state.chat_history.append({"role": "assistant", "content": response.content})
            
            # 显示回复
            st.markdown(response.content)

# --------------- 知识管理 -------------------
with st.sidebar:
    st.markdown("---")
    if st.button("加载/重新加载食谱数据库"):
        with st.spinner("🧑🍳 正在加载正宗泰式食谱..."):
            if agent.knowledge:
                agent.knowledge.load()
                st.success("食谱数据库已加载！")

st.caption("注意：跨会话维持对话历史记录。复杂查询可能需要20-30秒处理时间。")