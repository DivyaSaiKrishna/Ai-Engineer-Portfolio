import os

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude, how are you?",
        }
    ],
    model="claude-opus-5-5",
    stream=True,
)

for event in message:
        print(event.type)