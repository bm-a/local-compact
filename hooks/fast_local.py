# Minimal Claude Code / OpenCode session-compact hook (pseudo-code).
# 1. Run local_compact.compact() on the candidate messages.
# 2. If verdict == "nothing-left-to-prune": let the built-in summary handle it.
# 3. If verdict == "scored" and saved_tokens > threshold: apply kept/dropped, log tombstones.
# 4. Only then (opt-in) escalate ambiguous mids (0.15 <= p < threshold) to Jev/Laya.
#
# Never send full transcripts to a third party by default. See README.
from local_compact import compact

def on_compact(messages, threshold=0.5):
    r = compact(messages, keep_threshold=threshold, backend="local")
    if r["verdict"] == "nothing-left-to-prune":
        return {"action": "fallback-to-summary"}
    return {"action": "apply-local", "kept": r["kept"], "dropped": r["dropped"],
            "saved_tokens": r["saved_tokens"]}
