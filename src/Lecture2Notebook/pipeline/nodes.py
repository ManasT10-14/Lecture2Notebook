from langgraph.types import Command,Send
import nbformat
from typing import Literal,Dict,List,TypedDict,Optional,Annotated,Any
from pathlib import Path
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import os
from langgraph.graph import START,END
from dotenv import load_dotenv
from Lecture2Notebook.pipeline.state import State
from Lecture2Notebook.schemas.lesson import LessonMemory
from Lecture2Notebook.schemas.week import Week
from Lecture2Notebook.schemas.cells import Cells,CellFormat
from Lecture2Notebook.prompts.lesson_prompt import PROMPT_VERSION_LESSON,SYSTEM_PROMPT_LESSON,build_lesson_memory_generation_prompt
from Lecture2Notebook.prompts.week_summary_prompt import PROMPT_VERSION_WEEK,SYSTEM_PROMPT_WEEK,build_week_summary_generation_prompt
from Lecture2Notebook.prompts.cell_generation import PROMPT_VERSION_CELL,build_cell_generation_prompt,SYSTEM_PROMPT_CELL
from Lecture2Notebook.llm.service import call_llm_cached
from Lecture2Notebook.rendering.config import MODEL_NAME
load_dotenv()


def map_transcripts(state:State) -> State:
    transcripts_path = state["transcripts_path"]
    chapters:List = os.listdir(transcripts_path)
    
    file_paths = {}
    for idx,chapter in enumerate(chapters):
        files = [f"{transcripts_path}/{chapter}/{file.name}"  for file in os.scandir(Path(f"{transcripts_path}/{chapter}"))]
        file_paths[idx+1] = files
    print("[MAPPING] Mapping was successful.")
    return {"path":file_paths}

def route_week(state: State) -> State:
    current_week = state["current_week"]
    print(f"[CONTENT CREATION] Processing the week {current_week}")

    transcripts = state["path"][current_week]
    
    return {"current_week_transcripts":transcripts}


def fan_out_week(state: State):
    weeks = state["weeks"]
    return [
        Send(
            "process_transcript",
            {"transcript": transcript, "current_week": state["current_week"],"t_id":id+1,"weeks":weeks,"cache":state["cache"],"llm":state["llm"],"provider":state["provider"]}
        )
        for id,transcript in enumerate(state["current_week_transcripts"])
    ]
    
    
def process_transcript(state: State) -> State:
    
    transcript = state["transcript"]
    week = state["current_week"]
    t_id = state["t_id"]
    with open(transcript,"r") as f:
        content = f.read()
        
    if week == 1:
        week_context = None
    else:
        prev_weeks_content = state["weeks"]
        last_week : Week = prev_weeks_content[week-1]
        week_context = f"""
        Week {week-1} Summary:

        Previously introduced concepts:
        {last_week.introduced_concepts}

        Concepts reinforced in the previous week:
        {last_week.reinforced_concepts}

        Assumptions for this lesson:
        - The reader already understands the above concepts.
        - Do NOT re-explain them from first principles.
        - Only reference them briefly if needed to support new ideas.
        """
        
    prompt = build_lesson_memory_generation_prompt(lesson_transcript=content,previous_week_context=week_context)

    result : LessonMemory = call_llm_cached(
    cache=state["cache"],
    llm=state["llm"],
    provider=state["provider"],
    model_name=MODEL_NAME,
    system_prompt=SYSTEM_PROMPT_LESSON,
    user_prompt=prompt,
    output_schema=LessonMemory,
    prompt_version=PROMPT_VERSION_LESSON,
    )
    result.lesson_id = t_id
    return {"output_week_material":[result]}


def compile_for_a_week(state:State):
    current_week = state["current_week"]
    print(f"[CONTENT CREATION] Processing for week {current_week} was successfull.")
    output_curr_week = state["output_week_material"]
    output = dict(state["lessons"])
    output[current_week] = output_curr_week
    return {
        "lessons": output,"output_week_material":None,"current_week_transcripts":None
    }


def summary_week(state:State) ->State:
    week = state["current_week"]
    print(f"[SUMMARY] Generating summary for week {week}")
    if week == 1:
        week_context = None
    else:
        prev_weeks_content = state["weeks"]
        last_week : Week = prev_weeks_content[week-1]
        week_context = f"""
        Week {week-1} Summary:

        Previously introduced concepts:
        {last_week.introduced_concepts}

        Concepts reinforced in the previous week:
        {last_week.reinforced_concepts}

        Assumptions for this lesson:
        - The reader already understands the above concepts.
        - Do NOT re-explain them from first principles.
        - Only reference them briefly if needed to support new ideas.
        """
    lesson_memories_: LessonMemory = state["lessons"][week]
    updated_lesson_memories = [{"lesson_id":item.lesson_id,"key_concepts":item.key_concepts,"intuitions":item.intuitions} for item in lesson_memories_]
    
    
    prompt = build_week_summary_generation_prompt(lesson_memories=updated_lesson_memories,previous_week_context=week_context)
    
    result : Week = call_llm_cached(
    cache=state["cache"],
    llm=state["llm"],
    provider=state["provider"],
    model_name=MODEL_NAME,
    system_prompt=SYSTEM_PROMPT_WEEK,
    user_prompt=prompt,
    output_schema=Week,
    prompt_version=PROMPT_VERSION_WEEK,
    )
    
    result.week_id = state["current_week"]
    curr_week_summary = state["weeks"]
    curr_week_summary[state["current_week"]] = result
    print(f"[SUMMARY] Summary generation successfully completed.")
    return {"weeks":curr_week_summary}


def advance_week(state: State) -> Command[Literal["route_cell","route_week"]]:
    current_week = state["current_week"]
    if current_week == len(state["path"]):
        print(f"[ROUTING] Processing for all weeks successful moving to the cell generation part.")
        return Command(update={"current_week":1},goto="route_cell")
    else:
        print(f"[ROUTING] Moving to the week {state['current_week']+1}")
        return Command(goto="route_week",update={"current_week": state["current_week"] + 1})
 
def route_cell(state: State) -> State:
    current_week = state["current_week"]
    print(f"[CELL CREATION] Starting cell creation for the week {current_week}")
    lessonMemory_ = state["lessons"].get(current_week, [])
    return {"current_week_cell_transcripts":lessonMemory_}

def fan_out_cell(state: State):
    items = state.get("current_week_cell_transcripts")
    if not items:
        return []
    
    sends = []
    for idx, item in enumerate(items):
        sends.append(
            Send(
                "cell_generation",
            {"lesson_memory": item, "current_week": state["current_week"],"t_id":idx+1,"cache":state["cache"],"llm":state["llm"],"provider":state["provider"]},
            )
        )
    
    
    return sends

def cell_generation(state:State) -> State:
    
    lesson = state["lesson_memory"]
    lesson_id = state["t_id"]
    prompt = build_cell_generation_prompt(lesson_memory=lesson)
    
    result : Cells = call_llm_cached(
    cache=state["cache"],
    llm=state["llm"],
    provider=state["provider"],
    model_name=MODEL_NAME,
    system_prompt=SYSTEM_PROMPT_CELL,
    user_prompt=prompt,
    output_schema=Cells,
    prompt_version=PROMPT_VERSION_CELL,
    )
    
    return {"output_cells_":[{lesson_id:result.cells}]}


def join_cell_generation(state: State) -> State:
    print(f"[CELL GENERATION] Cell generation for week {state['current_week']} was successful.")
    value = state["output_cells_"]
    return {"current_week_cell_transcripts": [],"lesson_cells":{state["current_week"]:value},"output_cells_":None}


def advance_cells_week(
    state: State,
) -> Command[Literal["route_cell", "build_and_save_notebook"]]:
    current_week = state["current_week"]
    total_weeks = len(state["lessons"])

    if current_week == total_weeks:
        print(f"[ROUTING] All weeks processed now moving towards the notebook generation.")
        return Command(goto="build_and_save_notebook")

    else:
        
        next_week = current_week + 1
        print(f"[ROUTING] Moving to the week {next_week}")
        return Command(
            goto="route_cell",
            update={"current_week": state["current_week"]+1}
        )

def build_and_save_notebook(state: State) -> Command:
    lesson_cells = state["lesson_cells"]

    nb = new_notebook(cells=[])

    for week_id in sorted(lesson_cells.keys()):
        nb.cells.append(new_markdown_cell(f"# Week {week_id}"))

  
        lessons_raw = lesson_cells[week_id]

        lessons_in_week: Dict[int, List[CellFormat]] = {}
        for item in lessons_raw:
            lessons_in_week.update(item)

        for lesson_id in sorted(lessons_in_week.keys()):
      
            nb.cells.append(new_markdown_cell(f"## Lesson {lesson_id}"))

            cells_list = lessons_in_week[lesson_id]

            sorted_cells = sorted(cells_list, key=lambda c: c.cell_no)

            for cell in sorted_cells:
       
                if cell.purpose:
                    nb.cells.append(
                        new_markdown_cell(f"**{cell.purpose}**")
                    )

                if cell.cell_type == "markdown":
                    nb.cells.append(
                        new_markdown_cell(cell.cell_content)
                    )

                elif cell.cell_type == "code":
                    nb.cells.append(
                        new_code_cell(cell.cell_content)
                    )

                else:
                    raise ValueError(f"Unknown cell_type: {cell.cell_type}")
    output_dir = Path("generated_notebooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    notebook_path = output_dir / "course_notes.ipynb"
    nbformat.write(nb, notebook_path)

    return Command(
        update={"notebook_path": str(notebook_path)},
        goto=END,
    )