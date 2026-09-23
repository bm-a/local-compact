"""Free local compaction: honest tokens + guarded drop. Zero deps."""
from .tokens import estimate_tokens
from .scorer import score
from .compactor import compact
from .adapters import load_transcript

__version__ = "0.2.0"
__all__ = ["estimate_tokens", "score", "compact", "load_transcript", "__version__"]
