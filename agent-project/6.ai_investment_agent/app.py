# 导入所需的库
import streamlit as st                      # 用于构建 Web 应用的库
from agno.agent import Agent            # Agno 框架中的智能助手类
from agno.models.openai import OpenAIChat   # 用于调用 OpenAI 模型的类
from agno.tools.yfinance import YFinanceTools  # 用于获取股票数据的工具


# 设置 Streamlit 应用的标题和描述
st.title("AI 投资助手 📈🤖")
st.caption("本应用可以对比两只股票的表现并生成详细报告。")


# Get OpenAI API key from user
openai_api_key = st.text_input("OpenAI API Key", type="password")

if openai_api_key:
    # 创建 agent 实例，指定使用 GPT-4o 模型 和 YFinance 工具
    agent = Agent(
 
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),   # 使用 GPT-4o 模型
        tools=[
            YFinanceTools(
                stock_price=True,                      # 获取股价
                analyst_recommendations=True,          # 获取分析师建议
                company_info=True,                     # 获取公司信息
                company_news=True                      # 获取公司新闻
            )
        ],
        show_tool_calls=True,   # 显示使用了哪些工具（方便调试或教学）
    )


        # 用户输入两只要对比的股票代码
    stock1 = st.text_input("请输入第一只股票的代码")
    stock2 = st.text_input("请输入第二只股票的代码")


    if stock1 and stock2:
        # 构造查询语句，告诉 AI 要对比这两只股票，使用所有可用工具
        query = f"Compare {stock1} to {stock2}. Use every tool you have."
        
        # 向 AI 助手发送查询，请求结果（stream=False 表示一次性返回，不是流式输出）
        response = agent.run(query, stream=False)
        
        # 显示返回内容
        st.write(response.content)

