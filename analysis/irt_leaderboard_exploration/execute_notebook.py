"""Execute this exploration notebook without requiring Jupyter packages.

The notebook contains plain Python cells only (no magics or rich-display
dependencies), so a small standard-library runner is sufficient for CI-style
top-to-bottom validation and for refreshing its text outputs.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import traceback
from pathlib import Path


DEFAULT_NOTEBOOK = Path(__file__).with_name("irt_leaderboard_exploration.ipynb")


def stream_output(name: str, value: str) -> dict[str, object]:
    return {"name": name, "output_type": "stream", "text": value.splitlines(True)}


def execute_notebook(path: Path) -> int:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__main__"}
    execution_count = 0

    for cell_index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        execution_count += 1
        source = "".join(cell.get("source", []))
        stdout = io.StringIO()
        stderr = io.StringIO()
        outputs: list[dict[str, object]] = []
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exec(
                    compile(source, f"{path.name}:cell-{cell_index}", "exec"),
                    namespace,
                )
        except Exception as exc:
            if stdout.getvalue():
                outputs.append(stream_output("stdout", stdout.getvalue()))
            if stderr.getvalue():
                outputs.append(stream_output("stderr", stderr.getvalue()))
            outputs.append(
                {
                    "ename": type(exc).__name__,
                    "evalue": str(exc),
                    "output_type": "error",
                    "traceback": traceback.format_exc().splitlines(),
                }
            )
            cell["execution_count"] = execution_count
            cell["outputs"] = outputs
            path.write_text(
                json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8",
            )
            raise

        if stdout.getvalue():
            outputs.append(stream_output("stdout", stdout.getvalue()))
        if stderr.getvalue():
            outputs.append(stream_output("stderr", stderr.getvalue()))
        cell["execution_count"] = execution_count
        cell["outputs"] = outputs
        cell.setdefault("metadata", {}).pop("execution", None)

    path.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    return execution_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", nargs="?", type=Path, default=DEFAULT_NOTEBOOK)
    args = parser.parse_args()
    count = execute_notebook(args.notebook.resolve())
    print(f"Executed {count} code cells: {args.notebook.resolve()}")


if __name__ == "__main__":
    main()
