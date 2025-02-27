from typing import List #从typing模块导入List，用于类型注解，表示列表类型。
from rich.pretty import pprint #从rich库导入pprint，用于美化打印输出（类似print，但格式更友好）。
from pydantic import BaseModel, Field #从pydantic库导入，用于定义结构化数据模型和字段。
from agno.agent import Agent, RunResponse #从agno库导入Agent（智能代理类）和RunResponse（运行响应的返回类型）。
from agno.models.openai import OpenAIChat #导入OpenAI的聊天模型接口。

# 作用：这个模型定义了电影脚本的结构，确保输出符合预期的格式。
class MovieScript(BaseModel):
    setting: str = Field(..., description="为一部大片提供一个精彩的场景设定。")
    ending: str = Field(..., description="电影的结局。如果没有提供，则提供一个幸福结局。")
    genre: str = Field(
        ..., description="电影的类型。如果没有提供，从动作片、惊悚片或浪漫喜剧中选择。"
    )
    name: str = Field(..., description="给这部电影取一个名字。")
    characters: List[str] = Field(..., description="这部电影中角色的名字。")
    storyline: str = Field(..., description="电影的3句话剧情概要。让它令人兴奋！")

# Agent that uses JSON mode
# 创建一个代理，用于生成电影脚本，输出为JSON格式。
json_mode_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="你编写电影脚本。",
    response_model=MovieScript,
)
# Agent that uses structured outputs
# 与json_mode_agent类似，但使用结构化输出模式。
structured_output_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="你编写电影脚本。",
    response_model=MovieScript,
    structured_outputs=True,
)

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)
# structured_output_response: RunResponse = structured_output_agent.run("New York")
# pprint(structured_output_response.content)

json_mode_agent.print_response("北京")
structured_output_agent.print_response("北京")

#工作流程
#输入：用户提供"New York"作为提示（可能暗示电影设定）。
#处理：
#两个代理基于gpt-4o模型生成电影脚本。
#根据MovieScript模型，输出包括设定、结局、类型、名字、角色和剧情。
#输出：
#json_mode_agent：返回JSON格式的脚本。
#structured_output_agent：返回结构化格式的脚本（可能更优化）。
#展示：通过print_response直接打印。