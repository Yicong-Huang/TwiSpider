from datetime import datetime

from twitter import Status


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
