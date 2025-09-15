from aiogram.utils.markdown import hbold


def get_error_message(error_type: str = "general") -> str:
    """Get error message based on error type."""
    from shared.i18n import i18n

    return i18n.t(f"errors.{error_type}")


def get_success_message(action: str = "general") -> str:
    """Get success message based on action."""
    from shared.i18n import i18n

    return i18n.t(f"success.{action}")


def get_help_text(free_limit: int = None) -> str:
    from shared.i18n import i18n
    from config.openai import OPENAI_CONFIG
    
    # Use provided limit or get from config
    if free_limit is None:
        free_limit = OPENAI_CONFIG.get('FREE_MESSAGE_LIMIT', 100)

    return f"""
        {hbold(i18n.t('commands.help.title'))}

        {hbold(i18n.t('commands.help.commands_title'))}
        {i18n.t('commands.help.start_command')}
        {i18n.t('commands.help.help_command')}
        {i18n.t('commands.help.gender_command')}
        {i18n.t('commands.help.check_messages_command')}

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

        {i18n.t('commands.help.start_instruction', start_command=hbold('/start'))}
"""


def get_privacy_info_text() -> str:
    from shared.i18n import i18n

    return f"{i18n.t('consent.privacy_title')}\n\n{i18n.t('consent.privacy_text')}"
