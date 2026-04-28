"""templates_meta helpers (Story 3.3)."""

from app.whatsapp.templates_meta import map_template_record


def test_map_template_record_unmapped_status_uses_submitted() -> None:
    disp, meta, detail, _qual = map_template_record(
        {"name": "x", "language": "en", "status": "NEW_META_STATUS_X"}
    )
    assert disp == "submitted"
    assert meta == "NEW_META_STATUS_X"
    assert detail is not None
    assert "Unmapped" in detail


def test_map_template_record_missing_status_detail() -> None:
    disp, meta, detail, _q = map_template_record({"name": "x", "language": "en"})
    assert disp == "submitted"
    assert meta == "UNKNOWN"
    assert detail and "missing" in detail.lower()
