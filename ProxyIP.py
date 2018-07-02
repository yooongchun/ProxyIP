# -*- coding: utf-8 -*-

# @Author: yooongchun
# @File: ProxyIP.py
# @Time: 2018/6/19
# @Contact: yooongchun@foxmail.com
# @blog: https://blog.csdn.net/zyc121561
# @Description: 抓取代理IP

import requests
import re
import random
import time
from bs4 import BeautifulSoup
import threading
from multiprocessing import Process
from database import IP_Pool
from UA import FakeUserAgent
import logging
import config
config.config()


class Crawl(object):
    '''抓取网页内容获取IP地址保存到数据库中'''

    def __init__(self,
                 retry_times=10,
                 proxy_flag=False,
                 proxy_database=None,
                 proxy_table=None,
                 database_name="ALL_IP.db"):
        self.__URLs = self.__URL()  # 访问的URL列表
        self.__ALL_IP_TABLE_NAME = "all_ip_table"  # 数据库表名称
        self.__DATABASE_NAME = database_name  # 数据库名称
        self.__RETRY_TIMES = retry_times  # 数据库访问重试次数
        self.__PROXIES_FLAG = proxy_flag  # 是否使用代理访问
        self.__PROXY_DATABASE = proxy_database  # 代理访问的IP数据库
        self.__PROXY_TABLE = proxy_table  # 代理访问的IP数据库表

    def __URL(self):
        '''
        返回URL列表
        URL获取地址：
        1.西刺网站
        2.快代理网站
        3.66代理网站
        4.89代理网站
        5.秘密代理网站
        6.data5u网站
        7.免费代理IP网站
        8.云代理网站
        9.全网代理网站
        '''
        URL = []
        url_xici = [
            "http://www.xicidaili.com/nn/%d" % (index + 1)
            for index in range(3275)
        ]
        url_kuaidaili = [
            "https://www.kuaidaili.com/free/inha/%d" % (index + 1)
            for index in range(2367)
        ]
        url_66 = [
            "http://www.66ip.cn/%d.html" % (index + 1) for index in range(1288)
        ]
        url_89 = [
            "http://www.89ip.cn/index_%d.html" % (index + 1)
            for index in range(9)
        ]
        url_mimi = [
            "http://www.mimiip.com/gngao/%d" % (index + 1)
            for index in range(683)
        ]
        url_data5u = ['http://www.data5u.com/free/gngn/index.shtml']
        url_yqie = ['http://ip.yqie.com/ipproxy.htm']
        url_yundaili = [
            'http://www.ip3366.net/?stype=1&page=%d' % (index + 1)
            for index in range(7)
        ]
        url_quanwangdaili = ['http://www.goubanjia.com/']

        URL = url_xici + url_kuaidaili + url_66 + url_89 + url_mimi \
            + url_data5u + url_yqie + url_yundaili + url_quanwangdaili
        random.shuffle(URL)  # 随机打乱
        return URL

    def __proxies(self, database_name, table_name):
        '''构造代理IP,需要提供代理IP保存的数据库名称和表名'''
        ip = IP_Pool(database_name, table_name).pull(
            random_flag=True, re_try_times=self.__RETRY_TIMES)
        if ip:
            IP = str(ip[0]) + ":" + str(ip[1])
            return {"http": "http://" + IP}
        else:
            return False

    def __crawl(self, url, headers, proxies=False, re_conn_times=3):
        '''爬取url'''
        for cnt in range(re_conn_times):
            try:
                if not proxies:
                    response = requests.get(
                        url=url, headers=headers, timeout=5)
                else:
                    response = requests.get(
                        url=url, headers=headers, proxies=proxies, timeout=5)
                break
            except Exception:
                response = None
                continue
        if response is None:
            logging.error(u"ProxyIP-Crawl:请求url出错：%s" % url)
            return None
        try:
            html = response.content.decode("utf-8")
            return html
        except Exception:
            logging.error(u"ProxyIP-Crawl:HTML UTF-8解码失败，尝试GBK解码...")
        try:
            html = response.content.decode("gbk")
            return html
        except Exception:
            logging.error(u"ProxyIP-Crawl:HTML解码出错，跳过！")
            return None

    def __parse(self, html):
        '''解析HTML获取IP地址'''
        if html is None:
            return
        all_ip = []
        soup = BeautifulSoup(html, "lxml")
        tds = soup.find_all("td")
        for index, td in enumerate(tds):
            logging.debug(u"ProxyIP-Crawl:页面处理进度：{}/{}".format(
                index + 1, len(tds)))
            if re.match(r"^\d+\.\d+\.\d+\.\d+$",
                        re.sub(r"\s+|\n+|\t+", "", td.text)):
                item = []
                item.append(re.sub(r"\s+|\n+|\t+", "", td.text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 1].text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 2].text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 3].text))
                item.append(re.sub(r"\s+|\n+|\t+", "", tds[index + 4].text))
                all_ip.append(item)
            else:
                logging.debug(u"不匹配的项！")
        return all_ip

    def crawl(self, url, headers, proxies):
        '''抓取IP并保存'''
        html = self.__crawl(url, headers, proxies=proxies)
        if html is None:
            return
        ip = self.__parse(html)
        if ip is None or len(ip) < 1:
            return
        if len(ip) == 1:
            IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).push([ip])
        else:
            IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).push(ip)

    def multiple_crawl(self, thread_num=10, sleep_time=15 * 60):
        '''多线程抓取'''
        count = 0
        while True:
            count += 1
            logging.info(u"ProxyIP-Crawl:开始第{}轮抓取,当前url数：{}".format(
                count, len(self.__URLs)))
            IP_NUM_A = len(
                IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).pull(
                    re_try_times=self.__RETRY_TIMES))
            cnt = 0
            st = time.time()
            while cnt < len(self.__URLs):
                pool = []
                if self.__PROXIES_FLAG:
                    proxies = self.__proxies(self.__PROXY_DATABASE,
                                             self.__PROXY_TABLE)
                else:
                    proxies = False
                for i in range(thread_num):
                    if cnt >= len(self.__URLs):
                        break
                    url = self.__URLs[cnt]
                    headers = FakeUserAgent().random_headers()
                    th = threading.Thread(
                        target=self.crawl, args=(url, headers, proxies))
                    pool.append(th)
                    logging.info(
                        u"ProxyIP-Crawl:抓取URL：{}\t 进度：{}/{}\t{:.2f}%".format(
                            url, cnt + 1, len(self.__URLs),
                            (cnt + 1) / len(self.__URLs) * 100))
                    th.start()
                    time.sleep(2 * random.random())  # 随机休眠，均值：0.5秒
                    cnt += 1
                for th in pool:
                    th.join()
            ed = time.time()
            IP_NUM_B = len(
                IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).pull(
                    re_try_times=self.__RETRY_TIMES))
            logging.info(
                u"ProxyIP-Crawl:第{}轮抓取完成,耗时：{:.2f}秒，共计抓取到IP：{}条，当前IP池中IP数：{}条".
                format(count, ed - st, IP_NUM_B - IP_NUM_A, IP_NUM_B))
            st = time.time()
            while time.time() - st < sleep_time:
                logging.info(
                    u"ProxyIP-Crawl:休眠等待：{:.2f}秒".format(sleep_time -
                                                         time.time() + st))
                time.sleep(5)

    def run(self):
        self.multiple_crawl()


class Validation(object):
    '''校验IP有效性'''

    def __init__(self, all_ip_database="ALL_IP.db", ip_database="IP.db"):
        self.__URL = "http://httpbin.org/get"
        self.__VALID_IP_TABLE_NAME = "ip_table"
        self.__ALL_IP_TABLE_NAME = "all_ip_table"
        self.__ALL_IP_DATABASE = all_ip_database
        self.__IP_DATABASE = ip_database
        self.__RETRY_TIMES = 10  # 数据库访问重试次数

    def __check_ip_anonumous(self, ip):
        '''检验IP是否高匿名'''
        logging.info(u"ProxyIP-Validation:校验IP是否高匿：{}".format(ip[0]))
        if "高匿" in str(ip):
            return True
        else:
            logging.debug(u"ProxyIP-Validation:非高匿IP：{}".format(ip[0]))
            return False

    def __check_ip_validation(self, ip):
        '''校验IP地址有效性'''
        try:
            IP = str(ip[0]) + ":" + str(ip[1])
        except Exception:
            logging.info(u"ProxyIP-Validation:IP地址格式不正确!")
            return False
        re_conn_time = 2
        logging.info(u"ProxyIP-Validation:校验IP地址有效性：{}".format(IP))
        proxies = {"http": "http://" + IP}
        headers = FakeUserAgent().random_headers()
        for i in range(re_conn_time):
            try:
                response = requests.get(
                    url=self.__URL,
                    proxies=proxies,
                    headers=headers,
                    timeout=5)
                break
            except Exception:
                response = None
                continue
        if response is None:
            logging.error(u"ProxyIP-Validation:请求校验IP的网络错误！")
            return False
        return True

    def __filter_ip(self, ip):
        '''验证数据库中的IP地址是否有效,校验后删除'''
        if self.__check_ip_validation(ip) and self.__check_ip_anonumous(ip):
            IP_Pool(self.__IP_DATABASE, self.__VALID_IP_TABLE_NAME).push(
                [ip], re_try_times=self.__RETRY_TIMES)
        # 校验后删除
        IP_Pool(self.__ALL_IP_DATABASE, self.__ALL_IP_TABLE_NAME).delete(
            IP=ip, re_try_times=self.__RETRY_TIMES)

    def multiple_filter(self, thread_num=10, sleep=15 * 60):
        '''多线程验证'''
        IPs = IP_Pool(
            self.__ALL_IP_DATABASE,
            self.__ALL_IP_TABLE_NAME).pull(re_try_times=self.__RETRY_TIMES)
        count = 0
        while True:
            count += 1
            st = time.time()
            logging.info(u"ProxyIP-Validation:第{}轮验证开始，共计需验证IP:{} 条".format(
                count, len(IPs)))
            cnt = 0
            while cnt < len(IPs):
                pool = []
                for i in range(thread_num):
                    if cnt >= len(IPs):
                        break
                    logging.info(
                        u"ProxyIP-Validation:校验进度：{}/{}\t{:.2f}%".format(
                            cnt, len(IPs), cnt / len(IPs) * 100))
                    th = threading.Thread(
                        target=self.__filter_ip, args=(IPs[cnt], ))
                    th.start()
                    time.sleep(2 * random.random())
                    pool.append(th)
                    cnt += 1
                for th in pool:
                    th.join()
            ed = time.time()
            IP = IP_Pool(self.__IP_DATABASE, self.__VALID_IP_TABLE_NAME).pull(
                re_try_times=self.__RETRY_TIMES)
            logging.info(
                u"ProxyIP-Validation:第{}轮验证结束，耗时：{:.2f}\t共计验证IP:{}条\t当前IP池中有效IP:{}条".
                format(count, ed - st, len(IPs), len(IP)))
            st = time.time()
            while time.time() - st < sleep:
                logging.info(u"ProxyIP-Validation:休眠倒计时：{:.2f}秒".format(
                    sleep - time.time() + st))
                time.sleep(5)

    def __validation(self, ip):
        '''校验有效IP池中的IP有效性，无效则删除'''
        if not self.__check_ip_validation(ip):
            IP_Pool(self.__IP_DATABASE, self.__VALID_IP_TABLE_NAME).delete(
                IP=ip, re_try_times=self.__RETRY_TIMES)

    def multiple_validation(self, thread_num=20, sleep=15 * 60):
        '''定时校验有效IP池里的IP，无效的删除'''
        IPs = IP_Pool(
            self.__IP_DATABASE,
            self.__VALID_IP_TABLE_NAME).pull(re_try_times=self.__RETRY_TIMES)
        count = 0
        while True:
            count += 1
            logging.info(u"ProxyIP-Validation:第{}次校验，IP数：{}".format(
                count, len(IPs)))
            cnt = 0
            while cnt < len(IPs):
                pool = []
                for i in range(thread_num):
                    if cnt >= len(IPs):
                        break
                    logging.info(
                        u"ProxyIP-Validation:校验进度：{}/{}\t{:.2f}%".format(
                            cnt, len(IPs), cnt / len(IPs) * 100))
                    th = threading.Thread(
                        target=self.__validation, args=(IPs[cnt], ))
                    th.start()
                    time.sleep(2 * random.random())
                    pool.append(th)
                    cnt += 1
                for th in pool:
                    th.join()
            ips = IP_Pool(self.__IP_DATABASE, self.__VALID_IP_TABLE_NAME).pull(
                re_try_times=self.__RETRY_TIMES)
            logging.info(u"ProxyIP-Validation:完成第{}次校验，当前有效IP数：{}".format(
                count, len(ips)))
            logging.info(u"ProxyIP-Validation:进入休眠：{} 秒".format(sleep))
            time.sleep(sleep)

    def run(self):
        '''启动程序'''
        p1 = Process(target=self.multiple_filter)
        p2 = Process(target=self.multiple_validation)
        p1.start()
        p2.start()
        p1.join()
        p2.join()


def main():
    # 初始化
    crawl = Crawl()
    validation = Validation()
    p1 = Process(target=crawl.run)
    p2 = Process(target=validation.run)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == "__main__":
    # Crawl().run()
    # Validation().run()
    main()
