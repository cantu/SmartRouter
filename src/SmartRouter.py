#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

import ConfigParser
import MySQLdb
import sys
import time

#import other python files
import aMap
import RouteInfo

#reload(sys)
#sys.setdefaultencoding('utf-8')


#**************************************************************************
def simpleLocation( longtitude, latitude ):

    #http://www.storyday.com/wp-content/uploads/2008/09/latlung_dis.html
    #经度(Longtitude)的小数点第三位(0.001度)大概距离是86M
    #纬度(Latitude)     的小数点第三位(0.001度)大概距离是111M
    #对第三位做简化处理，第三位要么是０，要么是５
    #step: *2 -> 取小数点后两位 -> /2 -> 取小数点后三位  
    simple_lng = float("%.3f"%(float("%.2f"%(longtitude*2))/2)) #86/(10/2)=430m
    simple_lat = float("%.3f"%(float("%.2f"%(latitude  *2))/2))     #111*(10/2)=555m
    
    #check 
    lng_last = int(simple_lng* 1000 %10)
    lat_last  = int(simple_lat*1000%10 )
    if (lng_last!=0 and lng_last!=5 and lat_last!=0 and lat_last!=5  ):
        print 'simple location process error!'
        exit(0)
    return (simple_lng, simple_lat )

#*******************************************************************************
# main function

cursor = RouteInfo.initDatabase()

RouteInfo.createRecommendRouteTable(cursor)
RouteInfo.createPointAreaTable( cursor )


#对应到youche_route数据表中的id列
#route_id = 2178
#---------- go through all route in database -----------------------
try:
    count = cursor.execute("SELECT id from youche_route ORDER BY id")
    print 'database return %d line'%(count)
    result = cursor.fetchall()
except Exception, e:
    print e

if result:
    for item in result:
        print '-'*30 + ' Total:' + str(count) +'  id:' + str(item[0]) + ' '+ '-'*30
        route_id = item[0]
        route = RouteInfo.getRoute( cursor, route_id) 
        
        ( route['start_simple_lng'], route['start_simple_lat']) = simpleLocation(\
        																							route['start_longtitude'], route['start_latitude'] )
        ( route['end_simple_lng'], route['end_simple_lat']) = simpleLocation(\
        																							route['end_longtitude'], route['end_latitude'])
        
        route['start_address']  =  aMap.regeoDecode( route['start_longtitude'], route['start_latitude'] )
        route['end_address'] = aMap.regeoDecode( route['end_longtitude'],  route['end_latitude'])
     

        RouteInfo.inserPointToAreaTable(cursor, route )
        
        RouteInfo.insertRouteToTable(cursor, route)
        
        RouteInfo.printRoute( route )
    
        #SELECT * FROM `point_area_tb` WHERE 1 order by point_num  DESC limit 10
        
    #time.sleep(1)

print 'finish'






















