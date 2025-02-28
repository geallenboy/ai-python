"""🧠 菜谱专家与知识 - 您的AI泰国烹饪助手！

这个例子展示如何创建一个AI烹饪助手，结合精心挑选的菜谱数据库知识与网络搜索能力。该代理使用包含正宗泰国菜谱的PDF知识库，并能在需要时通过网络搜索补充信息。

示例提示：
- "如何制作正宗的泰式炒河粉（Pad Thai）？"
- "红咖喱和绿咖喱有什么区别？"
- "你能解释什么是高良姜以及可能的替代品吗？"
- "告诉我冬阴功汤的历史"
- "泰国厨房必备的食材有哪些？"
- "如何制作泰式罗勒鸡（Pad Kra Pao）？"

运行 `pip install openai lancedb tantivy pypdf duckduckgo-search agno` 以安装依赖项。
"""

from textwrap import dedent

from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.models.xai import xAI
from agno.models.deepseek import DeepSeek
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv
# --------- 加载API密钥 ---------
import os

# 加载 .env 文件中的环境变量
load_dotenv()
# 从环境变量中加载APIEKY密钥

gemini_api_key=os.getenv("GEMINI_API_KEY")\

if not gemini_api_key:
    print("未找到gemini_api_key密钥。请设置GEMINI_API_KEY环境变量。")
    exit()


# 创建一个具有泰国菜谱知识的菜谱专家代理
agent = Agent(
    model=Gemini(
        id="gemini-2.0-flash-exp",
        api_key=gemini_api_key,
    ),
    instructions=dedent("""\
        你是一个热情且知识渊博的泰国美食专家！🧑‍🍳
        将自己想象成一位温暖、鼓励的烹饪老师、一位泰国美食历史学家和文化大使的结合体。

        回答问题时遵循以下步骤：
        1. 首先搜索知识库中关于正宗泰国菜谱和烹饪信息的内容
        2. 如果知识库中的信息不完整或用户的问题更适合网络搜索，则通过网络搜索补充信息
        3. 如果知识库中已有信息，则无需搜索网络
        4. 对于正宗性，始终优先使用知识库中的信息，而非网络结果
        5. 如有需要，可通过网络搜索补充：
            - 现代改编或食材替代品
            - 文化背景和历史渊源
            - 额外的烹饪技巧和故障排除

        沟通风格：
        1. 每条回复以相关的烹饪表情符号开头
        2. 结构清晰地组织回复：
            - 简短的介绍或背景
            - 主要内容（菜谱、解释或历史）
            - 专业技巧或文化见解
            - 鼓励性的结语
        3. 对于菜谱，包括：
            - 食材清单及可能的替代品
            - 清晰的编号烹饪步骤
            - 成功秘诀和常见陷阱
        4. 使用友好、鼓励的语言

        特别功能：
        - 解释不常见的泰国食材并建议替代品
        - 分享相关的文化背景和传统
        - 提供适应不同饮食需求的菜谱建议
        - 包括搭配建议和配菜

        每条回复以振奋人心的结束语结尾，例如：
        - '祝你烹饪愉快！ขอให้อร่อย（享用你的美食）！'
        - '愿你的泰国烹饪冒险带来欢乐！'
        - '享受你的自制泰国盛宴！'

        记住：
        - 始终通过知识库验证菜谱的正宗性
        - 明确指出信息来自网络来源时
        - 对所有技能水平的家庭厨师保持鼓励和支持\
    """),
    knowledge=PDFUrlKnowledgeBase(
        urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="recipe_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    ),
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True,
    add_references=True,
    debug_mode=True,
)

# 加载知识库后注释掉以下内容
if agent.knowledge is not None:
    agent.knowledge.load()

# agent.print_response(
#     "如何制作椰奶鸡汤和高良姜汤", stream=True
# )
# agent.print_response("泰国咖喱的历史是什么？", stream=True)
# agent.print_response("制作泰式炒河粉需要哪些食材？", stream=True)
agent.print_response("告诉我泰国菜的区域差异", stream=True)
# 更多示例提示：
"""
探索泰国美食的这些查询：
1. "泰国烹饪中必不可少的香料和草药有哪些？"
2. "你能解释泰国不同类型的咖喱酱吗？"
3. "如何制作芒果糯米饭甜点？"
4. "泰国茉莉香米的正确烹饪方法是什么？"
5. "告诉我泰国菜的区域差异"
"""