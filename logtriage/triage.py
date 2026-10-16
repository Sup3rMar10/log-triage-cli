"""Group JSON-lines log errors by "signature" so 10,000 lines become a short ranked list.

A signature is the message with the variable parts (numbers, ids, hex, quoted strings) masked,
so "timeout after 31s for order 8841" and "timeout after 29s for order 9120" count as one problem.
"""
import json
import re
import sys
from collections import Counter, defaultdict

MASKS = [
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<uuid>"),
    (re.compile(r"\b0x[0-9a-f]+\b", re.I), "<hex>"),
    (re.compile(r"\"[^\"]*\"|'[^']*'"), "<str>"),
    (re.compile(r"(?<![A-Za-z_])\d+(?:\.\d+)?"), "<n>"),
]


def signature(message: str) -> str:
    for rx, token in MASKS:
        message = rx.sub(token, message)
    return message


def triage(lines, levels=("ERROR", "CRITICAL", "FATAL")):
    """Returns (ranked, skipped). ranked: [(signature, count, first_ts, last_ts, example)]."""
    counts, first, last, example = Counter(), {}, {}, {}
    skipped = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            level, msg = str(rec["level"]).upper(), str(rec["message"])
        except (ValueError, KeyError, TypeError):
            skipped += 1          # count, never hide, lines we could not read
            continue
        if level not in levels:
            continue
        sig = signature(msg)
        ts = rec.get("ts", "")
        counts[sig] += 1
        first.setdefault(sig, ts)
        last[sig] = ts
        example.setdefault(sig, msg)
    ranked = [(s, n, first[s], last[s], example[s]) for s, n in counts.most_common()]
    return ranked, skipped


def main(argv=None):
    path = (argv or sys.argv[1:] or ["-"])[0]
    f = sys.stdin if path == "-" else open(path, encoding="utf-8")
    ranked, skipped = triage(f)
    for sig, n, a, b, ex in ranked[:20]:
        print(f"{n:>6}  {a} .. {b}\n        {sig}\n        e.g. {ex}")
    if skipped:
        print(f"\n{skipped} line(s) were not valid JSON log records and were skipped.")


if __name__ == "__main__":
    main()
