# Launch drafts for local-compact v0.2.0 (pick one per site, no spam)

## 1. Hacker News — Show HN (title <= 80 chars)
Title: `Show HN: Free local compaction for Claude Code, no API key`

Body:
```
Preview what compaction would drop before it drops it.

local-compact is a zero-dep Python tool: honest token counts (dense
hex/UUID/base64 ~3ch/tok, Han ~1/char), receipt-guard (message_id/
invoice/commit never dropped), delete-only-when-confident, tombstones,
verdict scored vs nothing-left-to-prune.

Reads Claude Code JSONL + fast-jev Message[] + plain rows:
  local-compact preview session.jsonl

Fail-open: no key, no network, works offline. Jev/Laya backends are
opt-in only — transcripts are never sent by default.

Not SOTA ranking: local scorer is heuristics. The guards are the point.
14 offline tests, <1s. Apache-2.0.

Repo: https://github.com/bm-a/local-compact
Ask: post your transcript shape if the adapter misses it, and your
receipt words in your language.
```

## 2. Reddit r/ClaudeCode
Title: `Free offline compaction preview — stops the silent drops?`

Body:
```
I kept hitting two things with cloud compactors: (1) local token check
passes, API 400s on max_tokens (dense logs), (2) receipts vanishing.

Made local-compact: `preview` shows kept/dropped/saved before anything
is deleted, receipts (invoice/message_id/commit/tracking) are pinned,
drops get tombstones, verdict tells scored vs nothing-left-to-prune.

- No API key, works on Claude Code JSONL out of the box
- `local-compact preview examples/claude_session.jsonl` runs in ms
- Cloud (Jev/Laya) only if you opt in; default sends nothing anywhere

Honest limit: local ranking is heuristics, not a 400M model. Good for
noise (ok/listed files), safe on receipts/errors, weak on subtle
semantics. That's the trade for free.

Repo + demo: https://github.com/bm-a/local-compact
What transcript shape should I support next (OpenCode SST? Hermes)?
```

## 3. Reddit r/LocalLLaMA (angle: privacy)
Title: `[P] Compact Claude transcripts fully offline — no transcript leaves your box`

Same body as above + line: `Tested on Termux/Android CPU, <1ms per preview.`

## 4. Discord (Jev / TypeSafe / Laya servers) — short
```
shipped local-compact v0.2: free offline compaction preview for Claude
Code JSONL — honest tokens (dense/Han), receipt-guard, tombstones,
verdict. No key, fail-open. Jev/Laya opt-in only, never auto-sends.
Would love transcript shapes that break the adapter:
https://github.com/bm-a/local-compact
```

## 5. awesome-jev PR (to yibie/awesome-jev)
Title: `Add local-compact (free offline compaction preview)`
Body:
```
- Free, zero-dep, no API key; reads Claude Code JSONL + Message[]
- Honest tokens for dense runs + Han; receipt-guard; verdict-based
- Fail-open; cloud backends opt-in only
Link: https://github.com/bm-a/local-compact
```
