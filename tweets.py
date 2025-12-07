"""
Script for monitoring tweets from a specific user with keyword filtering and
sending Pushover notifications when a new tweet appears.

Configuration is sourced from environment variables and sensible defaults to
avoid hard-coded credentials in the source code.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
import twint


@dataclass
class MonitorSettings:
    """Settings that control tweet monitoring and notifications."""

    username: str
    search_terms: list[str]
    limit: int = 10
    language: str = "en"
    polling_interval: int = 15
    state_file: Path = Path("last_tweet.json")
    pushover_token: Optional[str] = None
    pushover_user: Optional[str] = None

    @property
    def search_query(self) -> str:
        return " OR ".join(self.search_terms)


def build_config_from_env() -> MonitorSettings:
    """Create settings from environment variables with fallbacks."""

    username = os.environ.get("TWITTER_USERNAME", "brecordernews")
    terms = os.environ.get(
        "TWEET_SEARCH_TERMS",
        "economy,inflation,demand,dollar,business",
    )
    search_terms = [term.strip() for term in terms.split(",") if term.strip()]

    limit = int(os.environ.get("TWEET_LIMIT", 10))
    language = os.environ.get("TWEET_LANGUAGE", "en")
    polling_interval = int(os.environ.get("POLLING_INTERVAL", 15))
    state_file = Path(os.environ.get("STATE_FILE", "last_tweet.json"))

    pushover_token = os.environ.get("PUSHOVER_TOKEN")
    pushover_user = os.environ.get("PUSHOVER_USER")

    return MonitorSettings(
        username=username,
        search_terms=search_terms,
        limit=limit,
        language=language,
        polling_interval=polling_interval,
        state_file=state_file,
        pushover_token=pushover_token,
        pushover_user=pushover_user,
    )


def load_last_tweet_id(state_file: Path) -> Optional[int]:
    """Read the last processed tweet id from disk."""

    if not state_file.exists():
        return None

    try:
        with state_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            return int(data.get("tweet_id"))
    except (json.JSONDecodeError, OSError, ValueError):
        return None


def save_last_tweet(state_file: Path, tweet_id: int, tweet_text: str) -> None:
    """Persist the latest seen tweet id and text to disk."""

    state_file.parent.mkdir(parents=True, exist_ok=True)
    with state_file.open("w", encoding="utf-8") as handle:
        json.dump({"tweet_id": tweet_id, "tweet": tweet_text}, handle, indent=2)


def fetch_latest_tweet(settings: MonitorSettings) -> Optional[dict]:
    """Fetch the newest tweet object using twint for the configured user."""

    twint.output.tweets_list.clear()

    config = twint.Config()
    config.Username = settings.username
    config.Search = settings.search_query
    config.Limit = settings.limit
    config.Lang = settings.language
    config.Store_object = True

    twint.run.Search(config)

    if not twint.output.tweets_list:
        return None

    latest_tweet = twint.output.tweets_list[0]
    return {"id": int(latest_tweet.id), "text": latest_tweet.tweet}


def notify_pushover(settings: MonitorSettings, message: str) -> None:
    """Send a Pushover notification if credentials are available."""

    if not settings.pushover_token or not settings.pushover_user:
        return

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": settings.pushover_token,
            "user": settings.pushover_user,
            "message": message,
        },
        timeout=10,
    )
    response.raise_for_status()


def monitor() -> None:
    """Continuously monitor for new tweets and send notifications."""

    settings = build_config_from_env()
    last_seen_id = load_last_tweet_id(settings.state_file)

    while True:
        tweet = fetch_latest_tweet(settings)

        if not tweet:
            time.sleep(settings.polling_interval)
            continue

        tweet_id = tweet["id"]
        tweet_text = tweet["text"]

        if last_seen_id is None or tweet_id != last_seen_id:
            save_last_tweet(settings.state_file, tweet_id, tweet_text)
            notify_pushover(settings, f"@{settings.username}: {tweet_text}")
            last_seen_id = tweet_id

        time.sleep(settings.polling_interval)


if __name__ == "__main__":
    monitor()
