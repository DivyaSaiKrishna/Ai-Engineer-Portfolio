from collections.abc import Iterator

from dotenv import load_dotenv
from anthropic import Anthropic, AsyncAnthropic
from leadlens.LeadLensSchemas import ResearchAnswer
from leadlens.LeadLensPrompts import JSON_SYSTEM_PROMPT, JSON_PROF_SYSTEM_PROMPT
from pydantic import ValidationError

load_dotenv()
client = Anthropic()

asyncClient = AsyncAnthropic()


MAX_TOKENS_LIMIT = 5000


class StructuredOutputError(Exception):
    pass

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0]
    return text.strip()                
class leadlensconfig:
    
    def __init__(self, model: str, max_tokens: int) -> None:
        if not 1 <= max_tokens <= MAX_TOKENS_LIMIT:
            raise ValueError(f"--max-tokens must be between 1 and {MAX_TOKENS_LIMIT}")
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
            
    
    def ask_json(self, question: str) -> ResearchAnswer:
        messages = [{"role": "user", "content": question}]

        for attempt in range(2):
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=JSON_SYSTEM_PROMPT,
                messages=messages,
            )
            self.last_usage = message.usage
            self.last_stop_reason = message.stop_reason
            text = "".join(b.text for b in message.content if b.type == "text")

            try:
                return ResearchAnswer.model_validate_json(_strip_fences(text))
            except ValidationError as e:
                if attempt == 1:
                    raise StructuredOutputError(f"Invalid JSON after retry: {e}") from e
                messages += [
                    {"role": "assistant", "content": text},
                    {"role": "user", "content": f"Your reply was not valid. Errors:\n{e}\n"
                                                 "Reply again with ONLY the corrected JSON."},
                ]
        raise AssertionError("unreachable")


    def ask_prof(self, question: str) -> ResearchAnswer:
        messages = [{"role": "user", "content": question}]

        for attempt in range(2):
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=JSON_PROF_SYSTEM_PROMPT,
                messages=messages,
            )
            self.last_usage = message.usage
            self.last_stop_reason = message.stop_reason
            text = "".join(b.text for b in message.content if b.type == "text")

            try:
                return ResearchAnswer.model_validate_json(_strip_fences(text))
            except ValidationError as e:
                if attempt == 1:
                    raise StructuredOutputError(f"Invalid JSON after retry: {e}") from e
                messages += [
                    {"role": "assistant", "content": text},
                    {"role": "user", "content": f"Your reply was not valid. Errors:\n{e}\n"
                                                 "Reply again with ONLY the corrected JSON."},
                ]
        raise AssertionError("unreachable")


        
          
