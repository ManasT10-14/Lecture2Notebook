from typing import Dict,List,Any,Optional,Literal,TypedDict,Annotated
from schemas.lesson import LessonMemory
from schemas.week import Week
from schemas.cells import Cells,CellFormat
from operator import add



def resettable_add(old: List[str], new: Optional[List[str]]):
    if new is None:
        return []
    return old + new    

class State(TypedDict):
    transcripts_path : str
    path: Dict[int,List[str]]
    current_week: int    
    weeks: Dict[int,Week]   
    lessons: Dict[int,List[LessonMemory]]
    current_week_transcripts: Annotated[List[str],resettable_add] # for getting the transcripts of that particular week
    output_week_material: Annotated[List[str],resettable_add] # for updating the output with the current weeks output. 
    lesson_cells: Dict[int,Dict[int,Annotated[List[CellFormat],add]]]
    current_lesson: int
    notebook_path: str
    cache: Any
    llm : Any
    provider : Any