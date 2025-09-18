from aiogram.utils.markdown import hbold
from shared.i18n import i18n


def get_error_message(error_type: str = "general") -> str:
    """Get error message based on error type."""
    return i18n.t(f"errors.{error_type}")


def get_success_message(action: str = "general") -> str:
    """Get success message based on action."""
    return i18n.t(f"success.{action}")


def get_help_text(free_limit: int = None) -> str:
    from shared.constants import OPENAI_CONFIG

    # Use provided limit or get from config
    if free_limit is None:
        free_limit = OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 50)

    # Use provided i18n instance or fallback to global

    return f"""
{hbold(i18n.t('commands.help.title'))}

{hbold(i18n.t('commands.help.commands_title'))}
{i18n.t('commands.help.start_command')}
{i18n.t('commands.help.help_command')}
{i18n.t('commands.help.gender_command')}
{i18n.t('commands.help.status_command')}
{i18n.t('commands.help.language_command')}
{i18n.t('commands.help.restart_command')}
{i18n.t('commands.help.stop_command')}

{hbold(i18n.t('commands.help.communication_title'))}
{i18n.t('commands.help.free_limit', free_limit=free_limit)}
{i18n.t('commands.help.premium_unlimited')}

{hbold(i18n.t('commands.help.companion_title'))}
{i18n.t('commands.help.female_description')}
{i18n.t('commands.help.male_description')}

{hbold(i18n.t('commands.help.premium_title'))}
{i18n.t('commands.help.premium_description')}

{hbold(i18n.t('commands.help.faq_title'))}
{i18n.t('commands.help.context_memory')}
{i18n.t('commands.help.gender_change')}
{i18n.t('commands.help.limit_reset')}
    """


def get_privacy_info_text() -> str:
    return f"{i18n.t('consent.privacy_title')}\n\n{i18n.t('consent.privacy_text')}"
