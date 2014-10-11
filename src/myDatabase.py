#!/usr/bin/python
# encoding: utf-8

import MySQLdb
import time

#***************************************************************
#complete insert a row in database.
def executeDB( cursor, sql ):
    try:
        cursor.execute( sql )
    except MySQLdb.Error,e:
        print e



#***************************************************************
#新建路线表，将所有需要处理的路线存储
def createRecommendRouteTable( cursor ):
	sql ="DROP TABLE IF EXISTS recommend_route_tb"
	executeDB( cursor, sql)
	
	sql = '''  create table if not exists recommend_route_tb(\
                    		   id                            int unsigned not null auto_increment primary key,
                    		    creater_uid				bigint(20) unsigned not null comment '路线创建者ID',
                    		    route_id				bigint(20) unsigned not null comment '路线唯一标示，对应到youche_route的id列',
                    		    route_type                enum('find_driver', 'find_passenger') not null,
                    		    start_longtitude        decimal(13,10) not null,
                    		    start_latitude         decimal(13,10) not null,
                    		    start_simple_lng        decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
                    		    start_simple_lat        decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
                    		    start_address           varchar(200) not null comment '精确经纬度对应的地址',
                    		    start_area_id           bigint(20) unsigned not null comment '粗化经纬度后，起点对应的方块编号',
                        		end_longtitude          decimal(13,10) not null,
                        		end_latitude            decimal(13,10) not null,
                        		end_simple_lng          decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
                        		end_simple_lat          decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
                        		end_address             varchar(200) not null comment '精确经纬度对应的地址',
                        		end_area_id             bigint(20) unsigned not null comment '粗化经纬度后，终点对应的方块编号',
                        		recommend_route_id      varchar(200) comment '推荐的同路路线id,以逗号分隔',
                        		update_time             timestamp not null
	                    )
                '''
	executeDB( cursor, sql )

#***************************************************************
#向表中添加一条新的路线
def insertRouteToTable( cursor, route):
    sql = " INSERT INTO recommend_route_tb ( creater_uid, route_id, route_type, \
    start_longtitude,  start_latitude,  start_simple_lng,  start_simple_lat,  start_address, start_area_id,\
    end_longtitude,  end_latitude,  end_simple_lng, end_simple_lat,  end_address,  end_area_id,update_time)\
    VALUES( '%d', '%d','%s',  '%f','%f','%f','%f','%s','%d',  '%f','%f','%f','%f',' %s', '%d', now()  )"%\
    ( route['creater_uid'], route['route_id'], route['type'],\
    route['start_longtitude'], route['start_latitude'], route['start_simple_lng'], route['start_simple_lat'], route['start_address'], 0,\
    route['end_longtitude'],  route['end_latitude'],  route['end_simple_lng'], route['end_simple_lat'],  route['end_address'],0,)
    
    #print sql
    executeDB(cursor, sql)
                    
        
#***************************************************************
#存储所有点对应的方块
def createPointAreaTable(cursor):
	sql ="DROP TABLE IF EXISTS point_area_tb"
	executeDB( cursor, sql )
	
	sql = '''create table if not exists point_area_tb(
                    id            bigint(20) unsigned not null auto_increment primary key comment '粗化经纬度后，起点对应的方块编号',
                    simple_lng      decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
                    simple_lat      decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
                    address         varchar(200)  comment '精确经纬度对应的地址',
                    address_hash    char(32) comment'对地址做hash',
                    point_num       int unsigned not null default 0 comment '落在这个方块内的点的总数',
                    route_id        text comment '起点或终点在这个方块内的路线id,以逗号分隔',
                    update_time     timestamp not null
		)
	'''

	executeDB( cursor, sql )
    
#***************************************************************
#存储所有点对应的方块
def inserPointToAreaTable( cursor, route):
    simple_start_lng = route['start_simple_lng']
    simple_start_lat = route['start_simple_lat']
    
    query_sql = "SELECT * FROM point_area_tb WHERE simple_lng=%f AND simple_lat=%f "%(simple_start_lat, simple_start_lng)
    count = cursor.execute( query_sql)
    if( count == 0 ):   
       #这个方块不在数据库中
        print "this record is not in table"
        insert_sql = "INSERT INTO point_area_tb( id, simple_lng, simple_lat, address, \
                            address_hash,point_num,route_id, update_time)\
                            VALUES(NULL, %f, %f, NULL, NULL, 1,  %s, now() ) " %\
                            ( route['start_simple_lng'],  route['start_simple_lat'],  str( route['route_id']) )
        executeDB(cursor, insert_sql)
    elif( count == 1 ): 
        #这个方块已经在数据库中
        print "this record is already in table"
        result = cursor.fetchone()
        route['area_id'] = result[0]
        #nead to update database!!!!!!!!!!!!!!!!!!!!!!!!!!
        print 'id=',route['area_id']
        time.sleep(1)
    else:
        #这个方块在数据库中有多条记录
        print "Error, this record has %d copy"%count
        