from agno.agent import Agent

agent = Agent(
    description="你是一位著名的短篇小说作家，受邀为一家杂志撰稿。",
    instructions=["你是一名飞行员，驾驶飞机从夏威夷飞往日本。"],
    markdown=True,
    debug_mode=True,
)
agent.print_response("告诉我一个两句话的恐怖故事。", stream=True)