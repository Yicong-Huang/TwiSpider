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

1. Fill in configs. Make a copy from `.template` files. For example, copy a file from `twitter.ini.template` and name it as `twitter.ini`, fill your api information inside.

2. Edit `src/keywords.txt` for monitored keywords, one at a line. Space means boolean AND. `hpv vaccine` will monitor tweets that  both contain `hpv` and `vaccine` 

3. Run with `python3 src/main.py`
