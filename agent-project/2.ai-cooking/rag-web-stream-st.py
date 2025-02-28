
from typing import Iterator
import streamlit as st
from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv
# --------- 加载API密钥 ---------
import os

# 加载 .env 文件中的环境变量
load_dotenv()
# 从环境变量中加载OpenAI API密钥
openai_api_key = os.getenv("OPENAI_API_KEY")

print(openai_api_key)

if not openai_api_key:
    print("未找到OpenAI API密钥。请设置OPENAI_API_KEY环境变量。")
    exit()
# 侧边栏展示示例问题
with st.sidebar:
    st.subheader("尝试这些泰国烹饪问题：")
    st.markdown("""
    * 如何制作正宗的泰式炒河粉？
    * 红咖喱和绿咖喱的区别是什么？
    * 高良姜的替代品有哪些？
    * 冬阴功汤的历史是什么？
    * 泰国厨房必备的食材有哪些？
    * 如何制作泰式罗勒鸡？
    """)
    st.markdown("---")
    st.write("📚 知识库：超过50个正宗菜谱")
    st.write("🌐 网络搜索：替代品和历史信息")

# 设置 Streamlit 应用
st.title("🧑🍳 AI泰国烹饪助手")
st.write("欢迎体验您的私人泰国美食专家！可询问菜谱、烹饪技巧和美食历史。")

#在侧边栏中添加一个复选框（checkbox），标签为“流式传输”。
stream = st.sidebar.checkbox("Stream")


# 初始化会话状态中的查询计数器
with st.sidebar:
    counter_placeholder = st.empty()
if "counter" not in st.session_state:
    st.session_state["counter"] = 0
st.session_state["counter"] += 1
with st.sidebar:
    counter_placeholder.caption(f"Chunks received: {st.session_state['counter']}")

# --------------- 代理部分 -------------------

# 创建具有烹饪知识的代理
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),
    # model=xAI(id="grok-2"),
    # model=Groq(id="llama-3.3-70b-versatile"),
    # model=DeepSeek(id="deepseek-chat"),
    # model=Gemini(
    #     id="gemini-2.0-flash-exp",
    #     api_key=gemini_api_key,
    # ),
    instructions=dedent("""\
        你是一个热情且知识渊博的泰国美食专家！🧑‍🍳
        结合温暖的烹饪指导语气与美食历史学家的专长。

        回答策略：
        1. 首先检查菜谱知识库以获取正宗信息
        2. 仅在以下情况下使用网络搜索：
           - 现代替代品
           - 历史背景
           - 额外的烹饪建议
        3. 对于菜谱，优先使用知识库内容
        4. 使用网络信息时明确引用来源

        回复格式：
        🌶️ 以相关表情符号开头
        📖 结构清晰：
        - 介绍/背景
        - 主要内容（菜谱/步骤/解释）
        - 专业建议和文化见解
        - 鼓励性结论

        对于菜谱包括：
        📝 带有替代品的食材清单
        🔢 编号步骤
        💡 成功秘诀和常见错误

        特别功能：
        - 解释泰国食材及其替代品
        - 分享文化传统
        - 根据饮食需求调整菜谱
        - 建议搭配推荐

        结束语：
        - '祝你烹饪愉快！ขอให้อร่อย（享用你的美食）！'
        - '愿你的泰国烹饪冒险带来欢乐！'
        - '享受你的自制泰国盛宴！'\
    """),
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
    show_tool_calls=True,
    markdown=True,
    add_references=True,
    debug_mode=True,
)

# --------------- 代理知识加载 -------------------

# 一次性加载知识库
# if agent.knowledge and agent.knowledge.exists() == False:
if agent.knowledge:
    # with st.spinner("🧑🍳 正在加载正宗泰国菜谱..."):
    agent.knowledge.load()

# --------------- 打印代理知识以进行调试 -------------------
# methods_info = []
# for method_name in dir(agent.knowledge):
#     if method_name.startswith('__'):
#         continue
#     method = getattr(agent.knowledge, method_name)
#     if callable(method):
#         try:
#             sig = inspect.signature(method)
#             methods_info.append(f"{method_name}{sig}")
#         except:
#             methods_info.append(method_name)
# st.markdown("**代理知识方法：**")
# st.code('\n'.join(methods_info))
# st.write(agent.knowledge.exists())

# 添加按钮并检查是否被点击
if st.sidebar.button("加载知识库"):
    if agent.knowledge:
        with st.sidebar:
            with st.spinner("🧑🍳 正在加载正宗泰国菜谱..."):
                agent.knowledge.load()
                st.success("菜谱数据库加载完成！")

# 用户输入
prompt = st.text_input("提出您的泰国烹饪问题（例如，'如何制作泰式炒河粉？'）")

# 生成并显示回答
if prompt:
    with st.spinner("👩🍳 正在准备您的答案..."):
        # stream = True  # 启用流式传输
        if stream:
            run_response: Iterator[RunResponse] = agent.run(prompt, stream=True)
            response = ""
            text_placeholder = st.empty()
            for chunk in run_response:
                response += chunk.content
                text_placeholder.markdown(response + "▌")
                st.session_state["counter"] += 1
                # counter_placeholder.write(st.session_state["counter"])
                with st.sidebar:
                    counter_placeholder.caption(f"已接收的分块数: {st.session_state['counter']}")
            text_placeholder.markdown(response)
        else:
            response = agent.run(prompt, stream=False)
            st.markdown(response.content)
            st.session_state["counter"] += 1
            # counter_placeholder.write(st.session_state["counter"])
            with st.sidebar:
                counter_placeholder.caption(f"已接收的分块数: {st.session_state['counter']}")

        st.caption(f"🍴 已回答的烹饪问题数: {st.session_state['counter']}")

st.caption("注：结合精选菜谱与网络研究。复杂查询可能需要20-30秒。")