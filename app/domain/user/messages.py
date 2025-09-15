"""
User domain messages - text templates and responses.
"""
from config.openai import OPENAI_CONFIG
from shared.i18n import i18n


def get_consent_given_text() -> str:
    """Get text after consent is given."""
    return i18n.t(
        "consent.agreed", free_limit=OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 100)
    )


def get_gender_change_warning_text() -> str:
    """Get gender change warning text."""
    return i18n.t("gender.change_warning")


def get_gender_selection_text() -> str:
    """Get gender selection text."""
    return i18n.t("gender.choose")
