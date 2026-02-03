import argparse
from pathlib import Path

from Lecture2Notebook.pipeline.graph import build_graph
from Lecture2Notebook.rendering.init_state import build_initial_state


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert lecture transcripts into structured Jupyter notebooks."
    )

    parser.add_argument(
        "--transcripts",
        type=Path,
        required=True,
        help="Path to transcripts directory (e.g. data/transcripts)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="LLM model to use",
    )


    return parser.parse_args()


def main():
    args = parse_args()


    if not args.transcripts.exists():
        raise FileNotFoundError(f"Transcripts path does not exist: {args.transcripts}")


    initial_state = build_initial_state(
        transcripts_path=str(args.transcripts),
        model_name=args.model,
    )

    graph = build_graph()
    final_state = graph.invoke(initial_state)

    notebook_path = final_state.get("notebook_path")
    print(f"\nNotebook successfully generated at:\n{notebook_path}")

    return final_state


if __name__ == "__main__":
    main()
