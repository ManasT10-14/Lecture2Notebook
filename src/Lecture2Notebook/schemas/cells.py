from pydantic import BaseModel, Field
from typing import List, Dict, Literal
class CellFormat(BaseModel):
    cell_type: Literal["code","markdown"] = Field(
        ...,
        description="Final rendered cell type. Must match the corresponding CellPlan."
    )
    purpose: str = Field(...,description="What is title for this cell.(What is happening here in short.)")

    cell_no: int = Field(
        ...,
        description="Cell index local to the lesson. Will be renumbered during notebook assembly."
    )

    cell_content: str = Field(
        ...,
        description=(
            "Complete content of the cell. "
            "Markdown cells may include LaTeX and Mermaid. "
            "Code cells must be valid, runnable Python."
        )
    )  

class Cells(BaseModel):
    cells: List[CellFormat] 