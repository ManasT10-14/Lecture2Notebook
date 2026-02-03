# llm/providers/gemini.py
from anthropic import RateLimitError
from Lecture2Notebook.llm.errors import UnifiedRateLimitError
from Lecture2Notebook.llm.providers.base import BaseLLMProvider

class ClaudeProvider(BaseLLMProvider):

    def call(self, llm, messages, schema=None):
        try:
            if schema is not None:
                llm = llm.with_structured_output(schema)
            return llm.invoke(messages)

        except RateLimitError as e:
            raise UnifiedRateLimitError() from e
