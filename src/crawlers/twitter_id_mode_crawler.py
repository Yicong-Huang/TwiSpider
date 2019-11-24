import logging
import time
import traceback
from typing import List, Iterable

import twitter

from crawlers.crawlerbase import CrawlerBase
from crawlers.twitter_filter_api_crawler import TweetFilterAPICrawler
from paths import TWITTER_API_CONFIG_PATH
from utilities.ini_parser import parse

logger = logging.getLogger(__name__)


class TweetIDModeCrawler(CrawlerBase):
    MAX_WAIT_TIME = 64

    def __init__(self):
        super().__init__()
        self.wait_time = 1
        self.api = twitter.Api(**parse(TWITTER_API_CONFIG_PATH, 'twitter-API'))
        self.data: List[twitter.Status] = []
        self.total_crawled_count = 0

    def crawl(self, ids: Iterable[int]) -> List[twitter.Status]:
        """
        Crawling twitter.Status with the given Tweet Id list.

        Args:
            ids (List[int]): list of Tweet IDs to be crawled, can contain duplicates.

        Returns:
            List[twitter.Status]

        """
        logger.info(f'Crawler Started')
        unique_ids = list(set(ids))
        while True:
            try:
                logger.info(f'Sending a Request to Twitter Get Status API')
                self.data = self.api.GetStatuses(unique_ids)
                self.reset_wait_time()
            except:
                logger.error('error: ' + traceback.format_exc())
                # in this case the collected twitter id will be recorded and tried again next time

                self.wait()
            else:
                break

        count = len(self.data)
        logger.info(f'Returning twitter.Status count: {count}')
        self.total_crawled_count += count
        logger.info(f'Total crawled count {self.total_crawled_count}')

        # save crawled to self.data (in-memory), or, if needed, to disk file
        # also return a reference of self.data
        return self.data

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

    tweet_filter_api_crawler = TweetFilterAPICrawler()

    tweet_id_mode_crawler = TweetIDModeCrawler()

    raw_ids = [1198357190844846081, 1198381629049315329]

    status = tweet_id_mode_crawler.crawl(raw_ids)
    for statu in status:
        print(statu)
