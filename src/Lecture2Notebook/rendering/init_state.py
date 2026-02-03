from llm.cache import init_cache_db
from llm.providers.gemini import GeminiProvider
from langchain_google_genai import ChatGoogleGenerativeAI
from llm.cache import SQLiteLLMCache
from config import DB_PATH,MODEL_NAME,TRANSCRIPTS_PATH
def build_initial_state():
    cache = SQLiteLLMCache(db_path=DB_PATH)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
    )

    provider = GeminiProvider()

    return {
        "cache": cache,
        "llm": llm,
        "provider": provider,

        "current_week": 1,
        "weeks": {},
        "lessons": {},
        "lesson_cells": {},

        "transcripts_path": TRANSCRIPTS_PATH,
    }
