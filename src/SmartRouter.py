#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

from  __future__ import division
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

def setupData():
    #1
    RouteInfo.initialRouteDatabase()
    
    #2
    RouteInfo.updateAddressInRouteTable()
    RouteInfo.updateAddressInPointAreaTable()
    RouteInfo.updateAreaIdInRouteTable()
    
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
    

#*******************************************
def getRouteMatchScore(car, passenger):

    cursor = RouteInfo.initDatabase()
    
    #车主起点到车主终点行车路径规划距离D0
    distance_0 = RouteInfo.queryDistanceFromDriveTable( car['start_simple_lng'], car['start_simple_lat'],
                                                                    car['end_simple_lng'], car['end_simple_lat'])
    #车主起点到乘客起点行车路径规划距离D1
    distance_1 = RouteInfo.queryDistanceFromDriveTable( car['start_simple_lng'], car['start_simple_lat'],
                                                                    passenger['start_simple_lng'], passenger['start_simple_lat'])
    #乘客起点到乘客终点行车路径规划距离Ｄ2
    distance_2 = RouteInfo.queryDistanceFromDriveTable( passenger['start_simple_lng'], passenger['start_simple_lat'],
                                                                    passenger['end_simple_lng'], passenger['end_simple_lat'])
    #乘客终点到司机终点行车路径规划距离Ｄ3
    distance_3 = RouteInfo.queryDistanceFromDriveTable( passenger['end_simple_lng'], passenger['end_simple_lat'],
                                                                    car['end_simple_lng'], car['end_simple_lat'])
    
    #计算车主绕行距离： d = (D1+D2+D3) - D0
    car_extra_distance = (distance_1 + distance_2 +distance_3) - distance_0
    #计算车主绕行因子：  r1 = d / D0,     ( 0< r1 < 1 )  越小越好
    car_extra_factor= car_extra_distance / distance_0 
    #计算车主收益因子：  r2 = D2 / D0，(0< r2 )  越大越好
    car_earn_factor= distance_2 /distance_0
    
    car_extra_plus = 1.5
    if( car_earn_factor< 0.1 ):
        match_factor = 0
    elif(car_extra_factor==0 and  car_earn_factor == 0 ):
        match_factor = 0
    else:
        match_factor = car_earn_factor - car_extra_plus*car_extra_factor
        
    #print "getRouteMatchScore, d0=%d, d1=%d, d2=%d, d3=%d"%(distance_0, distance_1, distance_2, distance_3)
    # print "车主绕行距离=%d,  车主绕行因子=%f,  车主收益因子=%f"%( car_extra_distance, car_extra_factor, car_earn_factor)   
    return (match_factor, car_extra_distance, car_extra_factor, car_earn_factor)     

#****************************************************************************************
def findMatchRoute(test_car_route_id ):
    #test_car_route_id = 2178
    table_name = 'recommend_'+ str(test_car_route_id) +'_tb'
    start_time = datetime.datetime.now()
    #go through all route in database 
    cursor = RouteInfo.initDatabase()
    
    #新建这条路线的匹配表
    RouteInfo.createRecommendFactorTable(cursor, table_name)
    
    #车主信息
    car = dict()
    try:
        get_car_sql =  "SELECT * from recommend_route_tb where route_id=%d "%test_car_route_id 
        print get_car_sql
        count = cursor.execute( get_car_sql)
        print 'database return %d line'%(count)
        result = cursor.fetchone()
    except Exception, e:
        print e
        
    if(result):
        car['id']= result[0]
        car['route_id'] = result[2]
        car['start_simple_lng'] = result[6]
        car['start_simple_lat'] =  result[7]
        car['start_area_id'] = result[9]
        car['end_simple_lng'] = result[12]
        car['end_simple_lat'] = result[13]
        car['end_area_id'] =result[15]
    else:
        print('error, can not get car info')    
            
    # scan all other route to find match route        
    try:
        count = cursor.execute("SELECT * from recommend_route_tb ORDER BY id")
        print 'database return %d line'%(count)
        result = cursor.fetchall()
    except Exception, e:
        print e
    
    if result:
        i = 0; #passenger index
        car_extra_distance =[]
        car_extra_factor=[]
        car_earn_factor=[]
        car_match_factor =[]
        for item in result:
            passenger = dict()
            now = datetime.datetime.now()
            cost_time = (now - start_time).seconds
            print '-'*10+ '[Smart Route]  '+ ' Total:' + str(count) +'  id:' + str(item[0]) + ',  cost time:  ' +str(cost_time) + '-'*30
            passenger['id']= item[0]
            passenger['route_id'] = item[2]
            passenger['start_simple_lng'] = item[6]
            passenger['start_simple_lat'] =  item[7]
            passenger['start_area_id'] = item[9]
            passenger['end_simple_lng'] = item[12]
            passenger['end_simple_lat'] = item[13]
            passenger['end_area_id'] =item[15]
            
            print "car_route_id=%d,  passenger_route_id=%d"%(car['route_id'], passenger['route_id'])
            
            #car route self
            if ( passenger['route_id'] == test_car_route_id ):
                continue
            
            (match_factor, distance, extra_factor, earn_factor) = getRouteMatchScore(car, passenger)
            car_extra_distance.append(distance)
            car_extra_factor.append(earn_factor)
            car_earn_factor.append(earn_factor)
            car_match_factor.append(match_factor)
            #print "车主绕行距离=%d,  车主绕行因子=%f,  车主收益因子=%f"%( car_extra_distance[i], car_extra_factor[i], car_earn_factor[i])   
            i +=1
            
            insert_sql = "INSERT INTO %s( id, car_route_id, passenger_route_id, match_factor, \
                                car_extra_distance,car_extra_factor, car_earn_factor,  update_time)\
                                VALUES(NULL, '%d', '%d', '%.3f', '%d',  '%.3f', '%.3f',  now() ) " %\
                                ( table_name, car['route_id'], passenger['route_id'], match_factor, distance, extra_factor, earn_factor )
            #print insert_sql
            cursor.execute( insert_sql );
    
    print 'finish '
    cursor.close()
    
#***********************************************************************************
#main function    


#实验用司机路线　route_id=2178,  
#中关村街道恒兴大厦(东门)                start_simple( 116.335, 39.985),     area_id =1
#通州区梨园地区新华联家园(南区)        end_simple( 116.645, 39.890),     area_id=326
example_car_route_list=[2178, 20, 814, 928, 3690, 1090, 1591, 2531, 788, 1377, 1490]

#findMatchRoute(1377)


for route_id in example_car_route_list:
    #findMatchRoute(route_id)
    RouteInfo.updateRecommendRouteInRouteTable( route_id)

#SELECT * FROM youche_info.recommend_2178_tb order by car_extra_factor limit 30;
#SELECT * FROM `recommend_route_tb` WHERE start_address LIKE '%大兴%'
#SELECT * FROM youche_info.recommend_20_tb where car_extra_factor <0.1 order by car_earn_factor desc limit 30;
#SELECT * FROM youche_info.recommend_2178_tb order by match_factor desc limit 100;
#SELECT * FROM youche_info.recommend_route_tb where recommend_route_id IS NULL limit 100;
    
    
    


    













