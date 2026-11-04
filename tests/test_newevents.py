"""Unit tests for the daily new-session watcher (network-free)."""

from reinvent26 import newevents as ne


def _s(sid, **kw):
    row = {"sessionId": sid, "code": sid.upper(), "title": f"title {sid}"}
    row.update(kw)
    return row


def test_diff_finds_added_and_removed():
    old = [_s("a"), _s("b"), {"no-id": True}]
    live = [_s("b"), _s("c"), {"no-id": True}]
    added, removed = ne.diff_catalogs(old, live)
    assert [s["sessionId"] for s in added] == ["c"]
    assert [s["sessionId"] for s in removed] == ["a"]


def test_diff_empty_old_treats_all_live_as_added():
    added, removed = ne.diff_catalogs([], [_s("x")])
    assert [s["sessionId"] for s in added] == ["x"]
    assert removed == []


def test_parse_session_detail_wrapped_and_flat():
    wrapped = {"session": {"seatAvailability": "limited", "abstract": "abc", "isReservable": True}}
    assert ne.parse_session_detail(wrapped) == ("limited", "abc", True)
    flat = {"seatAvailability": "available", "description": "d", "isReservable": False}
    assert ne.parse_session_detail(flat) == ("available", "d", False)
    assert ne.parse_session_detail({}) == (None, "", None)
    assert ne.parse_session_detail(None) == (None, "", None)


def test_evaluate_orders_core_first():
    config = {"topics": [{"name": "agents", "pattern": "agent"}]}
    tagged = _s("t1", title="agent session")
    plain = _s("t2", title="storage deep dive")
    ranked = ne.evaluate([plain, tagged], config)
    assert [s["sessionId"] for s in ranked] == ["t1", "t2"]
    assert ranked[0]["_core"] == ["agents"]


def test_opportunities_splits_fits_and_conflicts():
    from reinvent26 import mapper
    config = mapper._load_config()
    held = [_s("h", startTime="2026-12-01T12:00:00", endTime="2026-12-01T13:00:00",
                venue="Wynn/Encore", type="Chalk talk")]
    free = _s("f", startTime="2026-12-01T15:00:00", endTime="2026-12-01T16:00:00",
              venue="Wynn/Encore", type="Chalk talk", _seat="available")
    clash = _s("c", startTime="2026-12-01T12:30:00", endTime="2026-12-01T13:30:00",
               venue="Wynn/Encore", type="Chalk talk", _seat="limited")
    full = _s("x", startTime="2026-12-01T15:00:00", endTime="2026-12-01T16:00:00",
              venue="Wynn/Encore", type="Chalk talk", _seat="unavailable")
    fits, conflicts = ne.opportunities([free, clash, full], held, config)
    assert [s["sessionId"] for s in fits] == ["f"]
    assert [s["sessionId"] for s, _ in conflicts] == ["c"]


def test_render_report_has_all_sections_and_handoff():
    fits = [_s("f", startTime="2026-12-01T15:00:00", endTime="2026-12-01T16:00:00",
                venue="Wynn/Encore", type="Chalk talk", level="300",
                title="fit talk", _seat="available", _core=["agents"])]
    report = ne.render_report("2026-11-05", "reinvent2026", fits, [], fits, [],
                              [], 14, "topic-tags")
    for section in ("opportunities", "conflicts", "unchecked", "removed",
                    "all added sessions", "handoff to kiro-cli"):
        assert section in report
    assert "fit talk" in report


def test_render_handoff_names_ids_and_conflicts():
    fits = [_s("f", sessionId="sess-f")]
    conflicts = [(_s("c", sessionId="sess-c"), [_s("h")])]
    text = ne.render_handoff("reinvent2026", fits, conflicts)
    assert "sess-f" in text and "sess-c" in text
    assert "GetSchedule" in text
    assert "Reserve nothing new" in ne.render_handoff("reinvent2026", [], [])
