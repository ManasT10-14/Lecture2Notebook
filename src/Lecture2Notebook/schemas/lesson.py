from pydantic import BaseModel, Field
from typing import List, Dict, Literal

class LessonMemory(BaseModel):
    title: str = Field(...,description="Suitable title for this particular lesson.")
    lesson_id: int = Field(
        ...,
        description="Sequential ID of the lesson. Used only for ordering, not explanation."
    )

    key_concepts: List[str] = Field(
        ...,
        description=(
            "Atomic concepts that must be explained explicitly in the notebook. "
            "Each item should be a short noun phrase, not a sentence. "
            "Do not include examples or explanations here."
        )
    )

    intuitions: List[str] = Field(
        ...,
        description=(
            "High-level mental models or intuitions that help understanding. "
            "Write in simple language. Avoid equations and code."
        )
    )

    equations: List[str] = Field(
        ...,
        description=(
            "Core mathematical equations or symbolic expressions that must appear in markdown. "
            "Use LaTeX-style math where appropriate. Skip derivations."
        )
    )

    code_primitives: List[str] = Field(
        ...,
        description=(
            "Concrete code demonstrations that should be implemented in code cells. "
            "Describe the intent of the code, not the full implementation."
        )
    )

    visual_primitives: List[str] = Field(
        default_factory=list,
        description=(
            "Concepts that should be visualized using diagrams (e.g., Mermaid). "
            "Describe what the diagram should convey, not the diagram syntax."
        )
    )
