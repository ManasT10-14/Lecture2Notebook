from langgraph.graph import START,END,StateGraph
from Lecture2Notebook.pipeline.state import State
from Lecture2Notebook.pipeline.nodes import map_transcripts,route_week,fan_out_week,process_transcript,compile_for_a_week,summary_week,advance_week,route_cell,fan_out_cell,cell_generation,advance_cells_week,build_and_save_notebook,join_cell_generation
from dotenv import load_dotenv
load_dotenv()



def build_graph():
    workflow = StateGraph(state_schema=State)
    workflow.add_node("map_transcripts",map_transcripts)
    workflow.add_node("route_week",route_week)
    workflow.add_node("fan_out_week",fan_out_week)
    workflow.add_node("process_transcript",process_transcript)
    workflow.add_node("compile_for_a_week",compile_for_a_week)
    workflow.add_edge("map_transcripts", "route_week")
    workflow.add_node("summary_week",summary_week)
    workflow.add_node("advance_week", advance_week)
    workflow.add_node("route_cell",route_cell)
    workflow.add_node("fan_out_cell",fan_out_cell)
    workflow.add_node("cell_generation",cell_generation)
    workflow.add_node("advance_cells_week",advance_cells_week)
    workflow.add_node("join_cell_generation",join_cell_generation)
    workflow.add_node("build_and_save_notebook",build_and_save_notebook)
    
    workflow.add_edge(START,"map_transcripts")
    workflow.add_conditional_edges("route_week", fan_out_week, ["process_transcript"])
    workflow.add_edge("process_transcript","compile_for_a_week")
    workflow.add_edge("compile_for_a_week","summary_week")
    workflow.add_edge("summary_week","advance_week")
    workflow.add_conditional_edges("route_cell", fan_out_cell, ["cell_generation"])
    
    workflow.add_edge("cell_generation", "join_cell_generation")
    workflow.add_edge("join_cell_generation", "advance_cells_week")
    

    workflow.add_edge("build_and_save_notebook",END)
    graph = workflow.compile()
    
    return graph