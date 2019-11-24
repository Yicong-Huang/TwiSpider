import logging
import pickle
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

logger = logging.getLogger(__name__)


class Job:
    def __init__(self, tweet: Status, original_tweet_retweet_count=0):
        self.tweet_id = tweet.id
        self.tweet_created_at = datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y').timestamp()
        self.retweet_count = tweet.retweet_count - original_tweet_retweet_count

        print(self.tweet_id, self.retweet_rate())

    def retweet_rate(self):
        return self.retweet_count / (datetime.now().timestamp() - self.tweet_created_at)

    def __lt__(self, other):
        return self.retweet_rate() < other.retweet_rate()

    def __hash__(self):
        return self.tweet_id

    def __str__(self):
        return f'Job[id={self.tweet_id}, created_at={self.tweet_created_at}, retweet_count={self.retweet_count}]'

    def __eq__(self, other):
        return hash(self) == hash(other)

    __repr__ = __str__


class TriSpider:

    def __init__(self, keywords=None):

        self.keywords = ['hpv vaccine', 'hpvvaccine'] if keywords is None else keywords
        try:
            self.frontier = pickle.load(open(FRONTIER_CACHE, 'rb'))
        except:
            self.frontier = set()
        self.twitter_filter_api_crawler = TweetFilterAPICrawler()
        self.twitter_search_api_crawler = TweetSearchAPICrawler()
        self.twitter_id_mode_crawler = TweetIDModeCrawler()
        self.twitter_retweet_crawler = TweetRetweetCrawler()
        self.twitter_dumper = TweetDumper()
        self.twitter_retweet_of_dumper = TweetRetweetOfDumper()
        self.twitter_extractor = TweetExtractor()

    def _initial_run(self):

        retweeted_tweets = \
            list(filter(lambda tweet: tweet.retweet_count, self.twitter_id_mode_crawler.crawl(
                self.twitter_search_api_crawler.crawl(self.keywords, batch_number=20))))

        self.twitter_dumper.insert(self.twitter_extractor.extract(retweeted_tweets))
        self.frontier.update({Job(tweet) for tweet in retweeted_tweets})

        original_tweets = list(filter(lambda x: x, [tweet.retweeted_status for tweet in retweeted_tweets]))
        self.twitter_dumper.insert(self.twitter_extractor.extract(original_tweets))
        self.frontier.update({Job(tweet) for tweet in original_tweets})

    def run(self):
        if not self.frontier:
            self._initial_run()

        print('monitoring', len(self.frontier))
        print(self.frontier)
        check_time = datetime.now()
        while True:
            if (datetime.now() - check_time).total_seconds() < 20 * 60:
                check_list = sorted(list(filter(lambda job: job.retweet_rate(), self.frontier)), reverse=True)
            else:
                check_list = sorted(list(self.frontier), reverse=True)
                check_time = datetime.now()
            print(f"----> Checking {len(check_list)} in this iteration")
            for job in check_list:

                print(job.tweet_id, job.tweet_created_at, job.retweet_rate())
                new_tweets = self.twitter_retweet_crawler.crawl(job.tweet_id, )
                print(job.tweet_id, new_tweets)

                self.twitter_dumper.insert(self.twitter_extractor.extract(new_tweets))
                for new_retweeted_tweet in new_tweets:
                    self.twitter_retweet_of_dumper.insert(job.tweet_id, new_retweeted_tweet.id)

                count, = next(
                    Connection.sql_execute(f"select count(*) from retweet_of where original_tweet_id = {job.tweet_id}"))

                job.retweet_count = max(job.retweet_count, count)
                self.frontier.update({Job(tweet, job.retweet_count) for tweet in new_tweets})
                time.sleep(10)

            print('monitoring', len(self.frontier))


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    TriSpider().run()
