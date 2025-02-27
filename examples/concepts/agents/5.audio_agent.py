import base64

import requests
from agno.agent import Agent, RunResponse  # noqa
from agno.media import Audio
from agno.models.openai import OpenAIChat

# Fetch the audio file and convert it to a base64 encoded string
url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()
wav_data = response.content

agent = Agent(
    model=OpenAIChat(id="gpt-4o-audio-preview", modalities=["text"]),
    markdown=True,
)
agent.print_response(
    "这个音频里有什么？", audio=[Audio(content=wav_data, format="wav")]
)