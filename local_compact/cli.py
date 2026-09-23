"""CLI: preview savings before you drop anything."""
import argparse
import json


def main():
    from .compactor import compact
    from .tokens import estimate_tokens
    ap = argparse.ArgumentParser(prog="local-compact")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preview", help="preview what would be dropped")
    p.add_argument("file", help="jsonl or json with [{id,role,text,kind}]")
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--backend", default="local")
    t = sub.add_parser("tokens", help="honest token count")
    t.add_argument("text", nargs="?", default="hello world")
    args = ap.parse_args()
    if args.cmd == "tokens":
        print(estimate_tokens(args.text))
    elif args.cmd == "preview":
        raw = open(args.file).read()
        try:
            msgs = json.loads(raw)
            if isinstance(msgs, dict):
                msgs = msgs.get("messages", [])
        except Exception:
            msgs = [json.loads(l) for l in raw.splitlines() if l.strip()]
        r = compact(msgs, args.threshold, args.backend)
        print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in r.items()}, indent=2))
        print("\nkept %d / dropped %d / verdict %s / saved %d toks (%d -> %d)" % (
            len(r["kept"]), len(r["dropped"]), r["verdict"], r["saved_tokens"], r["tokens_before"], r["tokens_after"]))


if __name__ == "__main__":
    main()
