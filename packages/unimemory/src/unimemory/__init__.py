"""
UniMemory: Sovereign Cognitive Memory Substrate
===============================================
Authority: UniCortex Cognitive Architecture
"""

from unimemory.engine import UniMemoryEngine, get_engine
from unimemory.models import (
    WorkingMemoryItem,
    EpisodicEntry,
    SemanticFact,
    SymbolItem,
    MemoryRecallResult
)

__version__ = "2026.1.0"
__all__ = [
    "UniMemoryEngine",
    "get_engine",
    "WorkingMemoryItem",
    "EpisodicEntry",
    "SemanticFact",
    "SymbolItem",
    "MemoryRecallResult"
]
