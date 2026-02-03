from pipeline.graph import build_graph
from init_state import build_initial_state

def run_pipeline():
    initial_state = build_initial_state()
    graph = build_graph()
    final_state = graph.invoke(initial_state)


    notebook_path = final_state.get("notebook_path")
    if notebook_path:
        print(f"\nNotebook successfully generated at:\n{notebook_path}")
    else:
        print("\nPipeline finished, but no notebook path was returned.")

    print(final_state)
    return final_state


if __name__ == "__main__":
    run_pipeline()
