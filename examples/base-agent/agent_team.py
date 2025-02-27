from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
    name="Web Agent",
    role="搜索网络信息",
    model=OpenAIChat(id="gpt-4o"), #使用OpenAI的gpt-4o模型作为核心语言模型。
    tools=[DuckDuckGoTools()], #集成了DuckDuckGoTools，用于从网络搜索信息。
    instructions="要求始终包含信息来源。",
    show_tool_calls=True,
    markdown=True
)

finance_agent = Agent(
    name="Finance Agent",
    role="获取财务数据",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True,analyst_recommendations=True,company_info=True)],#从Yahoo Finance获取AI半导体公司的财务数据。
    instructions="要求使用表格展示数据。",
    show_tool_calls=True,
    markdown=True

)

agent_team = Agent(
    team=[web_agent, finance_agent], # 将web_agent和finance_agent组合成一个代理团队。
    model=OpenAIChat(id="gpt-4o"),
    instructions=["要求始终包含信息来源。", "要求使用表格展示数据。"], # 团队指令包括“始终包含来源”和“使用表格展示数据”。
    show_tool_calls=True,
    markdown=True
)

agent_team.print_response("AI半导体公司的市场前景和财务表现如何？", stream=True)