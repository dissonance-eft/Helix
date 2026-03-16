# HIL Validator — Phase 10
# Validates parsed HIL command dicts against schema constraints.

from .grammar import HIL_SCHEMA, GRAPH_SUBCOMMANDS

# Commands that are structurally destructive and must always be rejected
BLOCKED_PATTERNS = (
    "rm ", "rm\t", "mkfs", "dd ", "sudo rm",
    "DROP ", "DELETE FROM", "> /dev/",
)


def validate_command(cmd: dict) -> dict:
    """
    Validate a parsed HIL command against the schema.
    Returns dict: {"valid": bool, "error": str | None}
    """
    # Reject blocked shell patterns — check raw verb+target string
    raw = f"{cmd.get('verb', '')} {cmd.get('target', '')}".strip()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in raw.lower():
            return {"valid": False, "error": f"HIL_VALIDATION_ERROR: blocked pattern '{pattern.strip()}'"}

    verb = cmd.get("verb", "").lower()
    if not verb:
        return {"valid": False, "error": "HIL_VALIDATION_ERROR: empty command"}

    if verb not in HIL_SCHEMA:
        return {"valid": False, "error": f"HIL_VALIDATION_ERROR: unknown verb '{verb}'"}

    schema   = HIL_SCHEMA[verb]
    required = schema.get("required", [])

    for field in required:
        if field == "target" and not cmd.get("target"):
            return {"valid": False, "error": f"HIL_VALIDATION_ERROR: verb '{verb}' requires a target"}
        elif field != "target" and field not in cmd.get("params", {}):
            return {"valid": False, "error": f"HIL_VALIDATION_ERROR: verb '{verb}' requires param '{field}'"}

    # GRAPH subcommand validation (Phase 10)
    if verb == "graph":
        target = (cmd.get("target") or "").lower()
        if target not in GRAPH_SUBCOMMANDS:
            return {
                "valid": False,
                "error": f"HIL_VALIDATION_ERROR: unknown GRAPH subcommand '{target}'. "
                         f"Valid: {sorted(GRAPH_SUBCOMMANDS)}",
            }

    return {"valid": True, "error": None}
