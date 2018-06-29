# -*- coding: utf-8 -*-

# @Author: yooongchun
# @File: UA.py
# @Time: 2018/6/19
# @Contact: yooongchun@foxmail.com
# @blog: https://blog.csdn.net/zyc121561
# @Description: 生成随机请求头，模拟不同浏览器

import random
import requests


class FakeUserAgent(object):
    """
    生成随机请求头
    """

    def __init__(self):
        self.__uas = [
            "User-Agent,Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "User-Agent,Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "User-Agent,Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
            "User-Agent,Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
            "User-Agent,Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
            "User-Agent, Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
            "User-Agent,Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
            "User-Agent,Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
            "User-Agent,Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
            "User-Agent, Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
            "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"
        ]
        self.__referer = [
            "https://www.baidu.com/", "https://www.google.com.hk/",
            "https://cn.bing.com/", "https://www.sogou.com/",
            "https://www.so.com/"
        ]

    def __get_random_ua(self):
        return self.__uas[random.randint(0, len(self.__uas) - 1)]

    def get_random_headers(self):
        ua = self.__get_random_ua()
        headers = {
            "User-Agent": ua,
            "Referer": self.__referer[random.randint(0,
                                                     len(self.__referer) - 1)]
        }
        return headers


if __name__ == "__main__":
    cnt = 0
    while True:
        ua = FakeUserAgent().get_random_headers()
        try:
            requests.get(url="https://www.baidu.com", headers=ua, timeout=3)
            print("%s 有效！" % cnt)

        except Exception:
            print("无效请求头:%s" % ua)
        cnt += 1
