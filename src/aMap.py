#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

import ConfigParser
import urllib2
import urllib
import json
import datetime


#***********************************************************
#逆地理编码
#输入一个点的经纬度，返回街道名称
#http://restapi.amap.com/v3/geocode/regeo?location=116.396574,39.992706&key=608d75903d29ad471362f8c58c550daf&s=rsv3&radius=1000&extensions=all

def regeoDecode( lng, lat):
	
	start_time = datetime.datetime.now()
	#请求地址是分析逆地理编码的例子，抓取到请求地址
	URL = "http://restapi.amap.com/v3/geocode/regeo"
	#lat = point['lat']
	#lng = point['lng']

	#配置参数详见：http://lbs.amap.com/api/javascript-api/reference/search_plugin/
	parameter = dict()
	parameter['location'] = str(lng) + ',' + str(lat)
	parameter['s'] 		  = 'rsv3'
	parameter['radius']	  = '1000'

	#逆地理编码时，返回信息详略
	#默认值：base，返回基本地址信息；
	#取值为：all，返回地址信息及附近poi、道路、道路交叉口等信息
	parameter['extensions']='base'
	file_name = "../data/Configure.ini"
	section = "map"
	config = ConfigParser.ConfigParser()
	config.read( file_name )
	parameter['key']    = config.get( section, "amap_js_key")
	
	#HTTP get request
	#print urllib.urlencode(parameter)
	header={"User-Agent": "Mozilla-Firefox5.0"}
	#header = { "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0"}
	
	address = ''
	isSuccess = False
	while( isSuccess == False):
		request = urllib2.Request( URL, urllib.urlencode(parameter) , header)
		response = urllib2.urlopen( request )
		json_str = response.read()
		request_url = urllib.unquote( URL +'?'+ urllib.urlencode(parameter) )
		data = json.loads( json_str )
	
		if ( int(data['status']) == 1):
			address = data['regeocode']['formatted_address']
			isSuccess = True
		else:
			isSuccess = False
			print 'error, regeoDecode return error!'
			print request_url
			#print request_url
			#return request_url
	end_time = datetime.datetime.now()
	elapsed = (end_time -  start_time ).seconds
	print( 'aMap regeo decode used time: ', elapsed)
	return address
#***********************************************************
#http://restapi.amap.com/v3/direction/driving?origin=116.379018,39.865026&destination=116.321139,39.896028&strategy=0&extensions=&s=rsv3&key=608d75903d29ad471362f8c58c550daf
def requestDirveRoute( start_lng, start_lat , end_lng, end_lat):
	start_time = datetime.datetime.now()
	URL = "http://restapi.amap.com/v3/direction/driving"
	#配置参数详见：http://lbs.amap.com/api/javascript-api/reference/search_plugin/
	parameter = dict()
	parameter['origin'] = str(start_lng) + ',' + str(start_lat)
	parameter['destination'] = str(end_lng) + ',' +str(end_lat)
	parameter['s'] 		  = 'rsv3'
	parameter['strategy'] = 0
	#http://lbs.amap.com/api/javascript-api/reference/search_plugin/
	#默认值：base，返回基本地址信息
	#当取值为：all，返回DriveStep基本信息+DriveStep详细信息
	parameter['extensions']='base'
	
	file_name = "../data/Configure.ini"
	section = "map"
	config = ConfigParser.ConfigParser()
	config.read( file_name )
	parameter['key']    = config.get( section, "amap_js_key")
	
	#HTTP get request
	header={"User-Agent": "Mozilla-Firefox5.0"}
	#header = { "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0"}
	request = urllib2.Request( URL, urllib.urlencode(parameter) , header)
	response = urllib2.urlopen( request )
	json_str = response.read()
	#print json_str
	request_url = urllib.unquote( URL +'?'+ urllib.urlencode(parameter) )
	print request_url
	#check json ok?
	isSuccess = False
	tryTimes = 0
	while( isSuccess == False):
		data = json.loads( json_str )
		if ( int(data['status']) == 1):
			#distance = data['route']['paths']['ditance']
			isSuccess = True
		else:
			#驾车路线规划有问题的请求
			#http://restapi.amap.com/v3/direction/driving?origin=116.3350000000,39.9850000000&destination=121.3800000000,31.3100000000&strategy=0&s=rsv3&extensions=all&key=136474740ad745393d698348ab7c3153
			isSuccess = False
			tryTimes +=1
			print 'error, request drive route  return error, try times:', tryTimes
			print request_url
		#10次请求都错误后返回错位的结果
		if(tryTimes >10):
			break;
	end_time = datetime.datetime.now()
	elapsed = (end_time -  start_time ).seconds
	print( ' query one point all drive route total used time: ', elapsed)
	print( 'aMap route request used time: ', elapsed)
	return json_str

#***********************************************************
#
def parseDiverRoute( json_str ):
	distance = 0
	data = json.loads( json_str )
	path = dict()
	if ( int(data['status']) == 1):
			path['distance'] = int(data['route']['paths'][0]['distance'])
			path['duration'] = int(data['route']['paths'][0]['duration'])
	else:
		path['distance'] = 0
		path['duration'] = 0
		print 'Error, json state is not ok.'
		
	return path

#***********************************************************

def test():
	start = {'lng':116.379018, 'lat':39.865026}
	end   = {'lng':116.321139, 'lat':39.896028}

	(url, json_str) = regeoDecode( start )
	#print "%s" %getRegeoDecodeAddress( json_str)
	#regeoDecode( end   )

	#print requestDirveRoute( start, end )


#************************************************************
# 根据经纬度计算两点间距离
# 经度 long  纬度 lat
def GetDistanceByMath( lng1,  lat1,  lng2,  lat2):
    u'''''计算两点间球面距离 单位为m'''
    EARTH_RADIUS = 6378.137 # 地球周长/2*pi 此处地球周长取40075.02km pi=3.1415929134165665
    from math import asin,sin,cos,acos,radians, degrees,pow,sqrt, hypot,pi
    
    # 方法1
    # 据说来源于 google maps 的脚本
    # 见 http://en.wikipedia.org/wiki/Great-circle_distance 中的 haversine
    radLat1 = radians(lat1) # a点纬度(单位是弧度)
    radLat2 = radians(lat2) # b点纬度(单位是弧度
    a = radLat1 - radLat2 # 两点间的纬度弧度差
    b = radians(lng1) - radians(lng2) # 两点间的经度弧度差
    s = 2 * asin(sqrt(pow(sin(a/2),2) + cos(radLat1)*cos(radLat2)*pow(sin(b/2),2))) # 两点间的弧度
    s = s * EARTH_RADIUS
#   s = round(s * 10000) / 10000 # 四舍五入保留小数点后4位
    d=s*1000
    print '采用：d1=',d
 
    # 方法2
    # ''' 经纬坐标为P(x1,y1) Q(x2,y2) '''
    #   D=arccos[cosy1*cosy2*cos(x1-x2)+siny1*siny2]*2*PI*R/360
    d=acos(cos(radians(lat1))*cos(radians(lat2))*cos(radians(lng1-lng2))+sin(radians(lat1))*sin(radians(lat2)))*EARTH_RADIUS*1000
    print '参考：d2=',d
    return d


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

#******************************************************************************************
#再驾车路线表中，ｋｅｙ采用两点的组合名称
#下面的规则可以合并　Ａ点到Ｂ点　　Ｂ点到Ａ点　两种情况
def buildRouteName( start_lng, start_lat, end_lng, end_lat):
    if(start_lng > end_lng):
        route_name ='%s'% ('%.3f_%.3f_%.3f_%.3f'%(start_lng, start_lat, end_lng, end_lat))
    else:
        route_name = '%s'%( '%.3f_%.3f_%.3f_%.3f'%(end_lng, end_lat, start_lng, start_lat) )
    #元组转字符串
    string = "".join(route_name)
    return string

#**********************************************************
#main function

#test()

#GetDistanceByMath(116.372, 39.865, 116.371, 39.865)

	
