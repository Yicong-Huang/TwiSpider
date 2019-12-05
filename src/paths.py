import os

# root path of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# directory for logs
LOG_DIR = os.path.join(ROOT_DIR, 'backend', 'logs')

# dir for all configs
CONFIGS_DIR = os.path.join(ROOT_DIR, 'configs')

# path of the config file for connection to postgresql
DATABASE_CONFIG_PATH = os.path.join(CONFIGS_DIR, 'database.ini')
# path of the config file for twitter api
TWITTER_API_CONFIG_PATH = os.path.join(CONFIGS_DIR, 'twitter.ini')

# dir for all cache
CACHE_DIR = os.path.join(ROOT_DIR, 'cache')
# path of the job frontier set
FRONTIER_CACHE_PATH = os.path.join(CACHE_DIR, 'twitter.frontier.pickle')
# path of the id CacheSet
ID_CACHE_PATH = os.path.join(CACHE_DIR, 'ids.pickle')

# path for keywords.txt
KEYWORDS_PATH = os.path.join(ROOT_DIR, 'keywords.txt')
