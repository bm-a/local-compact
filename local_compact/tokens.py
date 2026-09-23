"""Honest tokens: prose ~4ch/tok, dense hex/uuid/b64 ~3ch/tok, Han ~1/char."""
import re
HEX = re.compile(r"\b[0-9a-fA-F]{16,}\b")
UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
B64 = re.compile(r"\b[A-Za-z0-9+/]{24,}={0,2}\b")

def _han(ch):
    cp = ord(ch)
    return 0x3400 <= cp <= 0x4DBF or 0x4E00 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    han = sum(1 for ch in text if _han(ch))
    spans = []
    for p in (UUID, HEX, B64):
        for m in p.finditer(text):
            spans.append([m.start(), m.end()])
    spans.sort()
    mg = []
    for s, e in spans:
        if mg and s <= mg[-1][1]:
            mg[-1][1] = max(mg[-1][1], e)
        else:
            mg.append([s, e])
    dense = 0
    for s, e in mg:
        c = text[s:e]
        if any(x.isdigit() for x in c) or len(c) >= 40 or (any(x.islower() for x in c) and any(x.isupper() for x in c)):
            dense += e - s
    rest = max(0, len(text) - han - dense)
    return int(round(han * 0.99 + dense / 3.0 + rest / 4.0)) or 1
