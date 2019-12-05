# TwiSpider
Crawling Tweets as a Network.

Given a list of keywords, TwiSpider will crawl for real time tweets with this keyword(s). It saves the original tweet of it if that's a retweet.
It then monitors the original tweets in a regualar basis.

# Setup
## Environment
postgresql@11

postgis@3.0

python@3.6+

## Dependency
`pip install -r requirements.txt`

# Quick Start
`python3 src/main.py`
