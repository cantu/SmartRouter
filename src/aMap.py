#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import urllib2
import urllib
import json


#***********************************************************
#逆地理编码
#输入一个点的经纬度，返回街道名称
#http://restapi.amap.com/v3/geocode/regeo?location=116.396574,39.992706&key=608d75903d29ad471362f8c58c550daf&s=rsv3&radius=1000&extensions=all

def regeoDecode( point ):

	#请求地址是分析逆地理编码的例子，抓取到请求地址
	URL = "http://restapi.amap.com/v3/geocode/regeo"
	lat = point['lat']
	lng = point['lng']

	#配置参数详见：http://lbs.amap.com/api/javascript-api/reference/search_plugin/
	parameter = dict()
	parameter['location'] = str(lng) + ',' + str(lat)
	parameter['s'] 		  = 'rsv3'
	parameter['radius']	  = '1000'

	#逆地理编码时，返回信息详略
	#默认值：base，返回基本地址信息；
	#取值为：all，返回地址信息及附近poi、道路、道路交叉口等信息
	parameter['extensions']='base'
    
	file_name = "Configure.ini"
	section = "map"
	config = ConfigParser.ConfigParser()
	config.read( file_name )
	parameter['key']    = config.get( section, "amap_js_key")

	#HTTP get request
	#print urllib.urlencode(parameter)
	header={"User-Agent": "Mozilla-Firefox5.0"}
	request = urllib2.Request( URL, urllib.urlencode(parameter) , header)
	response = urllib2.urlopen( request )
	json_str = response.read()

	request_url = urllib.unquote( URL +'?'+ urllib.urlencode(parameter) )

	return ( request_url, json_str )

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
	#header={"User-Agent": "Mozilla-Firefox5.0"}
	header = { "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0"}
	request = urllib2.Request( URL, urllib.urlencode(parameter) , header)
	response = urllib2.urlopen( request )
	json_str = response.read()
	#print json_str
	request_url = urllib.unquote( URL +'?'+ urllib.urlencode(parameter) )

	return ( request_url, json_str )

#***********************************************************
def getRegeoDecodeAddress( json_str ):
	data = json.loads( json_str )
	#print data
	#print data.keys()
	if ( int(data['status']) == 1):
		address = data['regeocode']['formatted_address']
		return address
	else:
		print 'error, json return status is not 1'
		return ''

#***********************************************************

def test():
	start = {'lng':116.379018, 'lat':39.865026}
	end   = {'lng':116.321139, 'lat':39.896028}

	(url, json_str) = regeoDecode( start )
	print "%s" %getRegeoDecodeAddress( json_str)
	#regeoDecode( end   )

	#print requestDirveRoute( start, end )



#**********************************************************
#main function

#test()

	
