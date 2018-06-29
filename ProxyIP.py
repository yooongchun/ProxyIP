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
from datetime import datetime
import threading
from multiprocessing import Process
from database import IP_Pool
from UA import FakeUserAgent
import logging
import config
config.config()


class Crawl(object):
    '''抓取网页内容获取IP地址保存到数据库中'''

    def __init__(self, database_name, valid_ip_table_name, all_ip_table_name):
        self.__URLs = self.__URL()
        self.__ALL_IP_TABLE_NAME = all_ip_table_name
        self.__VALID_IP_TABLE_NAME = valid_ip_table_name
        self.__DATABASE_NAME = database_name

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
        url_xici = ["http://www.xicidaili.com"]
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

    def __proxies(self):
        '''构造代理IP'''
        ip = IP_Pool(self.__DATABASE_NAME,
                     self.__VALID_IP_TABLE_NAME).pull(random_flag=True)
        if ip is not None:
            IP = str(ip[0]) + ":" + str(ip[1])
            return {"http": "http://" + IP}
        else:
            return None

    def __crawl(self, url, re_conn_times=3):
        '''爬取url'''
        headers = FakeUserAgent().get_random_headers()
        cnt = 0
        while cnt < re_conn_times:
            cnt += 1
            try:
                proxies = self.__proxies()
                if proxies is None:
                    response = requests.get(
                        url=url, headers=headers, timeout=5)
                else:
                    response = requests.get(
                        url=url, headers=headers, proxies=proxies, timeout=5)
                break
            except Exception:
                logging.debug("第{}次网络连接出错,重试!".format(cnt))
                response = None
        if response is None:
            logging.error("当前网络不可用，请检查网络连接后重试！")
            return None
        if not int(response.status_code) == 200:
            logging.error("响应出错，退出！")
            return None
        try:
            html = response.content.decode("utf-8")
        except Exception:
            try:
                html = response.content.decode("gbk")
            except Exception:
                logging.error("解码出错！")
                return None
        return html

    def __parse(self, url):
        '''解析HTML获取IP地址并保存到数据库中'''
        html = self.__crawl(url)
        if html is None:
            logging.debug("抓取失败！")
            return
        all_ip = []
        try:
            soup = BeautifulSoup(html, "lxml")
            tds = soup.find_all("td")
            for index, td in enumerate(tds):
                logging.debug("当前页面处理进度：{}/{}".format(index + 1, len(tds)))
                if re.match(r"^\d+\.\d+\.\d+\.\d+$",
                            re.sub(r"\s+|\n+|\t+", "", td.text)):
                    item = []
                    item.append(re.sub(r"\s+|\n+|\t+", "", td.text))
                    item.append(
                        re.sub(r"\s+|\n+|\t+", "", tds[index + 1].text))
                    item.append(
                        re.sub(r"\s+|\n+|\t+", "", tds[index + 2].text))
                    item.append(
                        re.sub(r"\s+|\n+|\t+", "", tds[index + 3].text))
                    item.append(
                        re.sub(r"\s+|\n+|\t+", "", tds[index + 4].text))
                    all_ip.append(item)
        except Exception:
            logging.error("解析html出错,返回！")
            return
        if len(all_ip) > 0:
            IP_Pool(self.__DATABASE_NAME,
                    self.__ALL_IP_TABLE_NAME).push(all_ip)

    def multiple_crawl(self, thread_num=10, sleep_time=60 * 60):
        '''多线程抓取'''
        count = 0
        while True:
            count += 1
            logging.info(u"{}\t开始第{}轮抓取,当前url数：{}".format(
                datetime.now(), count, len(self.__URLs)))
            IP_NUM_A = len(
                IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).pull())
            cnt = 0
            st = time.time()
            while cnt < len(self.__URLs):
                pool = []
                for i in range(thread_num):
                    if cnt >= len(self.__URLs):
                        break
                    url = self.__URLs[cnt]
                    th = threading.Thread(target=self.__parse, args=(url, ))
                    pool.append(th)
                    logging.info(u"{}\t 抓取URL：{}\t 当前进度：{}/{}\t{:.2f}%".format(
                        datetime.now(), url, cnt + 1, len(self.__URLs),
                        (cnt + 1) / len(self.__URLs) * 100))
                    th.start()
                    time.sleep(random.random())  # 随机休眠，均值：0.5秒
                    cnt += 1
                for th in pool:
                    th.join()
            ed = time.time()
            IP_NUM_B = len(
                IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).pull())
            logging.info(
                "{}\t第{}轮抓取完成,耗时：{:.2f}秒，共计抓取到IP：{}条，当前IP池中IP数：{}条".format(
                    datetime.now(), count, ed - st, IP_NUM_B - IP_NUM_A,
                    IP_NUM_B))
            st = time.time()
            while time.time() - st < sleep_time:
                logging.info(u"{}\t休眠等待：{:.2f}秒".format(
                    datetime.now(), sleep_time - time.time() + st))
                time.sleep(5)

    def run(self):
        self.multiple_crawl()


class Validation(object):
    '''校验IP有效性'''

    def __init__(self, database_name, valid_ip_table_name, all_ip_table_name):
        self.__URL = "http://httpbin.org/get"
        self.__VALID_IP_TABLE_NAME = valid_ip_table_name
        self.__ALL_IP_TABLE_NAME = all_ip_table_name
        self.__DATABASE_NAME = database_name

    def __check_ip_anonumous(self, ip):
        '''检验IP是否高匿名'''
        logging.info(u"校验IP是否高匿：{}".format(ip[0]))
        if "高匿" in str(ip):
            return True
        else:
            logging.debug("非高匿IP：{}".format(ip[0]))
            return False

    def __check_ip_validation(self, ip):
        '''校验IP地址有效性'''
        try:
            IP = str(ip[0]) + ":" + str(ip[1])
        except Exception:
            logging.info(u"IP地址格式不正确!")
            return None
        re_conn_time = 2
        cnt = 0
        while cnt < re_conn_time:
            cnt += 1
            try:
                logging.info(u"校验IP地址有效性：{}".format(IP))
                proxies = {"http": "http://" + IP}
                response = requests.get(
                    url=self.__URL,
                    headers=FakeUserAgent().get_random_headers(),
                    proxies=proxies,
                    timeout=5)
            except Exception:
                time.sleep(2 * random.random())
                response = None
        if response is None:
            logging.info(u"网络错误！")
            return
        if int(response.status_code) == 200 and IP.split(
                ":")[0] in response.text:
            logging.info(u"有效IP：{}".format(IP))
            return True
        else:
            logging.debug("无效IP：{}".format(IP))
            return False

    def __filter_ip(self, ip):
        '''验证数据库中的IP地址是否有效,校验后删除'''
        if self.__check_ip_validation(ip) and self.__check_ip_anonumous(ip):
            IP_Pool(self.__DATABASE_NAME,
                    self.__VALID_IP_TABLE_NAME).push([ip])
        IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).delete(ip)

    def multiple_filter(self, thread_num=50, sleep=15 * 60):
        '''多线程验证'''
        IPs = IP_Pool(self.__DATABASE_NAME, self.__ALL_IP_TABLE_NAME).pull()
        count = 0
        while True:
            count += 1
            st = time.time()
            logging.info(u"{}\t 第{}轮验证开始，共计需验证IP:{} 条".format(
                datetime.now(), count, len(IPs)))
            cnt = 0
            while cnt < len(IPs):
                pool = []
                for i in range(thread_num):
                    if cnt >= len(IPs):
                        break
                    logging.info(u"当前校验进度：{}/{}\t{:.2f}%".format(
                        cnt, len(IPs), cnt / len(IPs) * 100))
                    th = threading.Thread(
                        target=self.__filter_ip, args=(IPs[cnt], ))
                    th.start()
                    time.sleep(random.random())
                    pool.append(th)
                    cnt += 1
                for th in pool:
                    th.join()
            ed = time.time()
            IP = IP_Pool(self.__DATABASE_NAME,
                         self.__VALID_IP_TABLE_NAME).pull()
            logging.info(
                "{}\t 第{}轮验证结束，耗时：{:.2f}\t共计验证IP:{}条\t当前IP池中有效IP:{}条".format(
                    datetime.now(), count, ed - st, len(IPs), len(IP)))
            st = time.time()
            while time.time() - st < sleep:
                logging.info(u"休眠倒计时：{:.2f}秒".format(sleep - time.time() + st))
                time.sleep(5)

    def __validation(self, ip):
        '''校验有效IP池中的IP有效性，无效则删除'''
        if not self.__check_ip_validation(ip):
            IP_Pool(self.__DATABASE_NAME,
                    self.__VALID_IP_TABLE_NAME).delete(ip)

    def multiple_validation(self, thread_num=20, sleep=15 * 60):
        '''定时校验有效IP池里的IP，无效的删除'''
        IPs = IP_Pool(self.__DATABASE_NAME, self.__VALID_IP_TABLE_NAME).pull()
        count = 0
        while True:
            count += 1
            logging.info(u"{}\t 第{} 次校验，当前IP数：{}".format(
                datetime.now(), count, len(IPs)))
            cnt = 0
            while cnt < len(IPs):
                pool = []
                for i in range(thread_num):
                    if cnt >= len(IPs):
                        break
                    logging.info(u"校验进度：{}/{}\t{:.2f}%".format(
                        cnt, len(IPs), cnt / len(IPs) * 100))
                    th = threading.Thread(
                        target=self.__validation, args=(IPs[cnt], ))
                    th.start()
                    time.sleep(random.random())
                    pool.append(th)
                    cnt += 1
                for th in pool:
                    th.join()
            ips = IP_Pool(self.__DATABASE_NAME,
                          self.__VALID_IP_TABLE_NAME).pull()
            logging.info(u"{}\t 完成第{}次校验，当前有效IP数：{}".format(
                datetime.now(), count, len(ips)))
            logging.info(u"进入休眠：{} 秒".format(sleep))
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
    database_name = "ProxyIP.db"
    valid_ip_table_name = "ip_table"
    all_ip_table_name = "all_ip_table"
    p1 = Process(
        target=Crawl(database_name, valid_ip_table_name, all_ip_table_name)
        .run)
    p2 = Process(
        target=Validation(database_name, valid_ip_table_name,
                          all_ip_table_name).run)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == "__main__":
    main()
