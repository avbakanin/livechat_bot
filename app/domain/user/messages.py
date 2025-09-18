"""
User domain messages - text templates and responses.
"""

from shared.constants import OPENAI_CONFIG
from shared.i18n import i18n


def get_consent_given_text() -> str:
    """Get text after consent is given."""
    return i18n.t(
        "consent.agreed", free_limit=OPENAI_CONFIG.get("FREE_MESSAGE_LIMIT", 50)
    )


def get_gender_change_warning_text() -> str:
    """Get gender change warning text."""
    return i18n.t("gender.change_warning")


def get_gender_selection_text() -> str:
    """Get gender selection text."""
    return i18n.t("gender.choose")


def get_format_metrics_summary(metrics_summary, metrics_collector) -> str:
    return (
        f"📊 Bot Metrics\n\n"
        f"uptime_seconds: {metrics_summary['uptime_seconds']}\n"
        f"uptime_minutes: {metrics_summary['uptime_minutes']}\n\n"
        f"👥 USERS TODAY:\n"
        f"  unique_active_users: {metrics_summary['unique_active_users_today']}\n"
        f"  new_users: {metrics_summary['new_users_today']}\n"
        f"  retention_rate: {metrics_summary['retention_rate']}\n"
        f"  avg_messages_per_user: {metrics_summary['avg_messages_per_user']}\n\n"
        f"📊 ACTIVITY TODAY:\n"
        f"  total_interactions: {metrics_summary['total_interactions_today']}\n"
        f"  messages_sent: {metrics_summary['messages_sent_today']}\n"
        f"  commands_used: {metrics_summary['commands_used_today']}\n"
        f"  callback_queries: {metrics_summary['callback_queries_today']}\n"
        f"  ai_responses_sent: {metrics_summary['ai_responses_sent_today']}\n"
        f"  premium_users_active: {metrics_summary['premium_users_active_today']}\n\n"
        f"total_messages_processed: {metrics_summary['total_messages_processed']}\n"
        f"success_rate: {metrics_summary['success_rate']}\n"
        f"average_response_time: {metrics_summary['average_response_time']}\n"
        f"limit_exceeded_count: {metrics_summary['limit_exceeded_count']}\n\n"
        f"cache_hit_rate: {metrics_summary['cache_hit_rate']}\n"
        f"openai_errors: {metrics_summary['openai_errors']}\n"
        f"database_errors: {metrics_summary['database_errors']}\n"
        f"validation_errors: {metrics_summary['validation_errors']}\n\n"
        f"security_flags: {metrics_summary['security_flags']}\n"
        f"suspicious_content_detected: {metrics_summary['suspicious_content_detected']}\n"
        f"flood_attempts_blocked: {metrics_summary['flood_attempts_blocked']}\n"
        f"sanitization_applied: {metrics_summary['sanitization_applied']}\n"
        f"access_denied_count: {metrics_summary['access_denied_count']}\n\n"
        f"DEBUG - Daily user IDs count: {len(metrics_collector.metrics.daily_user_ids)}\n"
        f"DEBUG - Daily user IDs: {list(metrics_collector.metrics.daily_user_ids)}"
    )


def get_format_security_metrics(security_score: dict) -> str:
    if security_score["flags"]:
        flags_text = "Flags:\n" + "\n".join(
            f"  - {flag}" for flag in security_score["flags"]
        )
    else:
        flags_text = "No security flags detected ✅"

    return (
        f"🔒 Security Metrics\n\n"
        f"Your Security Score: {security_score['score']}/100\n"
        f"Risk Level: {security_score['risk_level']}\n"
        f"Security Flags: {len(security_score['flags'])}\n"
        f"Message Count: {security_score['message_count']}\n"
        f"Rapid Messages: {security_score['rapid_messages']}\n\n"
        f"{flags_text}"
    )


def get_format_clean_metrics_response(
    removed_count: int, cleaned_ids: set, real_user_ids: set
) -> str:
    if removed_count > 0:
        return (
            f"🧹 METRICS CLEANED\n\n"
            f"✅ Removed {removed_count} test/fake user IDs\n"
            f"✅ Kept {len(cleaned_ids)} real user IDs\n\n"
            f"**Real users: {sorted(real_user_ids)}\n"
            f"Cleaned daily IDs: {sorted(cleaned_ids) if cleaned_ids else 'None'}"
        )
    else:
        return (
            f"✅ NO TEST DATA FOUND\n\n"
            f"All {len(cleaned_ids)} daily user IDs are real users\n"
            f"**Daily IDs: {sorted(cleaned_ids) if cleaned_ids else 'None'}"
        )


def get_format_reset_daily_metrics_response() -> str:
    return (
        "🔄 **DAILY METRICS RESET**\n\n"
        "✅ All daily counters reset to 0\n"
        "✅ Daily user IDs cleared\n"
        "✅ Fresh start for today's metrics"
    )
