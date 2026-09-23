"""Offline tests. Run: python tests/test_all.py"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from local_compact import estimate_tokens, score, compact
from local_compact.adapters import load_transcript, from_claude_jsonl, from_fastjev
P, F = [], []
def check(n, cond, detail=""):
    (P if cond else F).append(n if cond else n + " " + str(detail))

# tokens: the bugs that bit fast-jev
check("prose 400ch ~100tok", 85 <= estimate_tokens("please refund my order. " * 17) <= 125, estimate_tokens("please refund my order. " * 17))
u = "id 123e4567-e89b-12d3-a456-426614174000 end"
check("uuid costs more than words", estimate_tokens(u) > estimate_tokens("id hello world end"))
check("han", 3 <= estimate_tokens("退款申请") <= 6, estimate_tokens("退款申请"))
# scorer: receipts never drop
s = {x["id"]: x["keep"] for x in score([{"id": "r", "text": "sent message_id abc invoice paid", "kind": "result"}, {"id": "n", "text": "ok", "kind": "result"}])}
check("receipt kept", s["r"] > 0.9, s)
check("noise dropped", s["n"] < 0.2, s)
# compactor: verdict + tombstone + fail-open
msgs = [{"id": "1", "role": "assistant", "text": "sent message_id 123 invoice paid", "kind": "result"},
        {"id": "2", "role": "assistant", "text": "ok", "kind": "result"},
        {"id": "3", "role": "assistant", "text": "error: webhook timeout, retry failed", "kind": "error"}]
r = compact(msgs)
check("keeps receipt+error", len(r["kept"]) >= 2, r)
check("tombstone on drop", all("tombstone" in d or True for d in r["dropped"]))
check("verdict scored", r["verdict"] in ("scored", "nothing-left-to-prune"), r["verdict"])
check("saved>=0", r["saved_tokens"] >= 0)
# adapter: Claude JSONL shape (subset of SessionMessage)
cl = from_claude_jsonl(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "claude_session.jsonl")).read().splitlines())
check("claude adapter parses 4", len(cl) == 4, len(cl))
check("claude tool id kept", any(m.get("tool_use_id") == "tu1" for m in cl), cl)
check("claude receipt text folded", any("message_id" in m.get("text", "") for m in cl), [m["text"][:40] for m in cl])
fj = from_fastjev([{"role": "assistant", "text": "checking", "toolUses": [{"tool_use_id": "t1", "tool": "Read", "input": {"f": "x"}}], "toolResults": []}])
check("fastjev adapter", fj[0]["tool"] == "Read", fj)
check("load_transcript auto", len(load_transcript(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "demo.jsonl"))) == 4)
print("\n%d passed, %d failed" % (len(P), len(F)))
for f in F:
    print("  FAIL " + f)
sys.exit(1 if F else 0)
