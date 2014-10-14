#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

import ConfigParser
import MySQLdb
import sys
import time
import sqlite3

#**************************************************************************
def initSqllite():
    create_recommend_route_tb_sql = '''  create table if not exists recommend_route_tb(\
                           id                            int unsigned not null auto_increment primary key,
                            creater_uid                bigint(20) unsigned not null comment '路线创建者ID',
                            route_id                bigint(20) unsigned not null comment '路线唯一标示，对应到youche_route的id列',
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
    con = sqlite3.connect("../data/youche_route.db")
    cursor = con.cursor()
    
    cursor.execute( cursor, create_recommend_route_tb_sql)
    cursor.commit()
    
    
    con.close()
    
    #***************************************************************************
    initSqllite()