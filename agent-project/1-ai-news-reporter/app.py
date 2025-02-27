# app/main.py
import os
from typing import Iterator
import streamlit as st
from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat

# 从环境变量加载 OpenAI API 密钥
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("未找到 OpenAI API 密钥。请设置 OPENAI_API_KEY 环境变量。")
    st.stop()

# 设置 Streamlit 应用
st.title("🌐AI新闻记者")
st.write("🎉 🎉 🎉 欢迎搜索体验AI新闻记者！给你不一样的新闻体验🔥🔥🔥")

counter_placeholder = st.empty()
if "counter" not in st.session_state:
    st.session_state["counter"] = 0
st.session_state["counter"] += 1
counter_placeholder.write(st.session_state["counter"])

# 创建代理
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),
    instructions=dedent("""\
        你是一个充满热情的新闻记者，擅长把新闻内容讲丰富多彩，简单易懂！🗽
        把自己想象成一个专业，有趣，幽默记者的混合体。

        你的风格指南：
        - 用带表情符号的引人注目的标题开头
        - 带着热情和分享新闻
        - 保持回答简洁但有趣
        - 以响亮的结束语结尾”

        记得验证所有事实，实事求是，真是有料！\
    """),
    markdown=True,
)

# 用户输入
prompt = st.text_input("向记者询问新闻内容（例如，‘中国有什么新鲜事？’）")

# 生成并显示回答
if prompt:
    with st.spinner("正在获取最新消息..."):
        stream = False 
        if stream:
            run_response: Iterator[RunResponse] = agent.run(prompt, stream=True)
            response = ""
            text_placeholder = st.empty()
            for chunk in run_response:
                response += chunk.content
                text_placeholder.markdown(response)
                st.session_state["counter"] += 1
                counter_placeholder.write(st.session_state["counter"])
        else:
            response = agent.run(prompt, stream=False)
            response = response.content
            st.write(response)