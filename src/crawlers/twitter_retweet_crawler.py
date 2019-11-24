import logging
import time
import traceback
from typing import List

import twitter

from crawlers.crawlerbase import CrawlerBase
from paths import TWITTER_API_CONFIG_PATH
from utilities.ini_parser import parse

logger = logging.getLogger(__name__)


class TweetRetweetCrawler(CrawlerBase):
    MAX_WAIT_TIME = 64

    def __init__(self):
        super().__init__()
        self.wait_time = 1
        self.api = twitter.Api(**parse(TWITTER_API_CONFIG_PATH, 'twitter-API'))
        self.data: List[twitter.Status] = []
        self.total_crawled_count = 0

    def crawl(self, tweet_id) -> List[twitter.Status]:
        """
        Crawling twitter.Status with the given Tweet Id.

        Args:
            tweet_id (int): the tweet id to be crawled

        Returns:
            twitter.Status

        """
        logger.info(f'Crawler Started')
        while True:
            try:
                logger.info(f'Sending a Request to Twitter Get Retweets API')
                tweets = self.api.GetRetweets(tweet_id, count=100)
                self.reset_wait_time()
                return tweets
            except:
                logger.error('error: ' + traceback.format_exc())
                # in this case the collected twitter id will be recorded and tried again next time

                self.wait()

    def reset_wait_time(self):
        """resets the wait time"""
        self.wait_time = 1

    def wait(self) -> None:
        """Incrementally waits when the request rate hits limitation."""
        time.sleep(self.wait_time)
        if self.wait_time < self.MAX_WAIT_TIME:  # set a wait time limit no longer than 64s
            self.wait_time *= 2  # an exponential back-off pattern in subsequent reconnection attempts


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    tweet_retweet_crawler = TweetRetweetCrawler()

    status = tweet_retweet_crawler.crawl(1198263248036007936)
    print(status)
