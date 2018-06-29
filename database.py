# -*- coding: utf-8 -*-

# @Author: yooongchun
# @File: database.py
# @Time: 2018/6/19
# @Contact: yooongchun@foxmail.com
# @blog: https://blog.csdn.net/zyc121561
# @Description: 数据库

import sqlite3
import logging
import config
config.config()


class IP_Pool(object):
    """
    存取IP的数据库
    """

    def __init__(self, database_name, table_name):
        self.__table_name = table_name
        self.__database_name = database_name

    def push(self, IP_list):
        '''存储IP，传入一个列表，格式为[[IP,PORT,ADDRESS,TYPE,PROTOCOL],...]'''
        logging.info(u"写入数据库表：%s..." % (self.__table_name))
        try:
            conn = sqlite3.connect(self.__database_name, isolation_level=None)
            conn.execute(
                "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER,ADDRESS CHAR(50),TYPE CHAR(50),PROTOCOL CHAR(50))"
                % self.__table_name)
        except Exception:
            logging.error("连接数据库出错,退出：{}".format(self.__database_name))
            return
        for one in IP_list:
            if len(one) < 5:
                logging.error("IP格式不正确：{}，跳过！".format(one))
                continue
            conn.execute(
                "insert or ignore into %s(IP,PORT,ADDRESS,TYPE,PROTOCOL) values (?,?,?,?,?)"
                % (self.__table_name),
                (one[0], one[1], one[2], one[3], one[4]))
        conn.commit()
        conn.close()

    def pull(self, random_flag=False):
        '''获取IP，返回一个列表'''
        try:
            conn = sqlite3.connect(self.__database_name, isolation_level=None)
            conn.execute(
                "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER,ADDRESS CHAR(50),TYPE CHAR(50),PROTOCOL CHAR(50))"
                % self.__table_name)
        except Exception:
            logging.error("连接数据库出错：{}".format(self.__database_name))
            return
        cur = conn.cursor()
        if random_flag:
            cur.execute("select * from %s order by random() limit 1" %
                        self.__table_name)
            response = cur.fetchone()
        else:
            cur.execute("select * from %s" % self.__table_name)
            response = cur.fetchall()
        cur.close()
        conn.close()
        return response

    def delete(self, IP=None):
        '''删除指定的记录'''
        try:
            conn = sqlite3.connect(self.__database_name, isolation_level=None)
            conn.execute(
                "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER,ADDRESS CHAR(50),TYPE CHAR(50),PROTOCOL CHAR(50))"
                % self.__table_name)
        except Exception:
            logging.error("连接数据库出错：{}".format(self.__database_name))
            return
        cur = conn.cursor()
        if IP is not None:
            logging.info(u"删除记录：{}\t{}".format(self.__table_name, IP[0]))
            cur.execute("delete from %s where IP=?" % self.__table_name,
                        (IP[0], ))
        else:
            logging.info(u"删除所有记录:{}".format(self.__table_name))
            cur.execute("delete from %s" % self.__table_name)
        cur.close()
        conn.close()


class INFO_Pool(object):
    """
    存取博客文章统计数据的数据库
    """

    def __init__(self, database_name, table_name):
        self.__table_name = table_name
        self.__database_name = database_name

    def push(self, info):
        '''存储统计信息，传入一个列表，格式为[[TIME,TISTAMP,ARTICLE_NUM,TOTAL_VISIT],...]'''
        logging.info(u"写入数据库表：%s..." % (self.__table_name))
        try:
            conn = sqlite3.connect(self.__database_name, isolation_level=None)
            conn.execute(
                "create table if not exists %s(TIME CHAR(50) UNIQUE,TIMESTAMP INTEGER,ARTICLE_NUM INTEGER,TOTAL_VISIT INTEGER)"
                % self.__table_name)
        except Exception:
            logging.error("连接数据库出错,退出：{}".format(self.__table_name))
            return
        for one in info:
            conn.execute(
                "insert or ignore into %s(TIME,TIMESTAMP,ARTICLE_NUM,TOTAL_VISIT) values (?,?,?,?)"
                % (self.__table_name), (one[0], one[1], one[2], one[3]))
        conn.commit()
        conn.close()

    def pull(self):
        '''获取数据库内容，返回一个列表'''
        try:
            conn = sqlite3.connect(self.__database_name, isolation_level=None)
            conn.execute(
                "create table if not exists %s(TIME CHAR(50) UNIQUE,TIMESTAMP INTEGER,ARTICLE_NUM INTEGER,TOTAL_VISIT INTEGER)"
                % self.__table_name)
        except Exception:
            logging.error("连接数据库出错：{}".format(self.__table_name))
            return
        cur = conn.cursor()
        cur.execute("select * from %s" % self.__table_name)
        response = cur.fetchall()
        cur.close()
        conn.close()
        return response

    def delete(self, TIME=None):
        '''删除指定的记录'''
        try:
            conn = sqlite3.connect(self.__database_name, isolation_level=None)
            conn.execute(
                "create table if not exists %s(TIME CHAR(50) UNIQUE,TIMESTAMP INTEGER,ARTICLE_NUM INTEGER,TOTAL_VISIT INTEGER)"
                % self.__table_name)
        except Exception:
            logging.error("连接数据库出错：{}".format(self.__table_name))
            return
        cur = conn.cursor()
        if TIME is not None:
            logging.info(u"删除记录：{}-{}".format(self.__table_name, TIME))
            cur.execute("delete from %s where TIME=?" % self.__table_name,
                        (TIME, ))
        else:
            logging.info(u"删除所有记录:{}".format(self.__table_name))
            cur.execute("delete from %s" % self.__table_name)
        cur.close()
        conn.close()


if __name__ == "__main__":
    # pool = IP_Pool("ProxyIP.db", "all_ip_table")
    # pool.push([['127.0.0.1', '8080', '中国广州', '高匿名',
    #             'HTTPS'], ['126.1.1.23', '999', '宁夏回族自治州', '透明', 'SOCKS4'],
    #            ['129.1.1.23', '999', '哈萨克斯', '透明',
    #             'SOCKS4'], ['128.1.1.23', '999', '宁夏回族自治州', '透明', 'SOCKS4'],
    #            ['129.1.1.23', '999', '宁夏回族自治州', '透明', 'SOCKS4']])

    # for index, ip in enumerate(pool.pull(random_flag=False)):
    #     logging.info("{}:{}".format(index, ip))

    pool = IP_Pool("ProxyIP.db", "ip_table")
    for ip in pool.pull():
        logging.info(ip)

    pool = INFO_Pool("../INFO.db", "info_table")
    # info = [['2018-06-28 12:40:30.234543', 987623453, 888,
    #          10200], ['2018-06-28 12:40:30.234543', 987623453, 999, 10200],
    #         ['2018-06-28 12:40:32.234543', 987623453, 888,
    #          10200], ['2018-06-27 12:40:30.234543', 987623453, 888, 10200],
    #         ['2018-06-28 12:40:34.234543', 987623454, 888, 10200]]
    # pool.push(info)
    # pool.delete('2018-06-28 12:40:32.234543')
    for ip in pool.pull():
        logging.info(ip)