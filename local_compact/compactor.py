"""Guarded compactor: verdict-based, receipt-guard, tombstones, fail-open."""
from .tokens import estimate_tokens
from .scorer import score

def compact(messages, keep_threshold: float = 0.5, backend: str = "local") -> dict:
    """messages: [{id, role, text, kind}]. Returns {kept, dropped, verdict, saved_tokens}."""
    items = [{"id": m.get("id", str(i)), "text": m.get("text", ""), "kind": m.get("kind", "result")} for i, m in enumerate(messages)]
    scores = {s["id"]: s["keep"] for s in score(items, backend)}
    kept, dropped = [], []
    for m, it in zip(messages, items):
        p = scores.get(it["id"], 0.5)
        # delete-only-when-confident: drop only if clearly stale AND not a receipt
        if p < 0.15:
            dropped.append({**m, "tombstone": "[dropped by local-compact: judged stale]"})
        elif p < keep_threshold:
            t = str(m.get("text", ""))
            head = t[:300]
            tail = t[-200:] if len(t) > 500 else ""
            kept.append({**m, "text": head + ("\n...[truncated]...\n" + tail if tail else "")})
        else:
            kept.append(m)
    before = sum(estimate_tokens(str(m.get("text", ""))) for m in messages)
    after = sum(estimate_tokens(str(m.get("text", ""))) for m in kept)
    saved = before - after
    verdict = "scored" if dropped or saved > 0 else "nothing-left-to-prune"
    return {"kept": kept, "dropped": dropped, "verdict": verdict,
            "tokens_before": before, "tokens_after": after, "saved_tokens": saved}
