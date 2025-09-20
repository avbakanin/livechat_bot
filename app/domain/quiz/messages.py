def get_quiz_start_text(i18n) -> str:
    """Get localized quiz start text"""
    return i18n.t("quiz.start_text")


def get_quiz_texts(i18n) -> dict:
    """Get localized quiz texts"""
    return {
        "start": i18n.t("quiz.questions.landscape"),
        "superpower": i18n.t("quiz.questions.superpower"),
        "time_of_day": i18n.t("quiz.questions.time_of_day"),
        "book": i18n.t("quiz.questions.book"),
        "three_words": i18n.t("quiz.questions.three_words"),
        "rest": i18n.t("quiz.questions.rest"),
        "animal": i18n.t("quiz.questions.animal"),
        "min_words": i18n.t("quiz.messages.min_words"),
        "completion": i18n.t("quiz.messages.completion"),
        "start_chatting": i18n.t("quiz.messages.start_chatting"),
    }
