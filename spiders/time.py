import requests
from lxml import etree
from lxml.html import tostring
import re
from spiders.basespider import Spider
import datetime

class Time(Spider):
    Session = requests.session()
    newspaperlibraryid = "1050641404616769536"
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}
    proxy = {'http': 'http://127.0.0.1:8124', 'https': 'https://127.0.0.1:8124'}
    def paper_list(self,n=0):
        while n<5:
            try:
                n += 1
                url = 'http://time.com/api/magazine/region/us/page/' + str(n) + '/'
                response = self.Session.get(url,headers = self.headers,proxies = self.proxy)
                if response.status_code == 200:
                    data = response.json()[0]
                    date = data['pubDate']
                    dates = datetime.datetime.strptime(date, '%Y-%m-%d')
                    if dates <= datetime.datetime.today():
                        break
                else:
                    n -= 1
                    continue
            except:
                n -= 1
        return date, data['articles']

    def paper_text2(self,href,data,n=0):
        while n < 5:
            try:
                n += 1
                response = self.Session.get(href,headers = self.headers,proxies = self.proxy) #,proxies = self.proxy
                if response.status_code == 200:
                    break
            except:
                continue
        html = etree.HTML(response.text)
        mainbody = html.xpath('//div[@id="longform-body"]//p|//div[@id="article-body"]//h2')
        text = ''
        for i in mainbody:
            n = tostring(i).decode('utf-8', 'ignore')
            if '<p>&#160;</p>' not in n:
                text += n.strip()
        text = re.sub('<em>|</em>', '', text)
        text = re.sub('<a.*?>|</a>', '', text)
        data['mainBody'] = re.sub('<strong>|</strong>', '', text)
        try:
            image = [html.xpath('//div[contains(@class,"partial") and contains(@class,"hero-media")]/img/@src')[0]]
        except:
            image = ['']
        try:
            descriptions = [html.xpath('//div[contains(@class,"partial") and contains(@class,"hero-media")]//div[@class="caption hero-caption align left"]//text()')[0].strip()]
        except:
            descriptions = ['']
        for img in html.xpath('//div[@class="image-wrapper"]/div'):
            image.append(img.xpath('@data-src')[0])
            try:
                descriptions.append(img.xpath('@data-title')[0])
            except:
                descriptions.append('')
        data['images'] = '#'.join(image)
        data['imageDescriptions'] = '#'.join(descriptions)
        return data

    def paper_text(self,data,n=0):
        paper_data = {'title':'','subTitle':'','author':'','abstract':'','authorArea':'','authorDescriptions':'','channel':'','mainBody':'','page':'','images':'','imageDescriptions':'','cookies':'','referer':'',}
        channel = [data['section']['name']]
        try:
            channel.append(data['tags'])
        except:
            pass
        paper_data['channel'] = '#'.join(channel)
        paper_data['author'] = data['authors'][0]['name'].replace(', ', '#').replace(',', '#')
        paper_data['title'] = data['friendly_title']
        try:
            paper_data['abstract'] = data['excerpt']
        except:
            pass
        htmls = etree.HTML(data['content'])
        for click in [i for i in htmls.xpath('//a')]:
            if re.match('http://time.com/longform',click.xpath('@href')[0]) and 'click here' in click.xpath('text()')[0]:
                return self.paper_text2(click.xpath('@href')[0],paper_data)
        while n < 5:
            try:
                n += 1
                response = self.Session.get(data['url'],headers = self.headers,proxies = self.proxy) #,proxies = self.proxy
                if response.status_code == 200:
                    break
            except:
                continue
        html = etree.HTML(response.text)
        mainbody = html.xpath('//div[@id="article-body"]//p|//div[@id="article-body"]//h2')
        text = ''
        for i in mainbody:
            n = tostring(i).decode('utf-8', 'ignore')
            if '<p>&#160;</p>' not in n:
                text += n.strip()
        text = re.sub('<em>|</em>','',text)
        text = re.sub('<a.*?>|</a>','',text)
        paper_data['mainBody'] = re.sub('<strong>|</strong>','',text)
        try:
            image = [html.xpath('//div[@class="image-and-burst"]//img/@src')[0]]
        except:
            image = ['']
        try:
            descriptions = [html.xpath('//div[@class="image-and-burst"]//img/@title')[0]]
        except:
            descriptions = ['']
        for img in html.xpath('//div[@class="image-wrapper"]/div'):
            image.append(img.xpath('@data-src')[0])
            try:
                descriptions.append(img.xpath('@data-title')[0])
            except:
                descriptions.append('')
        paper_data['images'] = '#'.join(image)
        paper_data['imageDescriptions'] = '#'.join(descriptions)
        return paper_data

    # def get_papar(self,date):
    #     year = date.split('-')[0]
    #     url = 'http://time.com/api/magazine/year/' + year + '/'
    #     response = self.Session.get(url, headers=self.headers, proxies=self.proxy)
    #
    #
    # def supplement(self):
    #     date = input('请输入日期')
    #     if self.a(date):
    #         print('采集失败：时代周刊-发行日期已经存在，报纸日期（' + date + ')')
    #         return 0
    #     data = self.get_papar(date)
    #     print('报纸日期：', date)
    #     package = []
    #     tips = 0
    #     for i in data:
    #         tips += 1
    #         print('正在抓取第' + str(tips) + '篇')
    #         paper = self.paper_text(i)
    #         if paper:
    #             package.append(paper)
    #     super().uploaddata(date, package, self.newspaperlibraryid, True)
    #     print("采集成功:时代周刊-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
    #     return len(package)

    def run(self):
        print('开始采集:时代周刊')
        date,data = self.paper_list()
        if not data:
            return 0
        date_time = datetime.datetime.strptime(date, '%Y-%m-%d')
        now_time = datetime.datetime.today()
        if self.a(date) or now_time < date_time :
            print("采集失败：时代周刊-发行日期已经存在/未到发行日期，报纸日期（" + date + ")")
            return 0
        package = []
        tips = 0
        for i in data:
            tips += 1
            print('正在抓取第' + str(tips) + '篇')
            paper = self.paper_text(i)
            if paper:
                package.append(paper)
        super().uploaddata(date, package, self.newspaperlibraryid, True)
        print("采集成功:时代周刊-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def get_paper(self,date):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        n = 0
        while n<100:
            try:
                n += 1
                url = 'http://time.com/api/magazine/region/us/page/' + str(n) + '/'
                response = self.Session.get(url,headers = self.headers,proxies = self.proxy)
                if response.status_code == 200:
                    data = response.json()[0]
                    pubDate = data['pubDate']
                    dates = datetime.datetime.strptime(pubDate, '%Y-%m-%d').date()
                    if dates == date:
                        print('已找到报纸')
                        return data['articles']
                    elif dates < date:
                        print('未找到报纸')
                        return
                else:
                    n -= 1
                    continue
            except:
                n -= 1

    def supplement(self):
        date = input('请输入日期：(例：2019-01-01)\n')
        if self.a(date):
            print("采集失败：时代周刊-发行日期已经存在，报纸日期（" + date + ")")
            return 0
        data = self.get_paper(date)
        package = []
        tips = 0
        for i in data:
            tips += 1
            print('正在抓取第' + str(tips) + '篇')
            paper = self.paper_text(i)
            if paper:
                package.append(paper)
        super().uploaddata(date, package, self.newspaperlibraryid, True)
        print("采集成功:时代周刊-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def a(self,publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为False,则说明已经存在
        if (ret["success"] and ret["result"]):
            return True
        else:
            return False
