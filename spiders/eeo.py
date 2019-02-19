import requests
from lxml import etree
import re
import operator
from functools import reduce
from spiders.basespider import Spider

# 作者：周毓谦
# 时间：2018-12-6
# 用途：经济观察网

class Eeo(Spider):
	name = "经济观察网"
	newspaperlibraryid = "1045861539476668416"
	headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
	}

	def run(self):
		# 主函数，提取最新期刊数
		print("开始采集:经济观察报")
		url = 'http://www.eeo.com.cn/epaper/eeocover/jjgcb'
		response = requests.get(url, headers=self.headers)
		response.encoding = 'utf-8'
		html = etree.HTML(response.text)
		publishedtime = html.xpath('//div[contains(@class,"Arial")]/text()')[0]
		if self.a(publishedtime):
			return 0
		print("正在采集新闻")
		number = html.xpath('//div[contains(@class,"f12") and contains(@class,"fd") and contains(@class,"mt5")]/text()')
		number = re.search(r'\d{3,}', number[0]).group()
		new_list = self.paper_url(number)
		package = []
		tips = 0
		for new in new_list:
			tips += 1
			print("正在采集第%d篇" % (tips))
			new_text = self.paper_text(new)
			if new_text == None:
				continue
			package.append(new_text)
		super().uploaddata(publishedtime, package, self.newspaperlibraryid, False)
		print("采集成功:经济观察报-发行日期（" + publishedtime + "),文章数量（" + str(len(package)) + "）")
		return len(package)

	def supplement(self):
		number = input('请输入期数：(例：903)\n')
		publishedtime = input('请输入时间：(例：2018-12-24)\n')
		if self.a(publishedtime):
			return 0
		print("开始采集:经济观察报")
		new_list = self.paper_url(number)
		package = []
		tips = 0
		for new in new_list:
			tips += 1
			print("正在采集第%d篇" % (tips))
			new_text = self.paper_text(new)
			if new_text == None:
				continue
			package.append(new_text)
		super().uploaddata(publishedtime, package, self.newspaperlibraryid, False)
		print("采集成功:经济观察报-发行日期（" + publishedtime + "),文章数量（" + str(len(package)) + "）")
		return len(package)

	def a(self,publishedtime):
		api = self.api
		# 先获取token
		ret = api.gettoken()
		if not ret:
			return 0
		ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
		#如果为True,则说明已经存在
		if(ret["success"] and ret["result"]):
			print("采集失败：经济观察报-发行日期已经存在，报纸日期（" + publishedtime + ")")
			return True
		else:
			return False

	def paper_url(self,number):
		# 文章url列表爬取
		new_list = []
		for page in range(1, 100):
			data = {
				'app': 'epaper',
				'controller': 'text',
				'action': 'eeolist',
				'cid': '261',
				'qid': number,
				'page': page
			}
			url = 'http://app.eeo.com.cn/'
			try:
				response = requests.get(url, params=data, headers=self.headers)
			except:
				response = requests.get(url, params=data, headers=self.headers)  # 失败重试
			response.encoding = 'utf-8'
			html = etree.HTML(response.text)
			new_list1 = html.xpath('//ul[@class="new_list"]/li/a/@href')
			if new_list1:
				new_list.append(new_list1)
			else:
				break
		return reduce(operator.add,new_list)

	def paper_text(self,url, tips=0):
		# print('开始采集：', url)
		# 新闻内容提取
		try:
			response = requests.get(url, headers=self.headers)
		except:
			# 失败递归调用
			tips += 1
			if tips < 5:
				data = self.paper_text(url, tips)
				return data
			else:
				return None
		data = {}
		response.encoding = 'utf-8'
		html = etree.HTML(response.text)
		data['title'] = html.xpath('//div[@class="xd-b-b"]/h1/text()')[0]
		text_list = html.xpath('//div[@class="xx_boxsing"]/p/text()')
		text = ''
		# 数据清洗
		if not text_list:
			return
		if text_list[0].isdigit():
			del text_list[0]
			if not text_list:
				return
		# 抓取作者
		data['author'] = ''
		data['authorDescriptions'] = ''
		try:
			if html.xpath('//div[@class="zuozhe"]/a/text()'):
				data['author'] = '#'.join(html.xpath('//div[@class="zuozhe"]/a/text()')).replace('/文', '')
				data['authorDescriptions'] = ''.join(html.xpath('//div[@class="jianjie"]/text()')).replace('\n',';')
				if text_list[0] in data['author']:
					del text_list[0]
			elif len(re.sub('\s', '', text_list[0])) < 6:
				data['author'] = re.sub('\s+', '#', text_list[0].strip().replace('/文', ''))
				del text_list[0]
			elif html.xpath('//div[@class="xd-b-b"]/p/text()'):
				data['author'] = html.xpath('//div[@class="xd-b-b"]/p/text()')[0].strip()
				if text_list[0].strip() in data['author']:
					del text_list[0]
				data['author'] = re.sub('\s+', '#', data['author'].replace('/文', ''))
		except:
			pass
		# try:
		# 	authordes = re.match('\(\S*\)',text_list[-1]).group()
		# except:
		# 	authordes = ''
		# if authordes and re.sub('\(|\)','',authordes) not in data['authorDescriptions']:
		# 	data['authorDescriptions'] += authordes
		for i in text_list:
			text += '<p>' + i.strip() + '</p>'
		data['mainBody'] = text
		data['authorArea'] = ''
		data['subTitle'] = ''
		data['abstract'] = ''
		data['channel'] = ''
		data['page'] = ''
		data['images'] = ''
		data['imageDescriptions'] = ''
		return data