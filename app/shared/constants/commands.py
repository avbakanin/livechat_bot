class Callbacks:
    # Confirm / Cancel
    STOP_CONFIRM = "stop_confirm"
    RESTART_CONFIRM = "restart_confirm"
    STOP_CANCEL = "stop_cancel"
    RESTART_CANCEL = "restart_cancel"
    # Help / Navigation
    CHOOSE_GENDER_HELP = "choose_gender_help"
    CHOOSE_LANGUAGE = "choose_language"
    BACK_TO_HELP = "back_to_help"
    PRIVACY_INFO_HELP = "privacy_info_help"
    CONSENT_AGREE = "consent_agree"
    # Gender actions
    GENDER_CHANGE_CONFIRM = "gender_change_confirm"
    GENDER_CHANGE_CANCEL = "gender_change_cancel"
    GENDER_FEMALE = "gender_female"
    GENDER_MALE = "gender_male"
    # Language dynamic prefix
    LANG_PREFIX = "lang_"
    # Commands
    RESET_DAILY_METRICS = "/reset_daily_metrics"
    CLEAN_METRICS = "/clean_metrics"
    # Subscription
    SUBSCRIBE_PREMIUM = "subscribe_premium"
    BUY_PREMIUM = "buy_premium"
    PREMIUM_INFO_HELP = "premium_info_help"

    @classmethod
    def get_all_commands(cls):
        """Возвращает список всех команд"""
        return [
            cls.STOP_CONFIRM,
            cls.RESTART_CONFIRM,
            cls.STOP_CANCEL,
            cls.RESTART_CANCEL,
            cls.CHOOSE_GENDER_HELP,
            cls.CHOOSE_LANGUAGE,
            cls.BACK_TO_HELP,
            cls.PRIVACY_INFO_HELP,
            cls.CONSENT_AGREE,
            cls.GENDER_CHANGE_CONFIRM,
            cls.GENDER_CHANGE_CANCEL,
            cls.GENDER_FEMALE,
            cls.GENDER_MALE,
            cls.LANG_PREFIX,
            cls.RESET_DAILY_METRICS,
            cls.CLEAN_METRICS,
            cls.SUBSCRIBE_PREMIUM,
            cls.BUY_PREMIUM,
            cls.PREMIUM_INFO_HELP,
        ]

    @classmethod
    def as_dict(cls):
        """Возвращает все команды в виде словаря"""
        return {
            "STOP_CONFIRM": cls.STOP_CONFIRM,
            "RESTART_CONFIRM": cls.RESTART_CONFIRM,
            "STOP_CANCEL": cls.STOP_CANCEL,
            "RESTART_CANCEL": cls.RESTART_CANCEL,
            "CHOOSE_GENDER_HELP": cls.CHOOSE_GENDER_HELP,
            "CHOOSE_LANGUAGE": cls.CHOOSE_LANGUAGE,
            "BACK_TO_HELP": cls.BACK_TO_HELP,
            "PRIVACY_INFO_HELP": cls.PRIVACY_INFO_HELP,
            "CONSENT_AGREE": cls.CONSENT_AGREE,
            "GENDER_CHANGE_CONFIRM": cls.GENDER_CHANGE_CONFIRM,
            "GENDER_CHANGE_CANCEL": cls.GENDER_CHANGE_CANCEL,
            "GENDER_FEMALE": cls.GENDER_FEMALE,
            "GENDER_MALE": cls.GENDER_MALE,
            "LANG_PREFIX": cls.LANG_PREFIX,
            "RESET_DAILY_METRICS": cls.RESET_DAILY_METRICS,
            "CLEAN_METRICS": cls.CLEAN_METRICS,
            "PREMIUM_INFO_HELP": cls.PREMIUM_INFO_HELP,
            "SUBSCRIBE_PREMIUM": cls.SUBSCRIBE_PREMIUM,
            "BUY_PREMIUM": cls.BUY_PREMIUM,
        }


class BotCommands:
    START = "start"
    CHOOSE_GENDER = "choose_gender"
    HELP = "help"
    PRIVACY = "privacy"
    LANGUAGE = "language"
    STATUS = "status"
    SECURITY = "security"
    RESET_METRICS = "reset_metrics"
    RESTART = "restart"
    STOP = "stop"
    METRICS = "metrics"
    QUIZ = "quiz"
    CLEAR_CACHE = "clear_cache"

    @classmethod
    def get_all_commands(cls):
        """Возвращает список всех команд"""
        return [
            cls.START,
            cls.CHOOSE_GENDER,
            cls.HELP,
            cls.PRIVACY,
            cls.LANGUAGE,
            cls.STATUS,
            cls.SECURITY,
            cls.RESET_METRICS,
            cls.RESTART,
            cls.STOP,
            cls.METRICS,
            cls.QUIZ,
            cls.CLEAR_CACHE,
        ]

    @classmethod
    def as_dict(cls):
        """Возвращает все команды в виде словаря"""
        return {
            "START": cls.START,
            "CHOOSE_GENDER": cls.CHOOSE_GENDER,
            "HELP": cls.HELP,
            "PRIVACY": cls.PRIVACY,
            "LANGUAGE": cls.LANGUAGE,
            "STATUS": cls.STATUS,
            "SECURITY": cls.SECURITY,
            "RESET_METRICS": cls.RESET_METRICS,
            "RESTART": cls.RESTART,
            "STOP": cls.STOP,
            "METRICS": cls.METRICS,
            "QUIZ": cls.QUIZ,
            "CLEAR_CACHE": cls.CLEAR_CACHE,
        }
