# Scrapy settings for zhihu project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import sys
import os
from os.path import dirname
path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(path)
from misc.log import *

BOT_NAME = 'zhihu'

SPIDER_MODULES = ['zhihu.spiders']
NEWSPIDER_MODULE = 'zhihu.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'zhihu (+http://www.yourdomain.com)'

# DOWNLOADER_MIDDLEWARES = {
#     # 'misc.middleware.CustomHttpProxyMiddleware': 400,
#     'misc.middleware.CustomUserAgentMiddleware': 401,
# }

ITEM_PIPELINES = {
    'zhihu.pipelines.JsonWithEncodingPipeline': 300,
    # 'zhihu.pipelines.RedisPipeline': 301,
}

LOG_LEVEL = 'INFO'

COOKIES_ENABLED = True

DOWNLOAD_DELAY = 1
