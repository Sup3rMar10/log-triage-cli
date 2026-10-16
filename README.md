# log-triage-cli

Turns a pile of JSON-lines logs into a short ranked list of distinct problems. When a customer says "it's failing", the first job is to find out *how many different ways* it is failing and which one dominates.

Standard library only. Synthetic examples.

## How it works

Each ERROR/CRITICAL/FATAL message is reduced to a **signature** by masking the parts that vary (UUIDs, hex, quoted strings, numbers). `timeout after 31s for order 8841` and `timeout after 29s for order 9120` become one signature, `timeout after <n>s for order <n>`. Signatures are counted and ranked, with first-seen, last-seen and one real example.

```
python -m logtriage.triage app.log      # or:  cat app.log | python -m logtriage.triage
```

```
     3  t1 .. t3
        timeout order <n>
        e.g. timeout order 1
```

## Tests

```
pip install pytest && python -m pytest -q
```

Four tests: masking, ranking while ignoring non-error levels, first/last seen, and unreadable lines being counted rather than silently dropped.

## Limits

- Expects one JSON object per line with `level` and `message`. Plain-text logs need a parser first (the count of skipped lines is printed so you notice).
- Masking is regex based. Over-masking merges different problems; under-masking splits one problem. Tune `MASKS` per customer.
- No time-window view, no stack-trace grouping, no streaming of very large files beyond reading line by line.

MIT licensed.
