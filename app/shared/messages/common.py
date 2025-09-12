"""
Common messages used across different domains.
"""
from aiogram.utils.markdown import hbold
from shared.i18n import i18n


def get_error_message(error_type: str = "general") -> str:
    """Get error message based on error type."""
    return i18n.t(f"errors.{error_type}")


def get_success_message(action: str = "general") -> str:
    """Get success message based on action."""
    return i18n.t(f"success.{action}")


def get_help_text(i18n_instance=None, free_limit: int = 100) -> str:
    """Get general help text."""
    if i18n_instance is None:
        from shared.i18n import i18n

        i18n_instance = i18n

    return f"""
{hbold(i18n_instance.t('commands.help.title'))}

{hbold(i18n_instance.t('commands.help.commands_title'))}
{i18n_instance.t('commands.help.start_command')}
{i18n_instance.t('commands.help.help_command')}
{i18n_instance.t('commands.help.gender_command')}

{hbold(i18n_instance.t('commands.help.communication_title'))}
{i18n_instance.t('commands.help.free_limit', free_limit=free_limit)}
{i18n_instance.t('commands.help.premium_unlimited')}

{hbold(i18n_instance.t('commands.help.companion_title'))}
{i18n_instance.t('commands.help.female_description')}
{i18n_instance.t('commands.help.male_description')}

{hbold(i18n_instance.t('commands.help.premium_title'))}
{i18n_instance.t('commands.help.premium_description')}

{hbold(i18n_instance.t('commands.help.faq_title'))}
{i18n_instance.t('commands.help.context_memory')}
{i18n_instance.t('commands.help.gender_change')}
{i18n_instance.t('commands.help.limit_reset')}

{i18n_instance.t('commands.help.start_instruction', start_command=hbold('/start'))}
"""


def get_privacy_info_text() -> str:
    """Get privacy policy text."""
    return f"{i18n.t('consent.privacy_title')}\n\n{i18n.t('consent.privacy_text')}"
