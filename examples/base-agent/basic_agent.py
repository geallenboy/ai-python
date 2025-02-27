from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="您是一位热情的新闻记者，并且擅长讲故事！",
    markdown=True
)
agent.print_response("告诉我一个来自纽约的突发新闻。", stream=True)