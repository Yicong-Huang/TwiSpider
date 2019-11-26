import logging
import pickle
import time
import traceback
from typing import List

from tokenizer import tokenize, TOK

from api.twitter_api_load_balancer import TwitterAPILoadBalancer
from crawlers.crawlerbase import CrawlerBase
from paths import ID_CACHE
from utilities.cacheset import CacheSet

logger = logging.getLogger(__name__)


class TweetFilterAPICrawler(CrawlerBase):
    MAX_WAIT_TIME = 64

    def __init__(self):
        super().__init__()
        self.wait_time = 1
        self.api_load_balancer = TwitterAPILoadBalancer()
        self.data: List = []
        self.keywords = []
        self.total_crawled_count = 0
        try:
            with open(ID_CACHE, 'rb') as cache_file:
                self.cache = pickle.load(cache_file)
        except:
            self.cache: CacheSet[int] = CacheSet()

    def crawl(self, keywords: List, batch_number: int = 100) -> List[int]:
        """
        Crawling Tweet ID with the given keyword lists, using Twitter Filter API

        Twitter Filter API only provides compatibility mode, thus no `full_text` is returned by the API. Have to crawl
        for IDs and then fetch full_text with GetStatus, which will be in other thread.

        Args:

            keywords (List[str]): keywords that to be used for filtering tweet text, hash-tag, etc. Exact behavior
                is defined by python-twitter.

            batch_number (int): a number that limits the returned list length. using 100 as default since Twitter API
                limitation is set to 100 IDs per request.

        Returns:
             (List[int]): a list of Tweet IDs

        """
        self.keywords = list(map(str.lower, keywords + ["#" + keyword for keyword in keywords]))
        logger.info(f'Crawler Started')
        self.data = []
        count = 0
        while len(self.data) < batch_number:
            logger.info(f'Sending a Request to Twitter Filter API')
            try:

                for tweet in self.api_load_balancer.get().GetStreamFilter(track=self.keywords, languages=['en']):
                    self.reset_wait_time()
                    if tweet.get('retweeted_status'):
                        self._add_to_batch(tweet['retweeted_status']['id'])
                    else:
                        self._add_to_batch(tweet['id'])

                    # print Crawling info
                    if len(self.data) > count:
                        count = len(self.data)
                        if count % (batch_number // 10) == 0:
                            logger.info(f"Crawled ID count in this batch: {count}")

                    if count >= batch_number:
                        break

            except:
                # in this case the collected twitter id will be recorded and tried again next time
                logger.error(f'Error: {traceback.format_exc()}')
                self.wait()

        count = len(self.data)
        with open(ID_CACHE, 'wb+') as cache_file:
            pickle.dump(self.cache, cache_file)
        logger.info(f'Outputting {count} Tweet IDs')
        self.total_crawled_count += count
        logger.info(f'Total crawled count {self.total_crawled_count}')
        return self.data

    @staticmethod
    def _tokenize_tweet_text(tweet):
        return set(txt for kind, txt, _ in tokenize(tweet['text']) if kind in [TOK.WORD, TOK.HASHTAG])

    def _add_to_batch(self, tweet_id: int) -> None:
        if tweet_id not in self.cache:
            self.data.append(tweet_id)
            self.cache.add(tweet_id)

    def reset_wait_time(self) -> None:
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
    for _ in range(3):
        raw_tweets = tweet_filter_api_crawler.crawl(['hpv vaccine', 'hpvvaccine'], batch_number=1)
        print(raw_tweets)
