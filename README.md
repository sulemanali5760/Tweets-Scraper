# Tweets-Scraper

This script monitors a user's timeline for tweets that match specific search
terms and can push notifications via Pushover when a new tweet is detected.

## Configuration

Set environment variables to adjust the behavior:

- `TWITTER_USERNAME` – Username to monitor (default: `brecordernews`).
- `TWEET_SEARCH_TERMS` – Comma-separated terms combined with `OR` in the search
  query (default: `economy,inflation,demand,dollar,business`).
- `TWEET_LIMIT` – Number of tweets twint should fetch per poll (default: `10`).
- `TWEET_LANGUAGE` – Language filter (default: `en`).
- `POLLING_INTERVAL` – Seconds to sleep between polls (default: `15`).
- `STATE_FILE` – Path to the JSON file where the last tweet id is stored
  (default: `last_tweet.json`).
- `PUSHOVER_TOKEN` and `PUSHOVER_USER` – Credentials for Pushover
  notifications. If either is missing, notifications are skipped.

## Usage

Install dependencies and run the monitor:

```bash
pip install -r requirements.txt
python tweets.py
```

The script will poll on a loop, save the latest tweet id to `STATE_FILE`, and
send a Pushover notification whenever a new tweet is seen.
