from textwrap import dedent  # 用于去除多行字符串的缩进
from agno.agent import Agent  # 引入 Agent 类，用于创建智能体
from agno.tools.serpapi import SerpApiTools  # 引入 SerpApi 工具，用于网页搜索
import streamlit as st  # 引入 Streamlit，用于构建 Web 应用
from agno.models.openai import OpenAIChat  # 引入 OpenAI 模型 GPT-4o

st.title("AI Personal Finance Planner 💰")
st.caption("使用 GPT-4o 创建个性化的预算、投资计划和储蓄策略，轻松管理你的财务")
# 让用户输入 OpenAI API 密钥（用于 GPT-4o 模型）
openai_api_key = st.text_input("请输入 OpenAI API 密钥（用于 GPT-4o）", type="password")

# 让用户输入 SerpAPI 密钥（用于网页搜索功能）
serp_api_key = st.text_input("请输入 SerpAPI 密钥（用于搜索功能）", type="password")

if openai_api_key and serp_api_key:
    researcher = Agent(
        name="Researcher",  # 名称：研究员
        role="根据用户偏好搜索财务建议、投资机会和储蓄策略",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),  # 使用 GPT-4o 模型
        description=dedent(
            """\
            你是世界级的财务研究员。根据用户的财务目标和当前财务状况，
            生成搜索关键词，寻找相关的建议和策略，并返回10个最相关的结果。
            """
        ),
        instructions=[
            "根据用户的目标，生成3个搜索关键词。",
            "用 `search_google` 搜索每个关键词并分析结果。",
            "从所有结果中提取出10条最相关的内容返回给用户。",
            "注意：结果的质量很重要。",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],  # 使用 SerpApi 搜索工具
        add_datetime_to_instructions=True,  # 添加当前时间信息，增加上下文
    )
    planner = Agent(
        name="Planner",  # 名称：规划师
        role="根据用户偏好和研究结果生成个性化财务计划",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent(
            """\
            你是一位高级财务规划师。根据用户的财务目标、当前状况和研究结果，
            制定一个个性化的财务规划。
            """
        ),
        instructions=[
            "结合用户的目标、现状和搜索结果，制定预算、投资和储蓄计划。",
            "确保规划结构清晰、内容丰富、语言有吸引力。",
            "提供平衡和有根据的建议，引用相关事实。",
            "不要编造信息，也不要抄袭，确保高质量。",
        ],
        add_datetime_to_instructions=True,
    )
    financial_goals = st.text_input("你的财务目标是什么？")
    current_situation = st.text_area("请描述你目前的财务状况")
    if st.button("生成财务规划"):
        with st.spinner("正在生成财务计划，请稍候..."):
            # 调用 planner Agent 生成响应（非流式返回）
            response = planner.run(
                f"Financial goals: {financial_goals}, Current situation: {current_situation}",
                stream=False
            )
            # 显示结果
            st.write(response.content)