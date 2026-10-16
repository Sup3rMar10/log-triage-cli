from logtriage.triage import signature, triage


def L(level, msg, ts="2026-01-01T00:00:00Z"):
    import json
    return json.dumps({"level": level, "message": msg, "ts": ts})


def test_variable_parts_are_masked():
    assert signature("timeout after 31s for order 8841") == signature("timeout after 29s for order 9120")
    assert signature("user 'bob' failed") == signature("user 'amy' failed")
    assert signature("id 3f2b8c1e-1111-2222-3333-444455556666") == "id <uuid>"


def test_groups_and_ranks_errors_only():
    lines = [L("ERROR", "timeout order 1"), L("ERROR", "timeout order 2"), L("ERROR", "bad card 7"),
             L("INFO", "started"), L("ERROR", "timeout order 3")]
    ranked, skipped = triage(lines)
    assert [(r[0], r[1]) for r in ranked] == [("timeout order <n>", 3), ("bad card <n>", 1)]
    assert skipped == 0


def test_first_and_last_seen():
    ranked, _ = triage([L("ERROR", "x 1", "t1"), L("ERROR", "x 2", "t2"), L("ERROR", "x 3", "t3")])
    assert ranked[0][2:4] == ("t1", "t3")


def test_unreadable_lines_are_counted_not_hidden():
    ranked, skipped = triage(["not json", '{"level": "ERROR"}', "", L("ERROR", "a 1")])
    assert skipped == 2 and ranked[0][1] == 1
