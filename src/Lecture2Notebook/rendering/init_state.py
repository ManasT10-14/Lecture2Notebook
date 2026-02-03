from Lecture2Notebook.llm.providers.gemini import GeminiProvider
from Lecture2Notebook.llm.providers.claude import ClaudeProvider
from langchain_google_genai import ChatGoogleGenerativeAI
from Lecture2Notebook.llm.cache import SQLiteLLMCache
from Lecture2Notebook.rendering.config import DB_PATH,MODEL_NAME,TRANSCRIPTS_PATH
from langchain_anthropic import ChatAnthropic
def build_initial_state(*,transcripts_path = TRANSCRIPTS_PATH,
    model_name = MODEL_NAME):
    
    cache = SQLiteLLMCache(db_path=DB_PATH)

    # llm = ChatGoogleGenerativeAI(
    #     model=model_name,
    #     temperature=0.0,
    # )
    llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0.2
    )

    provider = ClaudeProvider()

    return {
        "cache": cache,
        "llm": llm,
        "provider": provider,

        "current_week": 1,
        "weeks": {},
        "lessons": {},
        "lesson_cells": {},

        "transcripts_path": transcripts_path,
    }
