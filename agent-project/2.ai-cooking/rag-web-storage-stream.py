"""🧠 具有存储功能的食谱专家 - 您的AI泰国烹饪助手！

此示例展示了如何创建一个AI烹饪助手，它结合了精选食谱数据库的知识和网络搜索功能。该代理使用正宗泰国食谱的PDF知识库，
并在需要时可以通过网络搜索补充这些信息。

可以尝试的示例提示：
- "如何制作正宗的泰式炒河粉？"
- "红咖喱和绿咖喱有什么区别？"
- "你能解释一下高良姜是什么以及可能的替代品吗？"
- "告诉我冬阴功汤的历史"
- "泰国厨房必备的食材有哪些？"
- "如何制作泰式罗勒鸡（Pad Kra Pao）？"

运行 `pip install openai lancedb tantivy pypdf duckduckgo-search sqlalchemy agno` 安装依赖项。
"""

from textwrap import dedent
from typing import List, Optional

import typer
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType
from rich import print
from dotenv import load_dotenv
# --------- 加载API密钥 ---------
import os
# 加载 .env 文件中的环境变量
load_dotenv()
# 从环境中加载OpenAI API密钥
openai_api_key = os.getenv("OPENAI_API_KEY")
print(openai_api_key)
# if not openai_api_key:
    # st.error("未找到OpenAI API密钥。请设置OPENAI_API_KEY环境变量。")
    # st.stop()


agent_knowledge = PDFUrlKnowledgeBase(
    urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="recipe_knowledge",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)
# 知识库加载后注释掉
if agent_knowledge is not None:
    agent_knowledge.load()

agent_storage = SqliteAgentStorage(table_name="recipe_agent", db_file="tmp/agents.db")


def recipe_agent(user: str = "user"):
    session_id: Optional[str] = None

    # 询问用户是否要开始新会话或继续现有会话
    new = typer.confirm("您是否要开始新会话？")

    if not new:
        existing_sessions: List[str] = agent_storage.get_all_session_ids(user)
        if len(existing_sessions) > 0:
            session_id = existing_sessions[0]

    agent = Agent(
        user_id=user,
        session_id=session_id,
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=dedent("""\
            您是一位热情且知识渊博的泰国菜专家！🧑‍🍳
            把自己想象成热情鼓励的烹饪教师、
            泰国美食历史学家和文化大使的结合体。

            回答问题时请遵循以下步骤：
            1. 首先，在知识库中搜索正宗泰国食谱和烹饪信息
            2. 如果知识库中的信息不完整，或者用户提出的问题更适合在网络上搜索，则搜索网络以填补信息空白
            3. 如果在知识库中找到信息，则无需搜索网络
            4. 为了保证真实性，始终优先考虑知识库信息而非网络搜索结果
            5. 如有需要，通过网络搜索补充以下内容：
               - 现代改编或食材替代品
               - 文化背景和历史背景
               - 额外的烹饪技巧和问题排解

            沟通风格：
            1. 每个回复都以相关的烹饪表情符号开始
            2. 清晰地构建您的回复：
               - 简短的介绍或背景
               - 主要内容（食谱、解释或历史）
               - 专业提示或文化见解
               - 鼓励性结论
            3. 对于食谱，包括：
               - 食材清单及可能的替代品
               - 清晰、编号的烹饪步骤
               - 成功技巧和常见陷阱
            4. 使用友好、鼓励的语言

            特殊功能：
            - 解释不熟悉的泰国食材并提供替代品建议
            - 分享相关的文化背景和传统
            - 提供调整食谱以满足不同饮食需求的技巧
            - 包括上菜建议和配菜

            以振奋人心的告别语结束每个回复，如：
            - '烹饪愉快！ขอให้อร่อย（享用您的美食）！'
            - '愿您的泰国烹饪冒险带来欢乐！'
            - '享受您的自制泰国盛宴！'

            请记住：
            - 始终使用知识库验证食谱的真实性
            - 明确指出信息来自网络来源的情况
            - 鼓励和支持各种技能水平的家庭烹饪者\
        """),
        storage=agent_storage,
        knowledge=agent_knowledge,
        tools=[DuckDuckGoTools()],
        # 在响应中显示工具调用
        show_tool_calls=True,
        # 为代理提供聊天历史记录
        # 我们可以：
        # 1. 为代理提供读取聊天历史的工具
        read_chat_history=True,
        # 2. 自动将聊天历史添加到发送给模型的消息中
        add_history_to_messages=True,
        # 添加到消息中的历史响应数量
        num_history_responses=3,
        markdown=True,
    )

    print("您即将与代理聊天！")
    if session_id is None:
        session_id = agent.session_id
        if session_id is not None:
            print(f"已开始会话：{session_id}\n")
        else:
            print("已开始会话\n")
    else:
        print(f"正在继续会话：{session_id}\n")

    # 将代理作为命令行应用程序运行
    agent.cli_app(markdown=True)


if __name__ == "__main__":
    typer.run(recipe_agent)