#!/usr/bin/python
#encoding=utf-8
# -*- coding: utf-8 -*-

import ConfigParser
import urllib2
import urllib
import json


#***********************************************************
#逆地理编码
#输入一个点的经纬度，返回街道名称
#http://restapi.amap.com/v3/geocode/regeo?location=116.396574,39.992706&key=608d75903d29ad471362f8c58c550daf&s=rsv3&radius=1000&extensions=all

def regeoDecode( lng, lat):
	
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
		return address
#***********************************************************
#http://restapi.amap.com/v3/direction/driving?origin=116.379018,39.865026&destination=116.321139,39.896028&strategy=0&extensions=&s=rsv3&key=608d75903d29ad471362f8c58c550daf
def requestDirveRoute( start, end):

	URL = "http://restapi.amap.com/v3/direction/driving"
	
	#配置参数详见：http://lbs.amap.com/api/javascript-api/reference/search_plugin/
	parameter = dict()
	parameter['origin'] = str(start['lng']) + ',' + str(start['lat'])
	parameter['destination'] = str(end['lng']) + ',' +str(end['lat'])
	parameter['s'] 		  = 'rsv3'

	parameter['strategy'] = 0

	#http://lbs.amap.com/api/javascript-api/reference/search_plugin/
	#默认值：base，返回基本地址信息
	#当取值为：all，返回DriveStep基本信息+DriveStep详细信息
	parameter['extensions']='base'
	
	file_name = "Configure.ini"
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

	return ( request_url, json_str )

#***********************************************************
'''
def getRegeoDecodeAddress( json_str, request_url ):
	data = json.loads( json_str )
	#print data
	#print data.keys()
	if ( int(data['status']) == 1):
		address = data['regeocode']['formatted_address']
		return address
	else:
		print 'error, aMap getRegeoDecodeAddress json return status is not 1'
		print request_url
		return ''
'''
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
def GetDistance( lng1,  lat1,  lng2,  lat2):
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

#**********************************************************
#main function

#test()

#GetDistance(116.372, 39.865, 116.371, 39.865)

	
