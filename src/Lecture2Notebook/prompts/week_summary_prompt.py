from base import PROMPT_HEADER,STRICT_JSON_RULES
from typing import List,Dict,Any


PROMPT_VERSION_WEEK = "week_summary_generation_v1"

SYSTEM_PROMPT_WEEK = """You are an expert in aggregating content. Your task is to analyze the provided data for each lesson of for this week and produce a single Week object."""


def build_week_summary_generation_prompt(
    *,
    lesson_memories: List[Dict[str,Any]],
    previous_week_context: str,
) -> str:
    """
    Build the prompt for generating notebook cells for a lesson.
    """

    return f"""
        {PROMPT_HEADER}
        TASK:
        You are aggregating structured learning content for ONE week of a course.
    
            Your task is to analyze the provided data for each lesson for this week and
            produce a single Week object.

            Focus ONLY on this week.
            Do NOT summarize the entire course.
            Do NOT include lesson-level details.

            Guidelines:
            - Consolidate ideas across lessons.
            - Remove redundancy between lessons.
            - Emphasize conceptual progression within the week.
            - Assume the reader will study lessons in order.

            Concept Classification Rules (VERY IMPORTANT):

            - Introduced concepts:
            Concepts that appear for the FIRST time in this week and are explained or
            defined as new ideas.
            Do NOT include concepts that were introduced in earlier weeks.

            - Reinforced concepts:
            Concepts that were introduced in earlier weeks but are actively reused,
            applied, or relied upon in this week.
            These concepts are NOT reintroduced from first principles in this week.

            - If a concept appears in both prior context and this week:
            - Include it ONLY in reinforced_concepts
            - Do NOT include it in introduced_concepts

            - Do NOT include extremely generic concepts (e.g., "Neural Network",
            "Deep Learning") unless they are the primary focus of the week.

            Week Summary Rules:
            - Write a concise, high-level summary (1-2 short paragraphs).
            - Describe what the learner achieves by the end of the week.
            - Avoid lesson-by-lesson narration.
            - Avoid equations and code.

            Output Rules:
            - Return ONLY valid JSON matching the Week schema.
            - Do NOT include markdown, explanations, or commentary outside the schema.

            Week fields:

            - week_id:
            Use the provided week_id exactly.

            - week_summary:
            A high-level summary of what this week teaches and how the lessons connect.

            - introduced_concepts:
            A list of new concepts introduced in this week.
            Use short noun phrases.
            Limit to the most important concepts only.

            - reinforced_concepts:
            A list of previously introduced concepts that are reused or relied upon
            in this week without full re-explanation.

            Context from previous weeks (if any):
            {previous_week_context}

            LessonMemory objects for this week:
            {lesson_memories}
        
            {STRICT_JSON_RULES}
        """
