# -*- coding: utf-8 -*-

# @Author: yooongchun
# @File: config.py
# @Time: 2018/6/19
# @Contact: yooongchun@foxmail.com
# @blog: https://blog.csdn.net/zyc121561
# @Description: 配置打印信息级别及位置

import logging.handlers


class CONFIG(object):
    '''控制信息打印级别和位置'''

    def __init__(self, to_file=False, level="info", file_path="blogger.log"):
        if level == "FATAL":
            logging_level = logging.FATAL
        elif level == "ERROR":
            logging_level = logging.ERROR
        elif level == "WARNNING":
            logging_level = logging.WARNING
        elif level == "INFO":
            logging_level = logging.INFO
        elif level == "DEBUD":
            logging_level = logging.DEBUG
        elif level == "NOTSET":
            logging_level = logging.NOTSET
        else:
            logging_level = logging.INFO
        if to_file:
            handler = logging.handlers.RotatingFileHandler(
                file_path, mode="w", encoding='utf-8')
            logging.basicConfig(level=logging_level, handlers=[handler])
        else:
            logging.basicConfig(level=logging_level)


def config():
    '''在此处设置打印配置信息'''
    CONFIG(to_file=True, level="ERROR", file_path="blogger.log")
