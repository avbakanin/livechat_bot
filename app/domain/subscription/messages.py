from aiogram.utils.markdown import hbold
from shared.i18n import i18n


def get_premium_info_text():
    return f"""
{hbold(i18n.t("premium.title"))}

{hbold(i18n.t("premium.benefits_title"))}
{i18n.t("premium.benefits.unlimited")}
{i18n.t("premium.benefits.priority")}
{i18n.t("premium.benefits.history")}
{i18n.t("premium.benefits.modes")}

{hbold(i18n.t("premium.price_title"))}
{i18n.t("premium.price")}
"""
