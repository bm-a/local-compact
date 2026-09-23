"""Transcript adapters: Claude Code JSONL + fast-jev Message[] + simple rows -> local-compact messages.

Target row: {id, role, text, kind, tool?, tool_use_id?}
kind: result | error | user | chat
"""
import json
from typing import Any, Dict, List


def _row(i: int, role: str, text: str, kind: str = "result", tool: str = "", tid: str = "") -> Dict[str, Any]:
    return {"id": str(i), "role": role, "text": text or "", "kind": kind, "tool": tool, "tool_use_id": tid}


def from_simple(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for i, m in enumerate(data):
        out.append(_row(m.get("id", i), m.get("role", "assistant"), str(m.get("text", "")),
                        m.get("kind", "result"), str(m.get("tool", "")), str(m.get("tool_use_id", ""))))
    return out


def from_fastjev(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """fast-jev Message: {role, text, toolUses:[{tool_use_id,tool,input}], toolResults?:[{tool_use_id,text,isError}]}"""
    out = []
    for i, m in enumerate(messages):
        role = m.get("role", "assistant")
        text = str(m.get("text", ""))
        uses = m.get("toolUses", m.get("tool_uses", [])) or []
        results = m.get("toolResults", m.get("tool_results", [])) or []
        kind = "error" if any(r.get("isError") for r in results) else ("user" if role == "user" and not results else "result")
        tool = uses[0].get("tool", "") if uses else ""
        tid = uses[0].get("tool_use_id", "") if uses else (results[0].get("tool_use_id", "") if results else "")
        # fold tool-result text in so scorer sees it
        extra = " ".join(str(r.get("text", ""))[:500] for r in results)
        full = (text + "\n" + extra).strip() if extra else text
        out.append(_row(m.get("id", i), role, full, kind, tool, tid))
    return out


def _blocks_text(content: Any) -> tuple:
    """Extract (text, uses, results) from Anthropic content blocks."""
    texts, uses, results = [], [], []
    if isinstance(content, str):
        return content, uses, results
    for b in content or []:
        if not isinstance(b, dict):
            continue
        t = b.get("type", "")
        if t == "text":
            texts.append(str(b.get("text", "")))
        elif t in ("tool_use", "tooluse"):
            uses.append({"tool_use_id": b.get("id", ""), "tool": b.get("name", "")})
        elif t in ("tool_result", "toolresult"):
            inner = b.get("content", "")
            if isinstance(inner, list):
                inner = " ".join(x.get("text", "") for x in inner if isinstance(x, dict))
            results.append({"tool_use_id": b.get("tool_use_id", ""), "text": str(inner)[:2000],
                            "isError": bool(b.get("is_error"))})
    return "\n".join(texts), uses, results


def from_claude_jsonl(lines: List[str]) -> List[Dict[str, Any]]:
    """Claude Code session JSONL. Handles {type,message:{role,content}} and {role,content} variants."""
    out = []
    for i, ln in enumerate(lines):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        msg = o.get("message", None)
        if isinstance(msg, dict) and ("content" in msg or "role" in msg):
            content = msg.get("content", o.get("content", ""))
            role = msg.get("role", o.get("role", o.get("type", "assistant")))
        elif "content" in o or "parts" in o:
            content = o.get("content", "")
            role = o.get("role", o.get("type", "assistant"))
        elif "text" in o:
            # simple row: {id, role, text, kind}
            out.append(_row(o.get("id", i), o.get("role", "assistant"), str(o.get("text", "")),
                            o.get("kind", "result"), str(o.get("tool", "")), str(o.get("tool_use_id", ""))))
            continue
        else:
            continue
        if role in ("human", "user"):
            role = "user"
        else:
            role = "assistant"
        text, uses, results = _blocks_text(content)
        # OpenCode SST parts fallback: {parts:[{type,text}]}
        if not text and not uses and not results and isinstance(o.get("parts"), list):
            texts = [str(p.get("text", "")) for p in o["parts"] if isinstance(p, dict) and p.get("type") in ("text", "reasoning")]
            text = "\n".join(t for t in texts if t)
        kind = "error" if any(r.get("isError") for r in results) else ("user" if role == "user" and not results else "result")
        tool = uses[0]["tool"] if uses else ""
        tid = uses[0]["tool_use_id"] if uses else (results[0]["tool_use_id"] if results else "")
        extra = " ".join(r["text"][:500] for r in results)
        full = (text + "\n" + extra).strip() if extra else text
        if not full and not uses:
            continue
        out.append(_row(o.get("id", i), role, full, kind, tool, tid))
    return out


def load_transcript(path: str) -> List[Dict[str, Any]]:
    raw = open(path).read()
    # try whole-file JSON first
    try:
        o = json.loads(raw)
        if isinstance(o, list):
            # detect shape by first element keys
            if o and isinstance(o[0], dict) and ("toolUses" in o[0] or "tool_uses" in o[0]):
                return from_fastjev(o)
            return from_simple(o)
        if isinstance(o, dict) and isinstance(o.get("messages"), list):
            return from_simple(o["messages"])
    except Exception:
        pass
    # fall back to JSONL (Claude Code / OpenCode)
    return from_claude_jsonl(raw.splitlines())
