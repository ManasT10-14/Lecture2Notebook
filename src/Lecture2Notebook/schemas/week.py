from pydantic import BaseModel, Field
from typing import List, Dict, Literal

class Week(BaseModel):
    week_id: int = Field(...,description="The week number example 1 for week 1.")# eg: 1 or 2
    week_summary: str = Field(...,description="Summary of the transcription of that particular week.")
    introduced_concepts: List[str] = Field(...,description="What were the new concepts that were introduced in this week if this is not week 1.")
    reinforced_concepts: List[str] = Field(...,description="Concepts that were introduced in earlier weeks or lessons and are "
        "actively reused, applied, or relied upon in this week without being "
        "reintroduced from first principles. These concepts are assumed to be "
        "already understood by the reader and should not be fully re-explained "
        "again. Include a concept here if it appears in equations, code, or "
        "reasoning as a dependency rather than as a new topic.")