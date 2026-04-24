"""BSUID syntax and inbound identity resolution."""

from app.whatsapp.bsuid import is_valid_bsuid, normalize_bsuid
from app.whatsapp.identity import resolve_inbound_identity


def test_normalize_bsuid_trims() -> None:
    assert normalize_bsuid("  US.123456789012  ") == "US.123456789012"


def test_normalize_bsuid_uppercases_country_code() -> None:
    assert normalize_bsuid("us.123456789012") == "US.123456789012"


def test_is_valid_bsuid_accepts_meta_shape() -> None:
    assert is_valid_bsuid("US.13491208655302741918") is True


def test_is_valid_bsuid_accepts_four_digit_suffix() -> None:
    assert is_valid_bsuid("US.1234") is True


def test_is_valid_bsuid_rejects_phone() -> None:
    assert is_valid_bsuid("351912345678") is False


def test_is_valid_bsuid_rejects_garbage() -> None:
    assert is_valid_bsuid("not-a-bsuid") is False


def test_is_valid_bsuid_rejects_too_long_suffix() -> None:
    assert is_valid_bsuid("US." + "1" * 41) is False


def test_resolve_identity_bsuid_and_phone() -> None:
    value = {
        "contacts": [
            {
                "wa_id": "15551234567",
                "user_id": "US.13491208655302741918",
                "profile": {"name": "Ada"},
            }
        ],
    }
    message = {
        "from": "15551234567",
        "from_user_id": "US.13491208655302741918",
        "id": "wamid.x",
        "type": "text",
    }
    ident = resolve_inbound_identity(value, message)
    assert ident is not None
    assert ident.bsuid == "US.13491208655302741918"
    assert ident.wa_id == "15551234567"
    assert ident.display_name == "Ada"
    assert ident.stable_storage_key() == "US.13491208655302741918"


def test_resolve_identity_bsuid_only_no_contacts() -> None:
    value: dict = {"contacts": []}
    message = {
        "from_user_id": "US.13491208655302741918",
        "id": "wamid.x",
        "type": "text",
    }
    ident = resolve_inbound_identity(value, message)
    assert ident is not None
    assert ident.bsuid == "US.13491208655302741918"
    assert ident.wa_id is None
    assert ident.stable_storage_key() == "US.13491208655302741918"


def test_resolve_identity_phone_only() -> None:
    value = {
        "contacts": [{"wa_id": "15559876543", "profile": {"name": "Bob"}}],
    }
    message = {"from": "15559876543", "id": "wamid.y", "type": "text"}
    ident = resolve_inbound_identity(value, message)
    assert ident is not None
    assert ident.bsuid is None
    assert ident.wa_id == "15559876543"
    assert ident.stable_storage_key() == "15559876543"


def test_resolve_identity_invalid_bsuid_falls_back_to_wa() -> None:
    value = {
        "contacts": [{"wa_id": "15551234567", "user_id": "not-a-bsuid"}],
    }
    message = {
        "from": "15551234567",
        "from_user_id": "garbage-id",
        "id": "wamid.z",
        "type": "text",
    }
    ident = resolve_inbound_identity(value, message)
    assert ident is not None
    assert ident.bsuid is None
    assert ident.wa_id == "15551234567"
