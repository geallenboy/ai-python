from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file

agent = Agent(
    model=OpenAIChat(
        id="gpt-4o-audio-preview",
        modalities=["text", "audio"], # 支持的模式：文本和音频
        audio={"voice": "alloy", "format": "wav"}, # 音频配置：使用"alloy"语音，wav格式
    ),
    markdown=True,
)
response: RunResponse = agent.run("告诉我一个 5 秒钟的恐怖故事")

# Save the response audio to a file
if response.response_audio is not None:
    write_audio_to_file(
        audio=agent.run_response.response_audio.content, filename="tmp/scary_story.wav"
    )