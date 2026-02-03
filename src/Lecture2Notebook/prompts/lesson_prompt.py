from Lecture2Notebook.prompts.base import PROMPT_HEADER,STRICT_JSON_RULES

PROMPT_VERSION_LESSON = "lesson_generation_v1"

SYSTEM_PROMPT_LESSON = """You are an expert in extracting structured learning memory from a single transcript of a lesson. Do it as the user says. Maintain the proper format and see that the content is very much relevant."""


def build_lesson_memory_generation_prompt(
    *,
    lesson_transcript: str,
    previous_week_context: str,
) -> str:
    """
    Build the prompt for generating notebook cells for a lesson.
    """

    return f"""
        {PROMPT_HEADER}
        TASK:
        You are extracting structured learning memory from a single lesson transcript.

        Your task is to convert the provided transcript into a LessonMemory object.
        Focus ONLY on this lesson. Do NOT summarize the entire course or the entire week.

        Guidelines:
        - Extract atomic concepts, not explanations.
        - Separate intuition from equations and code.
        - Do NOT invent content that does not appear in the transcript.
        - Do NOT repeat definitions that are explicitly stated as previously covered.
        - Assume the reader has access to prior weeks' summaries if provided.

        Diagram Rules (IMPORTANT):
        - Generate Mermaid diagrams ONLY when a visual representation significantly improves understanding.
        - Use diagrams for:
        - data flow
        - algorithm steps
        - architectural relationships
        - process pipelines
        - Do NOT create diagrams for simple lists or trivial concepts.
        - Mermaid code must be valid and self-contained.
        - Prefer simple Mermaid types:
        - flowchart
        - sequenceDiagram
        - graph TD

        Output Rules:
        - Return ONLY valid JSON matching the LessonMemory schema.
        - Do NOT include markdown, commentary, or explanations outside the schema.
        - Do NOT generate notebook cells or formatting.

        LessonMemory fields:

        - lesson_id:
        Use the provided lesson_id exactly.

        - week_id:
        Use the provided week_id exactly.

        - title:
        Short descriptive title for this lesson.

        - key_concepts:
        List of atomic concepts introduced or used in this lesson.
        Each item must be a short noun phrase (2-5 words).
        Do NOT include explanations, examples, or verbs.

        - intuitions:
        High-level mental models that help understanding.
        Use simple language.
        Avoid equations, symbols, or code.

        - equations:
        Core mathematical expressions that appear in the lesson.
        Use LaTeX-style math when appropriate.
        Skip derivations.

        - code_primitives:
        Describe concrete coding demonstrations or implementations shown or discussed.
        Focus on intent, not full code.

        - visual_primitives:
        A list of Mermaid diagram definitions as strings.
        Each item must contain ONLY valid Mermaid syntax.
        Do NOT wrap diagrams in markdown code fences.
        Do NOT include explanations or comments.

        RULES:
        1. Limit key_concepts to the 8-12 most important concepts for this lesson.
        If more concepts appear, prioritize those that are central to learning objectives.
        2. Do NOT include:
            - historical anecdotes
            - personal advice
            - meta commentary
        unless they introduce a technical concept.
        
        Context from previous weeks (if any):
        {previous_week_context}

        Lesson transcript:
        {lesson_transcript}
        
        {STRICT_JSON_RULES}
        """
