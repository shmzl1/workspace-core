"""Helpers for calling human-maintained algorithm entry points."""

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from typing import Any


@dataclass(frozen=True)
class HumanOnlyContract:
    module_name: str
    file_path: str
    function_name: str
    not_ready_message: str


def algorithm_not_ready(contract: HumanOnlyContract, fallback_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the shared not-ready payload for missing human-only algorithms."""

    return {
        "status": "algorithm_not_ready",
        "message": contract.not_ready_message,
        "expected_module": contract.file_path,
        "expected_function": contract.function_name,
        "fallback_data": fallback_data or {},
    }


def load_human_only_function(contract: HumanOnlyContract) -> Callable[[dict[str, Any]], dict[str, Any]] | None:
    """Load a human-only function without importing it from API or Tool layers."""

    try:
        module = import_module(contract.module_name)
        entry = getattr(module, contract.function_name)
    except (ImportError, AttributeError):
        return None

    if not callable(entry):
        return None
    return entry
