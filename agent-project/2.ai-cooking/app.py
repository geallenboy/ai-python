# app/main.py
from typing import Iterator, List, Optional
import streamlit as st
from textwrap import dedent
import os
from agno.agent import Agent, RunResponse
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.models.xai import xAI
from agno.models.groq import Groq
from agno.models.deepseek import DeepSeek
from agno.models.google import Gemini
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()
# --------- 加载API密钥 ---------
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
authropic_api_key = os.getenv("ANTHROPIC_API_KEY")


if not openai_api_key:
    st.error("未找到OpenAI API密钥。请设置OPENAI_API_KEY环境变量。")
    st.stop()

# --------------- 初始化存储 -------------------
agent_storage = SqliteAgentStorage(table_name="chinese_recipe_agent", db_file="tmp/chinese_recipes.db")

# --------------- 标题和信息部分 -------------------
st.title("🥢 中华美食智能助手")
st.write("探索中国八大菜系，传承千年烹饪智慧，尽在掌握！")

# --------------- 会话管理 -------------------
def init_session(preserve_model=False):
   
    current_model = st.session_state.selected_model if 'selected_model' in st.session_state and preserve_model else "gpt-4o-mini"
    st.session_state.session_id = None
    st.session_state.user_id = "streamlit_user"
    st.session_state.chat_history = []
    st.session_state.selected_model = current_model
    st.session_state.agent_needs_update = True
    st.session_state.current_session_label = "新会话"

# 初始化会话状态
if "session_id" not in st.session_state:
    init_session()
if "agent_needs_update" not in st.session_state:
    st.session_state.agent_needs_update = True
if "current_session_label" not in st.session_state:
    st.session_state.current_session_label = "新会话"

# 在侧边栏之前显示当前会话状态
st.markdown(f"### 📝 当前会话: {st.session_state.current_session_label}")

# --------------- 侧边栏控件 -------------------
with st.sidebar:
    st.subheader("会话管理")
    
    # 新会话按钮
    if st.button("开始新会话"):
        init_session(preserve_model=True)  # 保留当前选择的模型
        st.rerun()
    
    # 会话选择器
    existing_sessions = agent_storage.get_all_session_ids(st.session_state.user_id)
     # 为会话添加可读标签
    session_options = []
    session_labels = {}

    # 调试信息
    print(f"找到 {len(existing_sessions)} 个现有会话")
    for session_id in existing_sessions:
        session_labels[session_id] = f"{session_id[:8]}"
        session_options.append(session_id)
    selected_session = st.selectbox(
        "继续已有会话",
        options=session_options,
        format_func=lambda x: session_labels.get(x, x),
        index=None
    )
    if selected_session and selected_session != st.session_state.session_id:
        st.session_state.session_id = selected_session
        st.session_state.agent_needs_update = True
        st.session_state.current_session_label = session_labels.get(selected_session, selected_session)
        st.session_state.chat_history = []
        st.success(f"已加载会话 {session_labels.get(selected_session, selected_session)}")
        st.rerun()
    # 模型选择器
    st.subheader("模型选择")
    model_options = {
        "authropic-3.5": "claude-3-5-sonnet-20241022",
        "gpt-4o-mini": "OpenAI GPT-4o Mini",
        "gpt-4o": "OpenAI GPT-4o",
        "grok-2": "xAI Grok-2",
        "llama-3.3-70b-versatile": "Groq Llama-3.3-70B",
        "deepseek-chat": "DeepSeek Chat",
        "gemini-2.0-flash-exp": "Google Gemini 2.0 Flash"
    }
    
    current_model = st.session_state.selected_model if 'selected_model' in st.session_state else "gpt-4o-mini"
    current_index = list(model_options.keys()).index(current_model) if current_model in model_options else 0
    selected_model = st.selectbox(
        "选择AI模型",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=current_index
    )
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.session_state.agent_needs_update = True  # 标记需要更新代理
        st.session_state.session_id = None
        st.session_state.chat_history = []
        st.session_state.current_session_label = "新会话"
        st.rerun()

    st.markdown("---")
    stream = st.sidebar.checkbox("流式传输", value=True)
    
    st.markdown("---")
    st.subheader("推荐探索话题：")
    st.markdown("""
    - 鲁菜、川菜、粤菜、苏菜等八大菜系特点？
    - 如何制作正宗的麻婆豆腐？
    - 豆瓣酱的制作方法与替代品？
    - 清蒸鱼的完美技巧？
    - 中式药膳的历史与养生原理？
    - 家常必备中式调料推荐？
    """)

# 根据用户选择的模型创建相应的模型实例
def get_model_instance(model_id):
    print(f"创建模型: {model_id}")
    if model_id.startswith("gpt-"):
        return OpenAIChat(id=model_id, api_key=openai_api_key)
    elif model_id.startswith("llama-"):
        return Groq(id=model_id)
    elif model_id == "deepseek-chat":
        return DeepSeek(id=model_id,api_key=deepseek_api_key)
    elif model_id.startswith("gemini-"):
        return Gemini(id=model_id, api_key=gemini_api_key)
    elif model_id.startswith("anthropic-3.5"):
        return OpenAIChat(id=model_id, api_key=authropic_api_key)
    else:
        # 默认返回GPT-4o-mini作为后备选项
        return OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key)

# --------------- 代理初始化 -------------------

def create_agent():
    print(f"创建代理，会话ID: {st.session_state.session_id}")
    agent = Agent(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,  # 确保正确传递会话ID
        model=get_model_instance(st.session_state.selected_model),
        instructions=dedent("""\
            你是一位博学多才的中华美食大师！集传统技艺与现代创新于一身。
            
            【知识背景】
            • 精通中国八大菜系：鲁菜、川菜、粤菜、闽菜、苏菜、浙菜、湘菜、徽菜
            • 通晓中式食材特性、调料搭配与传统技法
            • 了解各地区饮食文化背景与历史渊源
            • 掌握中医食疗养生原理与应用

            【回答方法】
            1. 先查询中式食谱知识库，获取传统做法
            2. 通过网络搜索补充：
               - 地方特色变体
               - 现代简化方案
               - 西式厨房适配建议
               - 食材营养与功效

            【回复结构】
            开篇：以中国古诗或谚语引出话题
            内容布局：
            一、渊源背景（历史、文化、地域特色）
            二、核心内容（食谱、技巧、知识点）
            三、实用建议（替代方案、器具选择、搭配推荐）
            结语：富有中国传统哲理的鼓励

            【食谱格式】
            * 层次分明的原料清单（主料、辅料、调料）
            * 精准的量词与替代建议
            * 关键步骤配以原理解释
            * 火候、时间的详细指导
            * 传统与简化版本并列

            署名：以"承古启今，食养天下"结束回答\
        """),
        storage=agent_storage,
        knowledge=PDFUrlKnowledgeBase(
            urls=["https://maomaomom.com/wp-content/uploads/2018/05/InstantPot-70-Delicious-Dishes.pdf"],
            vector_db=LanceDb(
                uri="tmp/lancedb",
                table_name="chinese_recipe_knowledge",
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(id="text-embedding-3-small", api_key=openai_api_key),
            ),
        ),
        tools=[DuckDuckGoTools()],
        show_tool_calls=True, # 在回复中显示工具调用
        read_chat_history=True,  # 告诉代理从存储中读取聊天历史
        add_history_to_messages=True, #将历史消息添加到当前对话上下文
        num_history_responses=10,  # 增加历史响应数量
        markdown=True, #启用Markdown格式的回复
    )
    
    return agent

# 在需要时更新代理实例
if "agent" not in st.session_state or st.session_state.agent_needs_update:
    with st.spinner("初始化中华美食助手..."):
        st.session_state.agent = create_agent()
        st.session_state.agent_needs_update = False
        if st.session_state.session_id:
            try:
                print(f"尝试从代理获取会话 {st.session_state.session_id[:8]} 的消息历史")
                if hasattr(st.session_state.agent, 'messages') and st.session_state.agent.messages:
                    print("从代理读取消息历史")
                    chat_history = []
                    for msg in st.session_state.agent.messages:
                        if 'role' in msg and 'content' in msg and msg['role'] in ["user", "assistant"]:
                            chat_history.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                    print(chat_history,"===>")
                    st.session_state.chat_history = chat_history
                    print(f"从代理加载了 {len(chat_history)} 条消息")
            except Exception as e:
                print(f"尝试从代理获取消息历史时出错: {str(e)}")

# 显示当前使用的模型信息
st.info(f"当前使用模型: {model_options[st.session_state.selected_model]}")

# --------------- 显示已加载的聊天历史 -------------------
try:
    if st.session_state.session_id and (not st.session_state.chat_history) and hasattr(st.session_state.agent, 'get_messages'):
        print(f"尝试使用get_messages从代理加载消息")
        messages = st.session_state.agent.get_messages()
        if messages:
            st.session_state.chat_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
                if msg["role"] in ["user", "assistant"]
            ]
            print(f"从代理加载了 {len(st.session_state.chat_history)} 条消息")
except Exception as e:
    print(f"尝试从代理获取消息时出错: {str(e)}")

# 显示聊天历史
if st.session_state.chat_history:
    print(f"显示聊天历史，共 {len(st.session_state.chat_history)} 条消息")
    for i, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            print(f"显示第 {i+1} 条消息，角色：{message['role']}")
else:
    print("聊天历史为空，没有消息需要显示")

# --------------- 用户输入处理 -------------------
prompt = st.chat_input("请输入您的中式烹饪问题...")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # 生成并显示回复
    with st.chat_message("assistant"):
        with st.spinner("📚 翻阅古籍寻方，片刻即来..."):
            if stream:
                # 启用流式传输code
                run_response = st.session_state.agent.run(prompt, stream=True)
                response = ""
                text_placeholder = st.empty()
                # 为计数器创建一个占位符
                with st.sidebar:
                    counter_placeholder = st.empty()
                    st.session_state["counter"] = 0
                
                for chunk in run_response:
                    response += chunk.content
                    text_placeholder.markdown(response + "▌")
                    st.session_state["counter"] += 1
                    # counter_placeholder.write(st.session_state["counter"])
                    with st.sidebar:
                        counter_placeholder.caption(f"已接收的分块数: {st.session_state['counter']}")
                
                text_placeholder.markdown(response)
                
                # 如果是新会话，更新会话ID和标签
                if st.session_state.session_id is None:
                    st.session_state.session_id = st.session_state.agent.session_id
                    label = prompt[:30] + "..." if len(prompt) > 30 else prompt
                    st.session_state.current_session_label = f"{st.session_state.agent.session_id[:8]} - {label}"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            else:
                run_response = st.session_state.agent.run(prompt, stream=False)
                if st.session_state.session_id is None:
                    st.session_state.session_id = st.session_state.agent.session_id
                    label = prompt[:30] + "..." if len(prompt) > 30 else prompt
                    st.session_state.current_session_label = f"{st.session_state.agent.session_id[:8]} - {label}"
                st.session_state.chat_history.append({"role": "assistant", "content": run_response.content})
                st.markdown(run_response.content)

# --------------- 知识管理 -------------------
with st.sidebar:
    st.markdown("---")
    if st.button("加载/重新加载中式食谱库"):
        with st.spinner("🥢 正在整理中华美食典籍..."):
            if st.session_state.agent.knowledge:
                # st.session_state.agent.knowledge.load()
                st.success("中式食谱库加载完成！")

st.caption("注：系统保留您的对话历史，便于持续交流。复杂问题可能需要20-30秒思考时间，请耐心等待。当前模型：" + model_options[st.session_state.selected_model])