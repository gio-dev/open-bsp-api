"""Unit: ordenacao e construcao de sinais (Story 4.4)."""

from app.services.channel_health import (
    ChannelHealthCounts,
    _build_signals,
)


def test_build_signals_empty_when_all_zero() -> None:
    c = ChannelHealthCounts(0, 0, 0, 0, 0)
    assert _build_signals(c) == []


def test_critical_platform_before_warnings() -> None:
    c = ChannelHealthCounts(
        outbound_failed_meta=2,
        outbound_failed_platform=1,
        outbound_rate_limited=0,
        outbound_stale_queued=0,
        handoff_failed=0,
    )
    sigs = _build_signals(c)
    assert sigs[0].code == "outbound_failed_platform"
    assert sigs[0].severity == "critical"
    codes = [s.code for s in sigs]
    assert "outbound_failed_meta" in codes


def test_handoff_failed_includes_next_step() -> None:
    c = ChannelHealthCounts(0, 0, 0, 0, 3)
    sigs = _build_signals(c)
    assert len(sigs) == 1
    assert sigs[0].code == "handoff_failed"
    assert sigs[0].count == 3
    assert sigs[0].source == "unknown"
    assert "handoff" in sigs[0].next_step.lower()


def test_stale_queued_signal() -> None:
    c = ChannelHealthCounts(0, 0, 0, 2, 0)
    sigs = _build_signals(c)
    assert [s.code for s in sigs] == ["outbound_stale_queued"]
    assert sigs[0].source == "platform"
    assert sigs[0].severity == "warning"


def test_rate_limited_signal() -> None:
    c = ChannelHealthCounts(0, 0, 3, 0, 0)
    sigs = _build_signals(c)
    codes = [s.code for s in sigs]
    assert codes == ["outbound_rate_limited"]
    assert sigs[0].source == "meta"
    assert sigs[0].severity == "warning"


def test_warnings_order_handoff_before_meta_failures() -> None:
    """Ordem de emissao: criticos primeiro; handoff antes de falhas/atrasos Meta."""
    c = ChannelHealthCounts(
        outbound_failed_meta=1,
        outbound_failed_platform=0,
        outbound_rate_limited=1,
        outbound_stale_queued=1,
        handoff_failed=1,
    )
    sigs = _build_signals(c)
    codes = [s.code for s in sigs]
    hi = codes.index("handoff_failed")
    assert codes.index("outbound_stale_queued") < codes.index("outbound_failed_meta")
    assert hi < codes.index("outbound_failed_meta")
    assert hi < codes.index("outbound_rate_limited")
