from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="您是泰国菜专家！",
    instructions=[
        "在您的知识库中搜索泰国食谱。",
        "如果问题更适合在网络上搜索，请在网上搜索以填补空白",
        "与网络搜索结果相比，优先选择您知识库中的信息。"
    ],
    knowledge=PDFUrlKnowledgeBase(
        urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="recipes",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    ),
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True
)

#知识库加载后注释掉
if agent.knowledge is not None:
    agent.knowledge.load()

agent.print_response("如何制作椰奶鸡肉高良姜汤", stream=True)
agent.print_response("泰国咖喱的历史有怎样？",stream=True)
# agent.print_response("Final Chinese output",stream=True)