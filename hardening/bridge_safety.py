"""Safety checks for the two dangerous operations: run_geoprocessing and execute_python.

In safe mode (default), execute_python is disabled and geoprocessing is limited to an
allowlist of toolbox prefixes, with an optional explicit blocklist. No arcpy import.
"""


class SafetyError(Exception):
    """Raised when a command is rejected by policy."""


def check_gp_tool(tool: str, cfg) -> None:
    """Validate a GP tool name against policy.

    Accepts both forms ArcPy/handle_run_geoprocessing support:
      * dotted:    'analysis.Buffer'      -> matched by allowed prefix 'analysis.'
      * one-part:  'Buffer_analysis'      -> matched by toolbox suffix '_analysis'
    """
    if not getattr(cfg, "safe_mode", True):
        return
    if not tool:
        raise SafetyError("empty GP tool name")
    if tool in getattr(cfg, "blocked_gp_tools", []):
        raise SafetyError("GP tool '{}' is blocked by policy.".format(tool))
    prefixes = getattr(cfg, "allowed_gp_prefixes", []) or []
    if not prefixes:
        return
    toolboxes = [p[:-1] for p in prefixes if p.endswith(".")]  # 'analysis.' -> 'analysis'
    if "." in tool:
        allowed = any(tool.startswith(p) for p in prefixes)
    else:
        # legacy one-part name '<Tool>_<toolbox>' (e.g. 'Buffer_analysis')
        allowed = any(tool.endswith("_" + tbx) for tbx in toolboxes)
    if not allowed:
        raise SafetyError(
            "GP tool '{}' is not in the allowed toolboxes {}. "
            "Add its prefix to allowed_gp_prefixes or disable safe_mode.".format(tool, prefixes)
        )


def check_execute_python(cfg) -> None:
    """Gate arbitrary Python execution."""
    if getattr(cfg, "safe_mode", True) and not getattr(cfg, "allow_execute_python", False):
        raise SafetyError(
            "execute_python is disabled in safe mode. "
            "Set allow_execute_python=true in config.json to enable it."
        )
