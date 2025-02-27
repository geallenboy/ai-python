from pathlib import Path

from agno.agent import Agent
from agno.media import Video
from agno.models.google import Gemini
import os
# Load OpenAI API key from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")
agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    markdown=True,
)

# Please download "GreatRedSpot.mp4" using
# wget https://storage.googleapis.com/generativeai-downloads/images/GreatRedSpot.mp4
video_path = Path(__file__).parent.joinpath("GreatRedSpot.mp4")

print(f"Video path: {video_path}")
print(f"File exists: {video_path.exists()}")

agent.print_response("请分析这个视频的内容", videos=[Video(filepath=video_path)])