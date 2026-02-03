from base import PROMPT_HEADER,STRICT_JSON_RULES
from typing import List,Dict,Any


PROMPT_VERSION = "cell_generation_v1"

SYSTEM_MESSAGE_CELL = """You are generating notebook cells for a SINGLE lesson in a Jupyter notebook.
You are NOT allowed to decide the structure of the notebook.
You MUST follow the provided CellPlan EXACTLY.
Your task is ONLY to fill in the content of each cell.
"""

def build_cell_plan(lesson) -> list[dict]:
    """
    Build a deterministic CellPlan from a LessonMemory object.
    Returns a list of CellPlanItem dicts.
    """
    plan = []
    cell_no = 1


    plan.append({
        "cell_no": cell_no,
        "cell_type": "markdown",
        "purpose": "Explain the core concepts of the lesson"
    })
    cell_no += 1

  
    plan.append({
        "cell_no": cell_no,
        "cell_type": "markdown",
        "purpose": "Explain intuitions and mental models for the lesson"
    })
    cell_no += 1

 
    if lesson.equations:
        plan.append({
            "cell_no": cell_no,
            "cell_type": "markdown",
            "purpose": "Present and explain the key equations used in the lesson"
        })
        cell_no += 1


    for i, primitive in enumerate(lesson.code_primitives):
        plan.append({
            "cell_no": cell_no,
            "cell_type": "code",
            "purpose": f"Implement code primitive: {primitive}"
        })
        cell_no += 1


    for i, visual in enumerate(lesson.visual_primitives):
        plan.append({
            "cell_no": cell_no,
            "cell_type": "markdown",
            "purpose": f"Create a Mermaid diagram: {visual}"
        })
        cell_no += 1

    return plan





def build_cell_generation_prompt(
    *,
    lesson,
    lesson_memory,
) -> str:
    """
    Build the prompt for generating notebook cells for a lesson.
    """

    cell_schema = """{
    "cells": [
      {
        "cell_type": "markdown" | "code",
        "purpose": "<string>",
        "cell_no": <integer>,
        "cell_content": "<string>"
      }
    ]
    }"""
    cell_plan = build_cell_plan(lesson=lesson)
    return f"""
        {PROMPT_HEADER}
        TASK:
        You will be given:
        1. A LessonMemory object (ground truth)
        2. A CellPlan that defines EXACTLY which cells to generate and in what order

        You MUST:
        - Generate exactly the same number of cells as in the CellPlan
        - Match each cell's type (markdown or code) EXACTLY
        - Follow the order strictly
        - NOT add, remove, merge, or reorder cells

        --------------------------------------------------
        CELLPLAN (DO NOT MODIFY):
        {cell_plan}
        --------------------------------------------------

        LESSONMEMORY (GROUND TRUTH — DO NOT INVENT):
        {lesson_memory}
        --------------------------------------------------

        GENERAL RULES (MANDATORY):

        1. STRUCTURE
        - Output MUST be valid JSON that matches this schema:
        {cell_schema}

        - Do NOT include explanations outside the JSON
        - Do NOT wrap JSON in markdown fences

        2. CONCEPT GROUNDING
        - You may ONLY use concepts explicitly present in LessonMemory
        - Do NOT introduce new concepts, terminology, or topics
        - If something is unclear, OMIT it rather than guessing

        3. MARKDOWN CELLS
        - Use clear pedagogical language
        - Include formulas using LaTeX ($ ... $ or $$ ... $$) when applicable
        - Do NOT include code blocks in markdown cells unless explicitly asked
        - Do NOT include headings that imply lesson structure (e.g., "Lesson Overview")

        4. FORMULAS
        - All mathematical expressions MUST be written in valid LaTeX
        - Prefer display equations ($$ ... $$) for important formulas
        - Do NOT include derivations unless explicitly present in LessonMemory

        5. CODE CELLS
        - Code MUST be valid, runnable Python
        - Keep code minimal and focused on the stated purpose
        - Do NOT add explanatory comments outside the code
        - Do NOT import unnecessary libraries
        - Do NOT use external datasets or files

        6. MERMAID DIAGRAMS (VERY IMPORTANT)
        - Mermaid diagrams MUST appear ONLY inside markdown cells
        - Mermaid diagrams MUST be wrapped EXACTLY like this:

        ```mermaid
        graph TD
            A --> B
            B --> C
            
        - Mermaid code MUST:

        - span multiple lines

        - use proper indentation

        - NOT be written on a single line

        - NOT include inline explanations

        7. CELL CONTENT ONLY

        - Each cell_content MUST contain ONLY the content of that cell

        - Do NOT include markdown fences for the whole cell

        - Do NOT include cell titles like "Cell 1", "Code Cell", etc.

        8. FAILURE POLICY

        - If you cannot generate a cell correctly, generate an EMPTY string for its content

        - Do NOT hallucinate to fill missing information

               
        {STRICT_JSON_RULES}
        
        NOW GENERATE THE CELLS. 
        """
