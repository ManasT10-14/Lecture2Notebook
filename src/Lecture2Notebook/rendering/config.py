from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

TRANSCRIPTS_PATH = BASE_DIR / "data" / "transcripts"
MODEL_NAME = "gemini-2.5-flash"
DB_PATH = BASE_DIR/"data"/"cache_data"/"llm_cache.db"
