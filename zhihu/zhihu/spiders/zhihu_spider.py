# coding: utf-8

from urlparse import urlparse

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.http import Request

from zhihu.items import *
from misc.log import *

import requests

import sys
reload(sys)
sys.setdefaultencoding('utf8')

'''
1. 默认取sel.css()[0]，如否则需要'__unique':false
2. 默认字典均为css解析，如否则需要'__use':'dump'表明是用于dump数据
'''


class ZhihuSpider(CrawlSpider):
    name = "zhihu"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        # "http://www.zhihu.com/",
        # "https://www.zhihu.com/people/hu-shi-wei-63",
        "https://www.zhihu.com/people/hu-shi-wei-63/followees",
    ]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
        'Referer': 'http://www.zhihu.com/',
    }
    rules = [
        # Rule(LinkExtractor(allow=("/people/[^/]+/followees$", )),
        #      callback='parse_followees'),
        # Rule(LinkExtractor(allow=("/people/[^/]+/followers$", )),
        #      callback='parse_followers'),
        Rule(LinkExtractor(allow=("/people/[^/]+$", )),
             callback='parse_people_with_rules', follow=True),
        Rule(LinkExtractor(allow=('/question/\d+#.*?', )),
             callback='parse_question', follow=True),
        Rule(LinkExtractor(allow=('/question/\d+', )),
             callback='parse_question', follow=True),
    ]

    # need dfs/bfs
    all_css_rules = {
        '.zm-profile-header': {
            '.zm-profile-header-main': {
                '__use': 'dump',
                'name': '.title-section .name::text',
                'sign': '.title-section .bio::text',
                'location': '.location.item::text',
                'business': '.business.item::text',
                'employment': '.employment.item::text',
                'position': '.position.item::text',
                'education': '.education.item::text',
                'education_extra': '.education-extra.item::text',
            },
            '.zm-profile-header-operation': {
                '__use': 'dump',
                'agree': '.zm-profile-header-user-agree strong::text',
                'thanks': '.zm-profile-header-user-thanks strong::text',
            },
            '.profile-navbar': {
                '__use': 'dump',
                'asks': 'a[href*=asks] .num::text',
                'answers': 'a[href*=answers] .num::text',
                'posts': 'a[href*=posts] .num::text',
                'collections': 'a[href*=collections] .num::text',
                'logs': 'a[href*=logs] .num::text',
            },
        },
        '.zm-profile-side-following': {
            '__use': 'dump',
            'followees': 'a.item[href*=followees] strong::text',
            'followers': 'a.item[href*=followers] strong::text',
        }
    }

    def start_requests(self):
        return [Request("https://www.zhihu.com/login/email", meta={'cookiejar': 1}, callback=self.post_login)]

    def get_captcha(self):
        s = requests.session()
        captcha_url = 'http://www.zhihu.com/captcha.gif'
        captcha = s.get(captcha_url, stream=True)
        print captcha
        f = open('captcha.gif', 'wb')
        for line in captcha.iter_content(10):
            f.write(line)
        f.close()
        return s

    # FormRequeset出问题了
    def post_login(self, response):
        print 'Preparing login'
        # 下面这句话用于抓取请求网页后返回网页中的_xsrf字段的文字, 用于成功提交表单
        xsrf = Selector(response).xpath(
            '//input[@name="_xsrf"]/@value').extract()[0]
        s = self.get_captcha()
        captcha_str = raw_input('Input captcha:')
        logindata = {
            '_xsrf': xsrf,
            'email': '531409927@qq.com',
            'password': '***',
            'rememberme': 'true',
            'captcha': captcha_str
        }
        res = s.post(
            'https://www.zhihu.com/login/email', headers=self.headers, data=logindata)
        cookies = dict(res.cookies)
        for url in self.start_urls:
            yield Request(url, cookies=cookies)

    def traversal(self, sel, rules, item):
        if '__use' in rules:
            for nk, nv in rules.items():
                if nk == '__use':
                    continue
                if nk not in item:
                    item[nk] = []
                if sel.css(nv):
                    item[nk] += [i.extract() for i in sel.css(nv)]
                else:
                    item[nk] = []
        else:
            for nk, nv in rules.items():
                for i in sel.css(nk):
                    self.traversal(i, nv, item)

    def dfs(self, sel, rules, item_class):
        if sel is None:
            return []
        item = item_class()
        self.traversal(sel, rules, item)
        return item

    def parse_with_rules(self, response, rules, item_class):
        return self.dfs(Selector(response), rules, item_class)

    def parse_people_with_rules(self, response):
        info('Parsed ' + response.url)
        item = self.parse_with_rules(
            response, self.all_css_rules, ZhihuPeopleItem)
        item['id'] = urlparse(response.url).path.split('/')[-1]
        yield item

    def parse_followers(self, response):
        return self.parse_people_with_rules(response)

    def parse_followees(self, response):
        return self.parse_people_with_rules(response)

    def parse_question(self, response):
        problem = Selector(response)
        item = QuestionItem()
        item['url'] = response.url
        item['name'] = problem.xpath('//span[@class="name"]/text()').extract()
        item['title'] = problem.xpath(
            '//h2[@class="zm-item-title zm-editable-content"]/text()').extract()
        item['description'] = problem.xpath(
            '//div[@class="zm-editable-content"]/text()').extract()
        item['answer'] = problem.xpath(
            '//div[@class="zm-editable-content clearfix"]/text()').extract()
        return item
