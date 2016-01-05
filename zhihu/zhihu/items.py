# -*- coding:utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ZhihuPeopleItem(Item):
    # define the fields for your item here like:
    id = Field()
    name = Field()
    sign = Field()
    location = Field()
    business = Field()
    employment = Field()
    position = Field()
    education = Field()
    education_extra = Field()
    description = Field()
    agree = Field()
    thanks = Field()
    asks = Field()
    answers = Field()
    posts = Field()
    collections = Field()
    logs = Field()
    followees = Field()
    followers = Field()
    follow_topics = Field()


class QuestionItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()  # 保存抓取问题的url
    title = Field()  # 抓取问题的标题
    description = Field()  # 抓取问题的描述
    answer = Field()  # 抓取问题的答案
    name = Field()  # 个人用户的名称
