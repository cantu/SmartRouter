#!/usr/bin/python
# encoding: utf-8

import MySQLdb
import ConfigParser
import time
import aMap

#**************************************************************************
#连接数据库，参数通过外部配置文件取得
def initDatabase():
    file_name = "../data/Configure.ini"    
    config = ConfigParser.ConfigParser()
    config.read( file_name )
    
    #sections = config.sections()
    #print 'get sections: ', sections

    #db_options = config.options("database")
    #print "database options: ", db_options
    
    section = "database"
    db_name         = config.get( section, "db_name")
    db_table     = config.get( section, "db_table")
    db_host      = config.get( section, "db_host") 
    db_user      = config.get( section, "db_user")
    db_password  = config.get( section, "db_password")
    #connect database
    try:
        db_route = MySQLdb.connect( 
                    host = db_host,
                    user = db_user,
                    passwd = db_password,
                    db = db_name,
                    charset = 'utf8')
        db_route.autocommit( True )
    except Exception, e:
        print e

    cursor = db_route.cursor()

    return cursor

#***************************************************************
#complete insert a row in database.
def executeDB( cursor, sql ):
    try:
        cursor.execute( sql )
    except MySQLdb.Error,e:
        print e


#**************************************************************************
#获取路线部分信息，缺少经纬度信息
def getRouteInfo( cursor, route_id ):

    table = "youche_route"
    sql = "SELECT * FROM %s WHERE id=%d"%(table,route_id);
    try:
        count = cursor.execute( sql )
        
        result = cursor.fetchone()
        if result:
            route = dict()
            route['route_id']         = result[0]    #每条线路的唯一标示符
            route['creater_uid']    = result[1]
            #route['start_name']     = result[5]    #根据起点坐标，客服端查询到的地址，可能不太准确，可以自己再查询一次
            route['start_id']        = result[4]    #每一个坐标点对应一个id，通过这个id与数据表youche_location联系
            #route['end_name']         = result[8]
            route['end_id']         = result[7]
            route['type']             = result[20] #路线分为找司机或者找乘客两种类型
    except MySQLdb.Error, e:
        print e

    return route

#**************************************************************************
#获取路线的经纬度信息
def getLocation( cursor, point_id ):
    table = "youche_location"
    sql = "SELECT * FROM %s WHERE id=%d"%(table, point_id)
    try:
        count = cursor.execute( sql )
        result = cursor.fetchone()
        if result:
            #print result
            point_location = dict()
            point_location['longtitude'] = float(result[2])
            point_location['latitude'] = float(result[3])
    except MySQLdb.Error, e:
        print e
    
    return point_location



#**************************************************************************
#获取路线完整信息
def getRoute( cursor, route_id ):

    route = getRouteInfo( cursor, route_id )
    start_location = getLocation( cursor, route['start_id'] )
    end_location = getLocation( cursor, route['end_id'] )
    route['start_longtitude'] = start_location['longtitude']
    route['start_latitude']   = start_location['latitude']
    route['end_longtitude']   = end_location['longtitude']
    route['end_latitude']     = end_location['latitude']

    #print str( route )
    
    return route

#**************************************************************************
def printRoute( route ):
    if( len(route) > 0):
        for item in route:
            print "route[%20s]: %s"%( item, route[item] )

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
    route['start_longtitude'], route['start_latitude'], route['start_simple_lng'], route['start_simple_lat'], route['start_address'], route['start_area_id'],\
    route['end_longtitude'],  route['end_latitude'],  route['end_simple_lng'], route['end_simple_lat'],  route['end_address'],route['end_area_id'])
    
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
                    all_route_id        text comment '起点或终点在这个方块内的路线id,以逗号分隔',
                    update_time     timestamp not null
		)
	'''

	executeDB( cursor, sql )
    
#***************************************************************
#存储所有点对应的方块
def inserPointToAreaTable( cursor, route):
        
    #添加起点
    query_sql = "SELECT * FROM point_area_tb WHERE simple_lng=%f AND simple_lat=%f "%\
                        (route['start_simple_lng'],  route['start_simple_lat'])
    count = cursor.execute( query_sql)
    #print query_sql
    #print count
    if( count == 0 ):   
       #这个方块不在数据库中
        print "insert new point to area table"
        start_address = aMap.regeoDecode( route['start_simple_lng'], route['start_simple_lat'])
        insert_sql = "INSERT INTO point_area_tb( id, simple_lng, simple_lat, address, \
                            address_hash,point_num,all_route_id, update_time)\
                            VALUES(NULL, %f, %f, '%s', NULL, 1,  '%s', now() ) " %\
                            ( route['start_simple_lng'],  route['start_simple_lat'],  start_address, str( route['route_id']) )
        executeDB(cursor, insert_sql)
        
        route['start_area_id'] = 0
        '''
        #查询新插入进去的点的编号
        query_sql = "SELECT id FROM point_area_tb WHERE simple_lng=%f AND simple_lat=%f "%\
                        (route['start_simple_lng'],  route['start_simple_lat'])
        count = cursor.execute( query_sql)
        if( count ==1 ):
            result = cursor.fetchone()
            route['start_area_id'] = result[0]
        else:
            print 'Insert point into table, but query the new line error!'
            exit(0)
         '''   
    elif( count == 1 ): 
        #这个方块已经在数据库中
        result = cursor.fetchone()
        print "this record is already in table, id=%d"%result[0]
        point_num = int(result[5])+ 1
        route_id_str = result[6] + ', ' + str(route['route_id'])
        route['start_area_id'] = result[0]
        update_sql = "UPDATE point_area_tb SET point_num=%d, all_route_id='%s' WHERE id = %d"%\
                                (point_num, route_id_str, route['start_area_id'])
        executeDB(cursor, update_sql)
        #print update_sql
        #nead to update database!!!!!!!!!!!!!!!!!!!!!!!!!!
        #time.sleep(1)
    else:
        #这个方块在数据库中有多条记录
        print "Error, this record has %d copy"%count
        exit(0)
        
    #添加终点
    query_sql = "SELECT * FROM point_area_tb WHERE simple_lng=%f AND simple_lat=%f "%\
                        (route['end_simple_lng'],  route['end_simple_lat'])
    count = cursor.execute( query_sql)
    #print query_sql
    #print count
    if( count == 0 ):   
       #这个方块不在数据库中
        print "this record is not in table"
        end_address = aMap.regeoDecode( route['start_simple_lng'], route['start_simple_lat'])
        insert_sql = "INSERT INTO point_area_tb( id, simple_lng, simple_lat, address, \
                            address_hash,point_num,all_route_id, update_time)\
                            VALUES(NULL, %f, %f, '%s', NULL, 1,  '%s', now() ) " %\
                            ( route['end_simple_lng'],  route['end_simple_lat'],  end_address, str( route['route_id']) )
        executeDB(cursor, insert_sql)
        
        route['end_area_id'] = 0
        '''
        #查询新插入进去的点的编号
        query_sql = "SELECT id FROM point_area_tb WHERE simple_lng=%f AND simple_lat=%f "%\
                        (route['end_simple_lng'],  route['end_simple_lat'])
        count = cursor.execute( query_sql)
        if( count ==1 ):
            result = cursor.fetchone()
            route['end_area_id'] = result[0]
        else:
            print 'Insert point into table, but query the new line error!'
            exit(0)
        '''
    elif( count == 1 ): 
        #这个方块已经在数据库中
        result = cursor.fetchone()
        print "this record is already in table, id=%d"%result[0]
        point_num = int(result[5])+ 1
        route_id_str = result[6] + ', ' + str(route['route_id'])
        route['end_area_id'] = result[0]
        update_sql = "UPDATE point_area_tb set point_num=%d, all_route_id='%s' WHERE id = %d"%\
                                (point_num, route_id_str, route['end_area_id'])
        executeDB(cursor, update_sql)
       # print update_sql
        #nead to update database!!!!!!!!!!!!!!!!!!!!!!!!!!
        #time.sleep(1)
    else:
        #这个方块在数据库中有多条记录
        print "Error, this record has %d copy"%count
        exit(0)
        
    return route
        