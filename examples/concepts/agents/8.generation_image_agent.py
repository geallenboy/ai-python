from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.dalle import DalleTools

image_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DalleTools()],
    description="你是一个可以使用 DALL-E 生成图像的 AI 代理。",
    instructions="当用户要求你创建图像时，使用`create_image`工具来生成图像。",
    markdown=True,
    show_tool_calls=True,
)

image_agent.print_response("生成一张重庆大熊猫的图像")

images = image_agent.get_images()
print("images:",images)
if images and isinstance(images, list):
    for image_response in images:
        image_url = image_response.url
        print(image_url)