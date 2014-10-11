#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

import ConfigParser
import MySQLdb
import sys
import time

#import other python files
import aMap
import myDatabase

#reload(sys)
#sys.setdefaultencoding('utf-8')



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
	db_name		 = config.get( section, "db_name")
	db_table	 = config.get( section, "db_table")
	db_host 	 = config.get( section, "db_host") 
	db_user 	 = config.get( section, "db_user")
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
			route['route_id'] 		= result[0]	#每条线路的唯一标示符
			route['creater_uid']	= result[1]
			#route['start_name'] 	= result[5]	#根据起点坐标，客服端查询到的地址，可能不太准确，可以自己再查询一次
			route['start_id']		= result[4]	#每一个坐标点对应一个id，通过这个id与数据表youche_location联系
			#route['end_name'] 		= result[8]
			route['end_id'] 		= result[7]
			route['type'] 			= result[20] #路线分为找司机或者找乘客两种类型
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
def simpleLocation( longtitude, latitude ):

	#longtitude = point['longtitude']
	#latitude   = point['latitude']
	#经纬度的小数点第三位大概距离是1000M
	#对第三位做粗话处理，第三位要么是０，要么是５
	#step: *2 -> 取小数点后两位 -> /2 -> 取小数点后三位  
	simple_lng = float("%.3f"%(float("%.2f"%(longtitude*2))/2))
	simple_lat = float("%.3f"%(float("%.2f"%(latitude  *4))/4))
	
	'''
	#check 
	last = int(route['start_simple_lng'] * 1000 %10)
	print 'last=',last
	if (last!=0 and last!=5):
		print 'error!'
	'''
	return (simple_lng, simple_lat )

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

	( route['start_simple_lng'], route['start_simple_lat']) = simpleLocation(\
		route['start_longtitude'], route['start_latitude'] )
	( route['end_simple_lng'], route['end_simple_lat']) = simpleLocation(\
		route['end_longtitude'], route['end_latitude'])
	#print str( route )
	
	return route

#**************************************************************************
def addAddressToRoute( route ):
	start = {'lng':route['start_longtitude'], 'lat':route['start_latitude']}
	end   = {'lng':route['end_longtitude'], 'lat':route['end_latitude']}
	( url, json_str) =  aMap.regeoDecode( start )
	#print json_str
	route['start_address'] = aMap.getRegeoDecodeAddress(json_str )
	(url, json_str) = aMap.regeoDecode( end )
	route['end_address'] = aMap.getRegeoDecodeAddress(json_str )

#**************************************************************************
def printRoute( route ):
	if( len(route) > 0):
		for item in route:
			print "route[%20s]: %s"%( item, route[item] )

#**************************************************************************
# main function

cursor = initDatabase()

#myDatabase.createRecommendRouteTable( cursor )
myDatabase.createPointAreaTable( cursor )


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
		route = getRoute( cursor, route_id) 
		
		#addAddressToRoute( route )
		
		printRoute( route )
		
		#myDatabase.insertRouteToTable(cursor, route)
		
		myDatabase.inserPointToAreaTable(cursor, route )
		#time.sleep(1)

print 'finish'






















