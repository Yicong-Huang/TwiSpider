import os

# root path of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# directory for all runnable tasks
# the task directory should not be changed, otherwise the task manager will crash
TASK_DIR = os.path.join(ROOT_DIR, 'backend', 'task')
# directory for all tasks' logs
LOG_DIR = os.path.join(ROOT_DIR, 'backend', 'logs')

# dir for all configs
CONFIGS_DIR = os.path.join(ROOT_DIR, 'configs')

# path of the config file for connection to postgresql
DATABASE_CONFIG_PATH = os.path.join(CONFIGS_DIR, 'database.ini')
# path of the config file for twitter api
TWITTER_API_CONFIG_PATH = os.path.join(CONFIGS_DIR, 'twitter.ini')
# path of the config file for logging in task manager
LOG_CONFIG_PATH = os.path.join(CONFIGS_DIR, 'logger-conf.json')

# dir for all cache
CACHE_DIR = os.path.join(ROOT_DIR, 'cache')

FRONTIER_CACHE = os.path.join(CACHE_DIR, 'twitter.frontier.pickle')
