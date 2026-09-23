# local-compact 🔒

**Free local compaction for Claude Code + OpenCode. No API key. Preview before you drop. Never lose receipts.**

```bash
pip install local-compact
local-compact preview transcript.json
# kept 120 / dropped 37 / verdict scored / saved 4200 toks
local-compact tokens "id 123e4567-e89b-12d3-a456-426614174000 + 退款申请"
```

## Why this exists

Cloud compactors send your full transcript to a third-party API, guess tokens wrong on hex/UUID/base64 (hello `max_tokens_exceeded` 400), and treat "nothing left to prune" as failure. This does the safe 80% offline:

- **Honest tokens** — prose ~4ch/tok, dense runs ~3ch/tok, Han ~1/char. No more local-check-passes-but-API-400s.
- **Receipt-guard** — `message_id`, `invoice`, `commit`, `tracking` etc. are never dropped. Non-idempotent tools can't be re-run.
- **Delete-only-when-confident** — drops only `p<0.15`, truncates head+tail otherwise, tombstones every drop so it's checkable.
- **Verdict, not ratio** — returns `scored` vs `nothing-left-to-prune` instead of mistaking clean history for failure.
- **Fail-open** — no key / no URL / API error → local scoring, never blocks you.
- **Privacy default** — `jev` backend refuses to send transcripts unless you explicitly opt in. Your code stays yours.

Works with Jev or Laya when you want them (`--backend jev|laya`), works without them when you don't.

## 30-second demo

```jsonl
{"id":"1","role":"assistant","text":"sent message_id 123 invoice paid","kind":"result"}
{"id":"2","role":"assistant","text":"ok","kind":"result"}
{"id":"3","role":"assistant","text":"error: webhook timeout","kind":"error"}
```

```bash
local-compact preview demo.jsonl --threshold 0.5
```

## Python

```python
from local_compact import compact
r = compact([
  {"id":"1","text":"sent message_id 123 invoice paid","kind":"result"},
  {"id":"2","text":"ok","kind":"result"},
], keep_threshold=0.5)
print(r["verdict"], r["saved_tokens"], len(r["kept"]), len(r["dropped"]))
```

## Claude Code / OpenCode

See `hooks/` for a minimal session-compact hook that calls `compact()` first and only escalates to the cloud when `verdict == scored` and savings are worth it. Default: local only.

## Honest limits

- Local scorer is keyword+recency heuristics with a receipt guard — great for noise (`ok`, `listed 12 files`), safe on receipts/errors, weak on subtle semantic staleness. That's the trade for free/offline.
- If you need semantic ranking, plug `--backend jev` (your key, your opt-in) or run Laya locally and point `LAYA_BASE_URL` at it. The guards (receipts, tombstones, verdict) stay on in every backend.

## Tests

```bash
python tests/test_all.py  # 9 passed, offline, <1s
```

## Roadmap / good first issues

1. Your stack's transcript adapter (Claude JSONL, OpenCode SST, Hermes engine)
2. Your language's receipt words
3. Head+tail vs head-only truncation A/B on your logs
4. Laya `baseUrl` wiring with redaction hook

Apache-2.0.
