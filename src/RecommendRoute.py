#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

'''
Created on Oct 13, 2014

@author: tusion
'''

import redis
import ConfigParser

#**************************************************************************
#连接数据库，参数通过外部配置文件取得
def initRedis():
    file_name = "../data/Configure.ini"    
    config = ConfigParser.ConfigParser()
    config.read( file_name )
    section = "redis"

    redis_host      = config.get( section, "redis_host") 
    redis_port      = config.get( section, "redis_port") 
    redis_db         = config.get( section, "redis_db") 

    #connect database
    r = redis.StrictRedis( host =  redis_host,  
                                     port  = redis_port,
                                    db     = redis_db)

    return r



#****************************************************************************
def testRedis():
    r = initRedis()
    r.set('name', 'tusion')
    print r.get('name')
    print r.keys()
    r.delete('name')
    print r.keys()
