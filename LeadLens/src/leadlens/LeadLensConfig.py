from collections.abc import Iterator

from dotenv import load_dotenv
from anthropic import Anthropic, AsyncAnthropic

load_dotenv()
client = Anthropic()

asyncClient = AsyncAnthropic()

class leadlensconfig:
    
    def __init__(self, model: str, max_tokens: int) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.client = client
        self.last_usage = None
        self.last_stop_reason = None
        
    def ask(self, question: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": question}],
        )
        self.last_usage = message.usage
        self.last_stop_reason = message.stop_reason
        return "".join(block.text for block in message.content if block.type == "text")

    def ask_stream(self, question: str) -> Iterator[str]:
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": question}],
        ) as stream:
            yield from stream.text_stream
            final = stream.get_final_message()
            self.last_usage = final.usage
            self.last_stop_reason = final.stop_reason


        
          
