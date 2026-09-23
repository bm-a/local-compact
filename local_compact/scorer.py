"""Scorer with 3 backends: local (default, free), jev (optional API), laya/baseUrl (optional).
Local = keyword + recency + receipt-guard. Never pretends to be SOTA — it is a safe default."""
import os
import re

RECEIPT = re.compile(r"(message_id|sent|commit|status:|invoice|receipt|order|tracking)", re.I)
NOISE = re.compile(r"^(ok|done|listed|found \d+|file updated)\.?$", re.I)

def _local_score(item: dict) -> float:
    """0..1 keep-score. High = must keep."""
    text = str(item.get("text", ""))[:2000]
    kind = item.get("kind", "result")
    if RECEIPT.search(text):
        return 0.95  # receipt-guard: never drop what you can't re-run
    if NOISE.match(text.strip().lower()):
        return 0.05
    if kind == "error":
        return 0.9
    if len(text) > 500:
        return 0.4
    return 0.3

def score(items, backend: str = "local") -> list:
    backend = backend or os.environ.get("COMPACT_BACKEND", "local")
    if backend == "local":
        return [{"id": it.get("id"), "keep": _local_score(it)} for it in items]
    # jev / laya pass-through: talk to API only if key/url present, else fall back local (fail-open)
    try:
        if backend == "jev":
            import json, urllib.request
            key = os.environ.get("TYPESAFE_API_KEY", "")
            if not key:
                raise RuntimeError("no TYPESAFE_API_KEY")
            # minimal: we do NOT send full transcripts without redaction; caller must opt in
            raise RuntimeError("jev backend needs explicit opt-in; refusing to send transcript by default")
        if backend in ("laya", "baseUrl"):
            import json, urllib.request
            base = os.environ.get("TYPESAFE_BASE_URL", os.environ.get("LAYA_BASE_URL", ""))
            if not base:
                raise RuntimeError("no base url")
            raise RuntimeError("baseUrl backend not wired in v0.1; use local")
    except Exception:
        return [{"id": it.get("id"), "keep": _local_score(it), "fallback": True} for it in items]
    return [{"id": it.get("id"), "keep": _local_score(it)} for it in items]
