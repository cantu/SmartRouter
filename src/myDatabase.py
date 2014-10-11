#!/usr/bin/python
# encoding: utf-8

import MySQLdb;


#***************************************************************
#complete insert a row in database.
def executeDB( cursor, sql ):
    try:
        cursor.execute( sql )
    except MySQLdb.Error,e:
        print e



#***************************************************************
#新建路线表，将所有需要处理的路线存储
def createRecommendRouteTable(cursor):
	sql ="DROP TABLE IF EXISTS recommend_route_tb"
	#executeDB( cursor, sql )
	print sql
	
	sql = '''
		create table recommend_route_table
		(
		id                      int unsigned not null auto_increament primary key,
		route_type				enum('find_driver', 'find_passenger') not null,
		creater_uid				bigint(20) unsigned not null comment '路线创建者ID',
		route_id				bigint(20) unsigned not null comment '路线唯一标示，对应到youche_route的id列',
		start_longtitude        decimal(13,10) not null,
		start_lattitude         decimal(13,10) not null,
		start_simple_lng        decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
		start_simple_lat        decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
		start_address           varchar(200) not null comment '精确经纬度对应的地址',
		strat_area_id           bigint(20) unsigned not null comment '粗化经纬度后，起点对应的方块编号',
		end_longtitude          decimal(13,10) not null,
		end_latitude            decimal(13,10) not null,
		end_simple_lng          decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
		end_simple_lat          decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
		end_address             varchar(200) not null comment '精确经纬度对应的地址',
		end_area_id             bigint(20) unsigned not null comment '粗化经纬度后，终点对应的方块编号',
		recommand_route_id      varchar(200) comment '推荐的同路路线id,以逗号分隔',
		update_time             timestamp not null
	)
	'''
	print sql
	#executeDB( cursor, sql )

#***************************************************************
#向表中添加一条新的路线
def insertRouteToTable( cursor, route):
	
	sql="

#***************************************************************
def createPointAreaTable(cursor):
	sql ="DROP TABLE IF EXISTS point_area_tb"
	executeDB( cursor, sql )
	
	sql = '''
		create table ponit_area_tb
		(
    		id              int unsigned not null auto_increament primary key,
   		 	area_id         bigint(20) unsigned not null comment '粗化经纬度后，起点对应的方块编号',
    		simple_lng      decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
    		simple_lat      decimal(13,10) not null comment '粗化经纬度，取到小数点后3位，大概500m的范围',
    		address         varchar(200) not null comment '精确经纬度对应的地址',
    		address_hash    char(32) comment'对地址做hash',
    		point_num       int unsigned not null default 0 comment '落在这个方块内的点的总数',
    		route_id        text comment '起点或终点在这个方块内的路线id,以逗号分隔',
    		update_time     timestamp not null
		)
	'''
	print sql
	#executeDB( cursor, sql )

