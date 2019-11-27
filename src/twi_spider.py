import logging
import pickle
import threading
import time

from crawlers.twitter_filter_api_crawler import TweetFilterAPICrawler
from crawlers.twitter_id_mode_crawler import TweetIDModeCrawler
from crawlers.twitter_retweet_crawler import TweetRetweetCrawler
from crawlers.twitter_search_api_crawler import TweetSearchAPICrawler
from dumpers.twitter_dumper import TweetDumper
from dumpers.twitter_retweet_of_dumper import TweetRetweetOfDumper
from extractor.twitter_extractor import TweetExtractor
from job import Job
from paths import FRONTIER_CACHE
from utilities.connection import Connection

logger = logging.getLogger(__name__)


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
