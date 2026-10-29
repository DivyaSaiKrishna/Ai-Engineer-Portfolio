

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

class leadlensconfig:
    
    def __init__(self, model: str, max_tokens: int) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.client = client
        
    def ask(self, question: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": question}],
        )
        return "".join(block.text for block in message.content if block.type == "text")


        
          
