"""
Simple notification utility for experiment completion alerts.
Supports Discord webhooks and ntfy.sh.

This module is completely optional - if no notification service is configured
(DISCORD_WEBHOOK_URL or NTFY_TOPIC), all functions silently do nothing.
"""

import os
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def send_notification(
    message: str,
    title: str = "Experiment Update",
    success: bool = True
):
    """
    Send a notification via configured service.

    Checks for these environment variables:
    - DISCORD_WEBHOOK_URL: Discord webhook URL
    - NTFY_TOPIC: ntfy.sh topic name

    If neither is configured, or if requests library isn't installed,
    this function silently does nothing.

    Args:
        message: The notification message
        title: Title/header for the notification
        success: Whether this is a success or failure notification
    """
    # Skip if requests isn't available
    if not REQUESTS_AVAILABLE:
        return

    discord_url = os.getenv("DISCORD_WEBHOOK_URL")
    ntfy_topic = os.getenv("NTFY_TOPIC")

    # Skip if no notification service configured
    if not discord_url and not ntfy_topic:
        return

    emoji = "✅" if success else "❌"
    full_message = f"{emoji} **{title}**\n{message}"

    # Try Discord
    if discord_url:
        try:
            requests.post(
                discord_url,
                json={"content": full_message},
                timeout=10
            )
        except Exception:
            pass  # Silently ignore notification failures

    # Try ntfy.sh
    if ntfy_topic:
        try:
            requests.post(
                f"https://ntfy.sh/{ntfy_topic}",
                data=message.encode('utf-8'),
                headers={
                    "Title": f"{emoji} {title}",
                    "Priority": "default" if success else "high"
                },
                timeout=10
            )
        except Exception:
            pass  # Silently ignore notification failures


def notify_experiment_complete(
    experiment_name: str = None,
    success: bool = True,
    completed: int = None,
    failed: int = None,
    duration_seconds: float = None,
    extra_info: str = None
):
    """
    Send a notification about experiment completion.

    Args:
        experiment_name: Name/identifier of the experiment
        success: Whether the experiment succeeded
        completed: Number of successful experiments (for batch runs)
        failed: Number of failed experiments (for batch runs)
        duration_seconds: How long the experiment took
        extra_info: Any additional information to include
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    parts = [f"Time: {timestamp}"]

    if experiment_name:
        parts.append(f"Experiment: {experiment_name}")

    if completed is not None or failed is not None:
        completed = completed or 0
        failed = failed or 0
        parts.append(f"Results: {completed} succeeded, {failed} failed")

    if duration_seconds is not None:
        if duration_seconds > 3600:
            duration_str = f"{duration_seconds/3600:.1f} hours"
        elif duration_seconds > 60:
            duration_str = f"{duration_seconds/60:.1f} minutes"
        else:
            duration_str = f"{duration_seconds:.1f} seconds"
        parts.append(f"Duration: {duration_str}")

    if extra_info:
        parts.append(extra_info)

    message = "\n".join(parts)
    title = "Experiment Complete" if success else "Experiment Failed"

    send_notification(message, title, success)