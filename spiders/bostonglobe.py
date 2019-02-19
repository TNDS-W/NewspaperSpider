import requests
from lxml import etree
import re
from spiders.basespider import Spider
##
class Bostonglobe(Spider):
	Session = requests.session()
	newspaperlibraryid = "1057442039982981120"
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
		'cookie':'bc_tstgrp=2; BGSessionID=09af2381-56a2-4823-8770-f11c70865680; s_fid=7C86A1CD6F6086BB-045CA95CB731E2AE; rmStore=smid:6744d122-8943-4144-a821-1016747106eb; __gads=ID=5cb12fa0e98f444f:T=1545612564:S=ALNI_Mad0OaPmx8hOKr7hfWdE5-vADYujg; RDB=c8030000000000000055533a4d412d2d2d2d2d2d2d2d2d2d00660000000080000000000000010005358091; TData=|||||||; FMFailure=AUTHENTICATED:0:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI1MzU4MDkxIiwiYXV0aFRva2VuIjoiNTBhZmEwYjUtNGJjMS00MTFmLTg3MmQtMzJkNDRkNTFiODViIn0.6nTcsmuhKaLK2u9WvvMrmP19Oxrt2obu8tqWY8oyL5k; s_cc=true; bostonuser=5358091; bostontoken=50afa0b5-4bc1-411f-872d-32d44d51b85b; pathAuth=50afa0b5-4bc1-411f-872d-32d44d51b85b; pathAuthJWT=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI1MzU4MDkxIiwiYXV0aFRva2VuIjoiNTBhZmEwYjUtNGJjMS00MTFmLTg3MmQtMzJkNDRkNTFiODViIn0.6nTcsmuhKaLK2u9WvvMrmP19Oxrt2obu8tqWY8oyL5k; stc111668=env:1546579576%7C20190204052616%7C20190104062932%7C14%7C1014751:20200104055932|uid:1545612542718.2051084298.4287162.111668.737108788.:20200104055932|srchist:1014751%3A1546579576%3A20190204052616:20200104055932|tsa:1546579576724.1468957604.2304344.21773908689085308:20190104062932; pathUrl=/todayspaper/2019/01/03%3Bjsessionid=E568AB62E0738C5663F3117F49CAA74F; s_ppv=10; _sp_id.ece6=003fd9ff90df8e8f.1545612535.10.1546581603.1545633116; s_sq=nytbostonglobecom%2Cnytbgglobal%3D%2526pid%253DToday%252527s%252520Paper%252520%25257C%252520BGC%252520Homepage%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fepaper.bostonglobe.com%25252F%2526ot%253DA; html5pubguid=2c60291d-c20c-4780-9829-b3d9a12687cf'
	}
	def paper_list(self, i=0):
		while i < 3:
			try:
				response = self.Session.get('https://epaper.bostonglobe.com/',headers=self.headers)
				break
			except:
				i += 1
				if i == 3:
					print('采集失败，请检查网络')
					return
				continue
		html = etree.HTML(response.text)
		script = html.xpath('//script/text()')[0].split(';')
		data = {}
		data['pubid'] = script[6].split('"')[-2]
		data['edid'] = script[8].split('"')[-2]
		data['lm'] = script[13].split()[-1]
		date = script[11].split('"')[-2].split('/')
		while i < 3:
			try:
				response = self.Session.get('https://epaper.bostonglobe.com/html5/reader/get_articles.aspx', params=data,headers=self.headers)
				break
			except:
				i += 1
				if i == 3:
					print('采集失败，请检查网络')
					return
				continue
		data['device'] = 'desktop'
		data['version'] = 'production'
		data['os'] = 'windows'
		while i < 3:
			try:
				rep = self.Session.get('https://epaper.bostonglobe.com/html5/reader/get_settings.aspx', params=data,headers=self.headers)
				break
			except:
				i += 1
				if i == 3:
					print('采集失败，请检查网络')
					return
				continue
		return response.json()['articles'],'-'.join([date[2],date[0],date[1]]),rep.json()

	def paper_text(self,data,channel_data):
		package = {'title': data['headline'], 'subTitle': data['subHeadline'], 'author': '', 'authorDescriptions': '',
				   'authorArea': '', 'page': '', 'mainBody': '', 'images': [], 'imageDescriptions': [],
				   'abstract': '', 'channel': '', 'cookies': '', 'referer': '',
				   }
		page_num = int(data['pageNumber'])
		for i in range(len(channel_data['bookmarks']['bookmark'])):
			page = int(channel_data['bookmarks']['bookmark'][i]['page'])
			if page_num >= page:
				try:
					if page_num < int(channel_data['bookmarks']['bookmark'][i+1]['page']):
						package['channel'] = channel_data['bookmarks']['bookmark'][i]['name']
				except:
					package['channel'] = channel_data['bookmarks']['bookmark'][i]['name']
		page_number = channel_data['reader']['friendlyNumbering']
		b = []
		c = []
		for i in page_number.split('|')[:-1]:
			n = i.split(':')
			b.append(n[0])
			c.append(int(n[1]))
		for i in range(len(c)):
			try:
				if page_number > c[i] and page_number <= c[i + 1]:
					package['page'] = b[i] + str(page_number - c[i])
			except:
				package['page'] = b[i] + str(page_num - c[i])
		authors = re.sub('<div.*?>', '', data['byline']).split('</div>')
		package['author'] = authors[0].replace('By', '').replace(' and ', '#').strip()
		for i in data['images']:
			package['images'].append(i['url'])
			package['imageDescriptions'].append(i['caption'])
		package['images'] = '#'.join(package['images'])
		package['imageDescriptions'] = '#'.join(package['imageDescriptions'])
		if not data['body']:
			return
		html = etree.HTML(data['body'])
		text = etree.tostring(html.xpath('//body')[0]).decode('utf-8', 'ignore')
		text = re.sub('<body.*?>|</body>', '', text).replace('<p />','').replace('<p/>','')
		package['mainBody'] = re.sub('<em.*?>|</em>', '', text).replace('&#8220;','"').replace('&#8217;&#8217;','"').replace('&#8217;','\'')
		return package

	def run(self):
		print('开始采集：波士顿环球邮报')
		data_list,date,channel_data = self.paper_list()
		if self.a(date):
			return 0
		print('数据获取成功，开始解析')
		package = []
		tips = 0
		for i in data_list:
			tips += 1
			print("正在采集第%d篇" % (tips))
			data = self.paper_text(i,channel_data)
			if data:
				package.append(data)
			else:
				continue
		super().uploaddata(date, package, self.newspaperlibraryid, True)
		print("采集成功:波士顿环球邮报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
		return len(package)

	def supplement(self):
		date = input('请输入日期：(年-月-日，例如：2019-01-06)\n')
		if self.a(date):
			return 0
		data,channel = self.date_paper('/'.join([i for i in reversed(date.split('-'))]))
		if not data:
			return 0
		package = []
		tips = 0
		for i in data:
			tips += 1
			print("正在采集第%d篇" % (tips))
			data = self.paper_text(i,channel)
			if data:
				package.append(data)
			else:
				continue
		super().uploaddata(date, package, self.newspaperlibraryid, True)
		print("采集成功:波士顿环球邮报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
		return len(package)

	def date_paper(self,date,i=0):
		try:
			response = self.Session.get('https://epaper.bostonglobe.com/',headers=self.headers)
			html = etree.HTML(response.text)
			script = html.xpath('//script/text()')[0].split(';')
			data = {'maxnumber': '22222222', 'version': 'production'}
			data['publicationguid'] = script[6].split('"')[-2]
			data['lm'] = script[13].split()[-1]
			response = self.Session.get('https://epaper.bostonglobe.com/html5/editionsdesktop_json.aspx',headers=self.headers, params=data)
			eid = {'pubname':'','edid':''}
			for i in response.json()['editions']['edition']:
				if i['@date'] == date:
					eid['edid'] = i['@editionguid']
					break
			if eid['edid']:
				print('已找到指定报纸，开始获取数据')
			else:
				print('未找到指定报纸，请确认日期是否正确')
				return
			response = self.Session.get('https://epaper.bostonglobe.com/html5/reader/production/default.aspx',headers=self.headers, params=eid)
			html = etree.HTML(response.text)
			script = html.xpath('//script/text()')[0].split(';')
			data = {}
			data['pubid'] = script[6].split('"')[-2]
			data['edid'] = script[8].split('"')[-2]
			data['lm'] = script[13].split()[-1]
			response = self.Session.get('https://epaper.bostonglobe.com/html5/reader/get_articles.aspx', params=data,headers=self.headers)
			data['device'] = 'desktop'
			data['version'] = 'production'
			data['os'] = 'windows'
			rep = self.Session.get('https://epaper.bostonglobe.com/html5/reader/get_settings.aspx', params=data,headers=self.headers)
			return response.json()['articles'],rep.json()
		except:
			if i<3:
				i += 1
			else:
				print('获取报纸失败，请检查网络')
				return
			return self.date_paper(date,i=i)

	def a(self,publishedtime):
		api = self.api
		# 先获取token
		ret = api.gettoken()
		if not ret:
			return 0
		ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
		# 如果为True,则说明已经存在
		if (ret["success"] and ret["result"]):
			print("采集失败：波士顿环球邮报-发行日期已经存在，报纸日期（" + publishedtime + ")")
			return True
		else:
			return False