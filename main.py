#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import logging
import cgi
import json
from google.appengine.ext.webapp import template 
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class MainHandler(webapp2.RequestHandler):
	def judgeSameStation(self, start, end):
		if(start == end):
			return True
		return False

	def judgeSameStationContain(self, nextStartStations, end):
		for nextStartStation in nextStartStations:
			if nextStartStation['Station'] == end:
				return True
		return False

	def getSameStationContain(self, nextStartStations, end):
		ans = {}
		for nextStartStation in nextStartStations:
			if nextStartStation['Station'] == end:
				ans = nextStartStation
		return ans


	def getPointSet(self, point, stas):
		somePoint = []
		for sta in stas:
			if sta['Station'] == point:
				somePoint.append(sta)
				self.response.write(sta['Name'])
				self.response.write(sta['Station'])
		return somePoint

	def getParentPoint(self, endPoint, stas):
		parentPoint = {}
		for sta in stas:
			if sta['Station'] == endPoint['ParentStation'] and sta['Name'] == endPoint['ParentName']:
				parentPoint = sta
		return parentPoint

	def getNextStations(self, startPoint, stas):
		nextStartStations = []
		preSta = {'Name': '', 'Station': '', 'ParentName': '', 'ParentStation': ''}
		#self.response.write("sta--- [ " + startPoint['Name'] + "," + startPoint['Station'] +  "," + startPoint['ParentName'] + "," + startPoint['ParentStation'] +" ] ")
		for sta in stas:
			if sta['Station'] == startPoint['Station'] and sta['Name'] == startPoint['Name']:
				if preSta['ParentName'] == '' and (preSta['Name'] == sta['Name'] or preSta['Station'] == sta['Station']):
					preSta['ParentName'] = sta['Name']
					preSta['ParentStation'] = sta['Station']
					nextStartStations.append(preSta)
					self.response.write(" [ " + sta['Name'] + "," + sta['Station'] +  "," + sta['ParentName'] + "," + sta['ParentStation'] +" ] ")
			if preSta['Station'] == startPoint['Station'] and preSta['Name'] == startPoint['Name'] and sta['ParentName'] == '':
				if preSta['Name'] == sta['Name'] or preSta['Station'] == sta['Station']:
					sta['ParentName'] = preSta['Name']
					sta['ParentStation'] = preSta['Station']
					nextStartStations.append(sta)
					self.response.write(" [ " + sta['Name'] + "," + sta['Station'] +  "," + sta['ParentName'] + "," + sta['ParentStation'] +" ] ")
			preSta = sta
		return nextStartStations

	def get(self):
		data = cgi.FieldStorage()
		start = data.getvalue('start', 'notfound').decode('utf-8')
		if start == 'notfound':
			self.response.write("<p>出発駅を入力してください</p>")
		end = data.getvalue('end', 'notfound').decode('utf-8')
		if end == 'notfound':
			self.response.write("<p>到着駅を入力してください</p>")
		
		base_url = "http://fantasy-transit.appspot.com/net?format=json"
		json_data = urlfetch.fetch(base_url)
		j = json.loads(json_data.content,"utf-8")
		#初期化
		stas = []
		for item in j:
			for sta in item['Stations']:
				stas.append({'Name': item['Name'], 'Station': sta, 'ParentName': '', 'ParentStation': ''})
				#self.response.write(" [ " + item['Name'] + "," + sta +  "," + stas[-1]['ParentName'] + "," + stas[-1]['ParentStation'] +" ] ")

		result = [] 
		nextStartStations = []
		startPoint = self.getPointSet(start, stas)
		if self.judgeSameStation(start, end):
			if(start != 'notfound' and end != 'notfound'):
				result =  result + startPoint
		else:
			for startP in startPoint:
				nextStartStations = nextStartStations + self.getNextStations(startP, stas)
			while self.judgeSameStationContain(nextStartStations, end) == False:
				if len(nextStartStations) != 0:
					print(nextStartStations)
					for nextStartStation in nextStartStations:
						nextStartStations = nextStartStations + self.getNextStations(nextStartStation, stas) 

			#for sta in stas:
				#self.response.write(" [ " + sta['Name'] + "," + sta['Station'] +  "," + sta['ParentName'] + "," + sta['ParentStation'] +" ] ")
			
			endPoint = self.getSameStationContain(nextStartStations, end)
			self.response.write(" enddd--------------[ " + endPoint['Name'] + "," + endPoint['Station'] +  "," + endPoint['ParentName'] + "," + endPoint['ParentStation'] +" ] ")
			while 1:
				result.append(endPoint)
				endPoint = self.getParentPoint(endPoint, stas)
				self.response.write(" enddd--------------[ " + endPoint['Name'] + "," + endPoint['Station'] +  "," + endPoint['ParentName'] + "," + endPoint['ParentStation'] +" ] ")
				if(endPoint['Station'] == start):
					break

		for nextStartStation in nextStartStations:
			self.response.write(" [ " + nextStartStation['Name'] + "," + nextStartStation['Station'] +  "," + nextStartStation['ParentName'] + "," + nextStartStation['ParentStation'] +" ] ")

		body = "hoge"
		template_values = {'body': body,}
		path = os.path.join(os.path.dirname(__file__) + '/', 'main.html')
		self.response.out.write(template.render(path,template_values))
		self.response.write("現在地")
		if len(result) != 0:
			for res in reversed(result):
				self.response.write(" -> " + res['Name'] + ":" + res['Station'])


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
