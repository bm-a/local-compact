"""Free local compaction: honest tokens + guarded drop. Zero deps."""
from .tokens import estimate_tokens
from .scorer import score
from .compactor import compact

__version__ = "0.1.0"
__all__ = ["estimate_tokens", "score", "compact", "__version__"]
