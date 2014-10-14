#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

import ConfigParser
import MySQLdb
import sys
import time
import datetime

#import other python files
import aMap
import RouteInfo

#reload(sys)
#sys.setdefaultencoding('utf-8')


#***********************************************************************************
#main function

#1
#initialRouteDatabase()

#2
#RouteInfo.updateAddressInRouteTable()
#RouteInfo.updateAddressInPointAreaTable()
#RouteInfo.updateAreaIdInRouteTable()



#3
#新建驾车路径的数据库
#RouteInfo.createDriveRouteTable()
#计算所有路线自己的路线
start_time = datetime.datetime.now()
RouteInfo.queryPathOneself()
end_time = datetime.datetime.now()
elapsed = (end_time -  start_time ).seconds
print( ' query one point all drive route total used time: ', elapsed)

#实验用司机路线　route_id=2178,  
#中关村街道恒兴大厦(东门)                start_simple( 116.335, 39.985),     area_id =1
#通州区梨园地区新华联家园(南区)        end_simple( 116.645, 39.890),     area_id=326

#实验路线的起点到其它所有点的规划
area_id = 1
start_time = time.clock( )
RouteInfo.queryPathOneToOthers( area_id )
print ''
print  '*'*80
elapsed = (time.clock() - start_time )
print( ' query one point all drive route total used time: ', elapsed)

    

#实验路线的终点到其它所有点的驾车路线规划
area_id = 326
start_time = datetime.datetime.now()
RouteInfo.queryPathOneToOthers( area_id )
print ''
print  '*'*80
end_time = datetime.datetime.now()
elapsed = (end_time -  start_time ).seconds
print( ' query one point all drive route total used time: ', elapsed)


















