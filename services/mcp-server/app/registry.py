from dataclasses import dataclass
from typing import Callable

RISK_READ_ONLY = "READ_ONLY"
RISK_PRIVATE_WRITE = "PRIVATE_WRITE"
RISK_EXTERNAL_WRITE = "EXTERNAL_WRITE"
RISK_FINANCIAL = "FINANCIAL"
RISK_DESTRUCTIVE = "DESTRUCTIVE"

# MVP policy: only FINANCIAL and DESTRUCTIVE are blocked outright.
_BLOCKED_RISK_LEVELS = {RISK_FINANCIAL, RISK_DESTRUCTIVE}


@dataclass
class Tool:
    name: str
    risk_level: str
    handler: Callable[[dict], dict]


TOOL_REGISTRY: dict[str, Tool] = {}


def tool(name: str, risk_level: str):
    def decorator(fn: Callable[[dict], dict]):
        TOOL_REGISTRY[name] = Tool(name=name, risk_level=risk_level, handler=fn)
        return fn

    return decorator


def is_blocked(risk_level: str) -> bool:
    return risk_level in _BLOCKED_RISK_LEVELS
