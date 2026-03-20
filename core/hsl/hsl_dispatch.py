"""
HIL Dispatch — Helix CLI entry point
=====================================
Routes HIL commands:
  ENTITY / GRAPH / SUBSTRATE / ANALYZE  → HILInterpreter (core.hsl/interpreter.py)
  All other verbs                        → legacy kernel Dispatcher

Called by the `helix` shell wrapper:
  ./helix "ENTITY get music.composer:jun_senoue"
  ./helix "SUBSTRATE list"
  ./helix "PROBE invariant:decision_compression"
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Verbs handled by the new interpreter
_INTERPRETER_VERBS = frozenset({"ENTITY", "GRAPH", "SUBSTRATE", "ANALYZE"})


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: helix \"HIL COMMAND\"")
        print()
        print("Examples:")
        print("  helix \"ENTITY get music.composer:jun_senoue\"")
        print("  helix \"SUBSTRATE list\"")
        print("  helix \"GRAPH neighbors music.composer:jun_senoue\"")
        print("  helix \"PROBE invariant:decision_compression\"")
        sys.exit(1)

    raw_command = " ".join(sys.argv[1:])
    print(f"[helix] {raw_command}")

    first_word = raw_command.strip().split()[0].upper() if raw_command.strip() else ""

    if first_word in _INTERPRETER_VERBS:
        result = _run_interpreter(raw_command)
    else:
        result = _run_dispatcher(raw_command)

    _print_result(result)
    _save_result(result)

    if result.get("status") not in ("ok", "validated", "not_found"):
        sys.exit(1)


def _run_interpreter(raw: str) -> dict:
    from core.hsl.interpreter import run_command
    return run_command(raw)


def _run_dispatcher(raw: str) -> dict:
    from core.hsl import dispatch
    try:
        from core.kernel.dispatcher.router import Dispatcher
        dispatcher = Dispatcher()
    except Exception:
        dispatcher = None
    try:
        return dispatch(raw, dispatcher=dispatcher)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def _print_result(result: dict) -> None:
    status = result.get("status", "unknown")
    print()
    if status == "ok":
        data = result.get("data", {})
        print("  status: ok")
        if isinstance(data, dict):
            if "substrates" in data:
                print(f"  substrates: {data['substrates']}")
            elif "count" in data:
                print(f"  count: {data['count']}")
            elif "id" in data:
                print(f"  entity: {data['id']}  ({data.get('type', '?')})")
            elif "neighbors" in data:
                print(f"  neighbors: {len(data['neighbors'])}")
                for n in data["neighbors"][:10]:
                    print(f"    {n['id']}  [{n['edge_type']}]")
            elif "edges_out" in data:
                print(f"  edges out: {len(data['edges_out'])}  in: {len(data['edges_in'])}")
            elif "path" in data:
                print(f"  reachable: {data['reachable']}  path: {data.get('path')}")
            else:
                print(f"  data: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"  data: {data}")
    elif status == "not_found":
        print(f"  status: not_found")
        print(f"  error:  {result.get('error', '')}")
    elif status == "validated":
        print(f"  status: validated")
        print(f"  canonical: {result.get('canonical', '')}")
    else:
        print(f"  status: {status}")
        err = result.get("error") or result.get("message", "")
        print(f"  error:  {err}")


def _save_result(result: dict) -> None:
    log_dir = REPO_ROOT / "artifacts"
    log_dir.mkdir(exist_ok=True)
    try:
        with open(log_dir / "last_hil_run.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
    except Exception:
        pass


if __name__ == "__main__":
    main()
