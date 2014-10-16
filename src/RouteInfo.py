#!/usr/bin/python
# encoding: utf-8

import MySQLdb
import ConfigParser
import aMap
import datetime

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
#*****************************************************************************
def initialRouteDatabase():
    
    cursor = initDatabase()
    
    #删除旧的数据表，新建数据表
    createRecommendRouteTable(cursor)
    createPointAreaTable( cursor )
    
    #go through all route in database 
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
            #build route info
            route = getRoute( cursor, route_id) 
            ( route['start_simple_lng'], route['start_simple_lat']) = aMap.simpleLocation(\
                                                                                                    route['start_longtitude'], route['start_latitude'] )
            ( route['end_simple_lng'], route['end_simple_lat']) = aMap.simpleLocation(\
                                                                                                    route['end_longtitude'], route['end_latitude'])
            route['start_address']=''
            route['end_address']=''
            
            inserPointToAreaTable(cursor, route )
            insertRouteToTable(cursor, route)
            
            printRoute( route )
            
            #SELECT * FROM `point_area_tb` WHERE 1 order by point_num  DESC limit 10
    cursor.close()    
            #time.sleep(1)
#***************************************************************
#新建路线表，将所有需要处理的路线存储
def createRecommendRouteTable( cursor ):
	sql ="DROP TABLE IF EXISTS recommend_route_tb"
	executeDB( cursor, sql)
	
	create_recommend_route_tb_sql = '''  create table if not exists recommend_route_tb(\
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
	executeDB( cursor, create_recommend_route_tb_sql )

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
	
	create_point_area_tb_sql = '''create table if not exists point_area_tb(
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

	executeDB( cursor, create_point_area_tb_sql )
    
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
        #start_address = aMap.regeoDecode( route['start_simple_lng'], route['start_simple_lat'])
        start_address = ''
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
        #end_address = aMap.regeoDecode( route['start_simple_lng'], route['start_simple_lat'])
        end_address = ''
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

#***********************************************************************************
#更新路线列表中起点和终点地址
def updateAreaIdInRouteTable( ):
    #go through all route in database 
    cursor = initDatabase()
    try:
        count = cursor.execute("SELECT * from recommend_route_tb ORDER BY id")
        print 'database return %d line'%(count)
        result = cursor.fetchall()
    except Exception, e:
        print e
    
    if result:
        for item in result:
            print '-'*10+ 'query address in route table:  '+ ' Total:' + str(count) +'  id:' + str(item[0]) + ' '+ '-'*30
            id = item[0]
            start_simple_lng = item[6]
            start_simple_lat = item[7]
            start_area_id = item[9]
            end_simple_lng = item[12]
            end_simle_lat = item[13]
            end_area_id = item[15]
             
            query_sql = "SELECT * FROM point_area_tb WHERE simple_lng=%f AND simple_lat=%f "%\
                                (start_simple_lng, start_simple_lat)
            print query_sql
            count = cursor.execute( query_sql)
            if( count >0 ): 
                result = cursor.fetchone()
                start_area_id = result[0]
                
            query_sql = "SELECT * FROM point_area_tb WHERE simple_lng=%f AND simple_lat=%f "%\
                                (end_simple_lng, end_simle_lat)
            count = cursor.execute( query_sql)
            if( count >0  ): 
                result = cursor.fetchone()
                end_area_id = result[0]
                
            print start_area_id
            print end_area_id
            update_sql = "UPDATE recommend_route_tb SET start_area_id=%d, end_area_id=%d WHERE id = %d"%\
                            (start_area_id, end_area_id, id)
            #print update_sql
            executeDB(cursor, update_sql)
        cursor.close()

#***********************************************************************************
#更新路线列表中起点和终点地址
def updateAddressInRouteTable( ):
    #go through all route in database 
    cursor = initDatabase()
    try:
        count = cursor.execute("SELECT * from recommend_route_tb ORDER BY id")
        print 'database return %d line'%(count)
        result = cursor.fetchall()
    except Exception, e:
        print e
    
    if result:
        for item in result:
            print '-'*10+ 'query address in route table:  '+ ' Total:' + str(count) +'  id:' + str(item[0]) + ' '+ '-'*30
            route_id = item[0]
            start_lng = item[4]
            start_lat = item[5]
            start_address = item[8]
            end_lng = item[10]
            end_lat = item[11]
            end_address = item[14]
            if( len(start_address) < 5):
                start_address = aMap.regeoDecode(start_lng, start_lat)
            if( len(end_address)<5):
                end_address = aMap.regeoDecode( end_lng, end_lat)
            update_sql = "UPDATE recommend_route_tb SET start_address='%s', end_address='%s' WHERE id = %d"%\
                                (start_address, end_address, route_id)
            print update_sql
            executeDB(cursor, update_sql)
    print 'finish update address to route table'
    cursor.close()
    
#***********************************************************************************
#更新点方块列表中各个点的地址
def updateAddressInPointAreaTable( ):
     #go through all route in database 
    cursor = initDatabase()
    try:
        count = cursor.execute("SELECT * from point_area_tb ORDER BY id")
        print 'database return %d line'%(count)
        result = cursor.fetchall()
    except Exception, e:
        print e
    
    if result:
        for item in result:
            print '-'*10+ 'query address in point area table:  '+ ' Total:' + str(count) +'  id:' + str(item[0]) + ' '+ '-'*30
            id = item[0]
            simple_lng = item[1]
            simple_lat = item[2]
            address = item[3]
     
            if( len(address) < 5):
                address = aMap.regeoDecode(simple_lng, simple_lat)
            update_sql = "UPDATE point_area_tb SET address='%s' WHERE id = %d"%\
                                (address, id)
            print update_sql
            executeDB(cursor, update_sql)
    print 'finish update address to route table'
    cursor.close()
    
   
#***************************************************************
#建立方块到方块的路劲规划数据表
def createDriveRouteTable():
    cursor = initDatabase()
    sql ="DROP TABLE IF EXISTS drive_route_tb"
    #print sql
    executeDB( cursor, sql )
    
    create_drive_route_tb_sql = '''create table if not exists drive_route_tb(
                    id                            bigint(20) unsigned not null auto_increment primary key comment '编号',
                    route_name             char(100) comment'由起点经纬度到终点经纬度做hash，提高查询速度',
                    route_hash             char(32) comment'由起点经纬度到终点经纬度做hash，提高查询速度',
                    start_area_id            bigint(20) comment'起点方块编号, 编号是point_area_tb 表中的ｉｄ列',
                    end_area_id             bigint(20)  comment'终点方块编号, 编号是point_area_tb 表中的ｉｄ列',
                    distance       int unsigned not null default 0 comment '距离（单位：米）',
                    duration     int unsigned not null default 0 comment '时间（单位：秒）',
                    update_time     timestamp not null
        )
    '''        
    executeDB( cursor, create_drive_route_tb_sql ) 
    cursor.close()


#***********************************************************************************
#更新点方块列表中各个点的地址
def queryPathOneToOthers( area_id ):
     #go through all route in database 
    cursor = initDatabase()
    
    
    #起点方块信息
    start = dict()
    try:
        count = cursor.execute("SELECT * from point_area_tb WHERE id=%d"%area_id)
        if( count ==1 ):
            result = cursor.fetchone()
        else:
            print' query area driver route error'
    except Exception, e:
        print e
    if(result):
        start['area_id']=result[0]
        start['simple_lng']=result[1]
        start['simple_lat'] =result[2]
            
    #依次和其他点计算驾车路劲    
    end = dict()
    try:
        count = cursor.execute("SELECT * from point_area_tb ORDER BY id")
        print 'database return %d line'%(count)
        result = cursor.fetchall()
    except Exception, e:
        print e
    
    if result:
        for item in result:
            end['area_id'] = item[0]
            end['simple_lng'] = item[1]
            end['simple_lat'] = item[2]
            
            print '-'*10+ 'queryPathOneToOthers:  '+ ' Total:' + str(count) +'  id:' + str(item[0]) + ' '+ '-'*30
            inserPathToDriveTable( start, end)
            
    print 'finish update address to route table'
    cursor.close()    
    
    
#***********************************************************************************************
def queryPathOneself( ):
    cursor = initDatabase()
    #go through all route in database 
    try:
        count = cursor.execute("SELECT *  FROM recommend_route_tb ORDER BY id")
        print 'database return %d line'%(count)
        result = cursor.fetchall()
    except Exception, e:
        print e

    if result:
        for item in result:
            print '-'*30 + ' Total:' + str(count) +'  id:' + str(item[0]) + ' '+ '-'*30
            #route_id = item[2]
            start =dict()
            start['simple_lng'] = item[6]
            start['simple_lat'] = item[7]
            start['area_id'] = item[9]
            end = dict()
            end['simple_lng'] = item[12]
            end['simple_lat'] = item[13]
            end['area_id'] = item[15]
    cursor.close()   
  
#*****************************************************************************************
def inserPathToDriveTable( start, end):
    #查询在数据库中是否已经有了
    cursor = initDatabase()
    route_name = aMap.buildRouteName(start['simple_lng'], start['simple_lat'] , end['simple_lng'], end['simple_lat'] )
    query_sql = "SELECT * FROM drive_route_tb WHERE  route_name = '%s'"%route_name
    #print query_sql
    count = cursor.execute( query_sql)
    #print query_sql
    print "query record %s  weather in dirver_route_tb"%route_name
    
    #print count
    if( count == 0 ): 
        #如果没有这条路线
        json_str = aMap.requestDirveRoute(start['simple_lng'], start['simple_lat'] , end['simple_lng'], end['simple_lat'] )
        path = aMap.parseDiverRoute(json_str)
        
        insert_sql = "INSERT INTO drive_route_tb( id, route_name, route_hash, start_area_id, end_area_id,\
                                distance, duration, update_time) \
                                VALUES(NULL, '%s', 'null', %d, %d,   %d,%d, now() ) " %\
                            ( route_name, start['area_id'], end['area_id'],path['distance'], path['duration'])
        #print insert_sql
        executeDB(cursor, insert_sql)
    else:
        print 'drive route is already in table, do nothing'
                 
#*****************************************************************************************               
def queryDistanceFromDriveTable( start_simple_lng, start_simple_lat, end_simple_lng, end_simple_lat):
    distance = 0
    #查询在数据库中是否已经有了
    cursor = initDatabase()
    route_name = aMap.buildRouteName( start_simple_lng, start_simple_lat, end_simple_lng, end_simple_lat )
    query_sql = "SELECT distance FROM drive_route_tb WHERE  route_name = '%s'"%route_name
    #print query_sql
    count = cursor.execute( query_sql)
    #print query_sql
    #print "query record %s  wether in dirver_route_tb"%route_name
    
    #print count
    if( count == 0 ): 
        #如果没有这条路线
        json_str = aMap.requestDirveRoute(start_simple_lng, start_simple_lat, end_simple_lng, end_simple_lat )
        path = aMap.parseDiverRoute(json_str)
        distance = path['distance']
        insert_sql = "INSERT INTO drive_route_tb( id, route_name, route_hash, start_area_id, end_area_id,\
                          distance, duration, update_time) \
                          VALUES(NULL, '%s', 'null', %d, %d,   %d,%d, now() ) " %\
                      ( route_name, 0,0,path['distance'], path['duration'])
        #print insert_sql
        executeDB(cursor, insert_sql)
    else:
        result = cursor.fetchone()
        distance = result[0]
        
    return distance

#***************************************************************
#存储所有点对应的方块
def createRecommendFactorTable(cursor, table_name ):
    sql ="DROP TABLE IF EXISTS %s"%table_name
    executeDB( cursor, sql )
    
    
    create_point_area_tb_sql = '''create table if not exists %s(
                    id            int unsigned not null auto_increment primary key comment '粗化经纬度后，起点对应的方块编号',
                    car_route_id       int unsigned not null comment '车主路线',
                    passenger_route_id       int unsigned not null comment '匹配的乘客路线',
                    match_factor            float not null default 0.0 comment "综合排名因子，越大越好",
                    car_extra_distance    int   not null default 0 comment '车主绕行距离',
                    car_extra_factor        float not null default 0.0 comment "车主绕行因子： 越小越好",
                    car_earn_factor         float  not null default 0.0 comment "车主收益因子： 越大越好",
                    update_time     timestamp not null
        )'''%table_name
    #print create_point_area_tb_sql
    cursor.execute(create_point_area_tb_sql)


        