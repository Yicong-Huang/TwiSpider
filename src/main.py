import logging
import pickle
import threading
import time
from datetime import datetime

from twitter import Status

from crawlers.twitter_filter_api_crawler import TweetFilterAPICrawler
from crawlers.twitter_id_mode_crawler import TweetIDModeCrawler
from crawlers.twitter_retweet_crawler import TweetRetweetCrawler
from crawlers.twitter_search_api_crawler import TweetSearchAPICrawler
from dumpers.twitter_dumper import TweetDumper
from dumpers.twitter_retweet_of_dumper import TweetRetweetOfDumper
from extractor.twitter_extractor import TweetExtractor
from paths import FRONTIER_CACHE
from utilities.connection import Connection

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(threadName)s:(%(name)s) [%(funcName)s()]   %(message)s')
logger = logging.getLogger(__name__)


class Job:
    def __init__(self, tweet: Status, original_tweet_retweet_count=0):
        self.tweet_id = tweet.id
        self.tweet_created_at = datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y').timestamp()
        self.retweet_count = tweet.retweet_count - original_tweet_retweet_count
        self.last_check_time = self.tweet_created_at

    def retweet_rate(self):
        return self.retweet_count / (datetime.now().timestamp() - self.tweet_created_at)

    def __lt__(self, other):
        return self.possible_retweets() < other.possible_retweets()

    def __hash__(self):
        return self.tweet_id

    def __str__(self):
        return f'Job[id={self.tweet_id}, created_at={self.tweet_created_at}, retweet_count={self.retweet_count},' \
               f' last_check_time={self.last_check_time}, retweet_rate={self.retweet_rate()}, ' \
               f'possible_retweets={self.possible_retweets()}]'

    def __eq__(self, other):
        return hash(self) == hash(other)

    def set_check_time(self):
        self.last_check_time = datetime.now().timestamp()

    def should_check(self):
        return self.possible_retweets() > 1 or \
               (self.retweet_rate() == 0 and
                (datetime.now().timestamp() - self.last_check_time) > 15 * 60 and (
                        datetime.now().timestamp() - self.tweet_created_at) < 60 * 60 * 12)

    def possible_retweets(self):
        delta_time = datetime.now().timestamp() - self.last_check_time
        return delta_time * self.retweet_rate()

    __repr__ = __str__


class TwiSpider:

    def __init__(self, keywords=None):

        self.keywords = ['hpv vaccine', 'hpvvaccine'] if keywords is None else keywords
        try:
            print(FRONTIER_CACHE)
            with open(FRONTIER_CACHE, 'rb') as cache_file:
                self.frontier = pickle.load(cache_file)
        except:
            self.frontier = set()
        self.twitter_filter_api_crawler = TweetFilterAPICrawler()
        self.twitter_search_api_crawler = TweetSearchAPICrawler()
        self.twitter_id_mode_crawler = TweetIDModeCrawler()
        self.twitter_retweet_crawler = TweetRetweetCrawler()
        self.twitter_dumper = TweetDumper()
        self.twitter_retweet_of_dumper = TweetRetweetOfDumper()
        self.twitter_extractor = TweetExtractor()


    def run_crawler_for_root_tweets(self, crawler, batch_number):
        while True:
            root_tweet_ids = crawler.crawl(self.keywords, batch_number)
            self.crawl_for_root_tweets(root_tweet_ids)
            time.sleep(1)

    def run(self):
        self.load_root_tweets()
        threading.Thread(target=self.run_crawler_for_root_tweets, args=(self.twitter_search_api_crawler, 1)).start()
        threading.Thread(target=self.run_crawler_for_root_tweets, args=(self.twitter_filter_api_crawler, 10)).start()
        threading.Thread(target=self.run_monitor).start()

    def run_monitor(self):
        logger.info(f'monitoring {len(self.frontier)}')
        logger.info(self.frontier)
        while True:
            if self.frontier:
                check_list = sorted(filter(lambda job: job.should_check(), list(self.frontier)), reverse=True)
                if check_list:
                    logger.info(f"----> Checking {len(check_list)} in this iteration")
                    ids = [job.tweet_id for job in check_list]
                    self.crawl_for_root_tweets(ids)
                    for job in check_list:

                        logger.info(f"running for {job}")
                        new_tweets = self.twitter_retweet_crawler.crawl(job.tweet_id)

                        self.twitter_dumper.insert(self.twitter_extractor.extract(new_tweets))

                        for new_retweeted_tweet in new_tweets:
                            self.twitter_retweet_of_dumper.insert(job.tweet_id, new_retweeted_tweet.id)
                            job.retweet_count = max(job.retweet_count, new_retweeted_tweet.retweet_count)

                        job.set_check_time()
                        time.sleep(7)
                        with open(FRONTIER_CACHE, 'wb+') as cache_file:
                            pickle.dump(self.frontier, cache_file)
                        logger.info(f"done with {job}")
                else:
                    logger.info("waiting for 5 seconds")
                    rank_panel = "#### Possible Rank\n"

                    for job in sorted(list(self.frontier), reverse=True)[:10]:
                        rank_panel += f"## {job}\n"
                    rank_panel += "\n"
                    logger.info(rank_panel)
                    time.sleep(5)

                logger.info(f'monitoring {len(self.frontier)}')

    def load_root_tweets(self):
        root_tweet_ids = {id_ for (id_,) in Connection.sql_execute("select id from tweets  where text not like 'RT %'")}
        self.crawl_for_root_tweets(root_tweet_ids)

    def crawl_for_root_tweets(self, root_tweet_ids):
        logger.info("Start crawling for root tweets")
        tweets = self.twitter_id_mode_crawler.crawl(root_tweet_ids)
        root_tweets = {tweet.retweeted_status if tweet.retweeted_status else tweet for tweet in tweets}
        self.twitter_dumper.insert(self.twitter_extractor.extract(root_tweets))
        self.frontier.update({Job(tweet) for tweet in root_tweets})


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    TwiSpider().run()
