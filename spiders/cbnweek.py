import requests
from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime
from spiders.basespider import Spider


# 作者：周毓谦
# 时间：2018-12-6
# 用途：测试1

class Cbnweek(Spider):
    Session = requests.session()
    name = "第一财经周刊"
    newspaperlibraryid = "1045861372144910336"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
    }

    def run(self):
        print('开始采集：第一财经周刊')
        self.login()  # 登陆获取session
        url_list, publishedtime = self.new_list()  # 解析获取数据
        if self.a(publishedtime):
            return 0
        # api = DamsApi('zyq', '123456')
        package = []
        tips = 0
        print('开始采集新闻……')
        for url in url_list:
            tips += 1
            print("-->采集第%d篇文章<--" % (tips))
            url = 'https://www.cbnweek.com' + url
            news_data = self.new_text(url)
            package.append(news_data)
        print("一共采集" + str(tips) + "篇文章")
        super().uploaddata(publishedtime, package, self.newspaperlibraryid, requireAgent=False)
        print("采集成功:第一财经周刊-发行日期（" + str(publishedtime) + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def supplement(self):
        url = input('请输入网页链接：(例：https://www.cbnweek.com/magazine/526)\n')
        print('开始采集：第一财经周刊')
        self.login()  # 登陆获取session
        url_list, publishedtime = self.new_list2(url)  # 解析获取数据
        if self.a(publishedtime):
            return 0
        # api = DamsApi('zyq', '123456')
        package = []
        tips = 0
        print('开始采集新闻……')
        for url in url_list:
            tips += 1
            print("-->采集第%d篇文章<--" % (tips))
            url = 'https://www.cbnweek.com' + url
            news_data = self.new_text(url)
            package.append(news_data)
        print("一共采集" + str(tips) + "篇文章")
        super().uploaddata(publishedtime, package, self.newspaperlibraryid, requireAgent=False)
        print("采集成功:第一财经周刊-发行日期（" + str(publishedtime) + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def a(self, publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：第一财经周刊-发行日期已经存在，报纸日期（" + str(publishedtime) + ")")
            return True
        else:
            return False

    def login(self):
        data = {'password': 'Yyy123456', 'username': '13574827001'}
        url = 'https://www.cbnweek.com/account/login?next=%2Fread'
        self.Session.post(url, headers=self.headers, data=data)

    def new_list2(self, url):
        response = self.Session.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        html = etree.HTML(response.text)
        publishedtime = html.xpath('//div[@class="text-muted"]/text()')[-1].replace('.', '-')
        url_list = html.xpath('//a[contains(@class,"article-item-image") and contains(@class,"img-wrap")]/@href')
        return url_list, publishedtime

    def new_list(self):
        response = self.Session.get('https://www.cbnweek.com/read', headers=self.headers)
        response.encoding = 'utf-8'
        html = etree.HTML(response.text)
        top_url = html.xpath('//a[@class="top-cover-image"]/@href')
        time = html.xpath('//div[@class="magazine-date"]/text()')[0]
        publishedtime = str(time).replace('.', '-').replace(' ', '').replace("\n", "")
        url = 'https://www.cbnweek.com' + top_url[0]
        response = self.Session.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        html = etree.HTML(response.text)
        url_list = html.xpath('//a[contains(@class,"article-item-image") and contains(@class,"img-wrap")]/@href')
        return url_list, publishedtime

    def new_text(self, url):
        # print('开始采集：', url)
        data = {}
        response = self.Session.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        html = etree.HTML(response.text)
        data['title'] = html.xpath('//div[@class="article-full-content "]/h1/text()')[0]
        data['author'] = '#'.join(html.xpath('//div[contains(@class,"article-author-name")]/text()'))
        try:
            data['abstract'] = \
            html.xpath('//div[contains(@class,"article-summary") and contains(@class,"text-muted")]/text()')[0]
        except:
            data['abstract'] = ''
        soup = BeautifulSoup(response.text, 'lxml')
        text_list = soup.select('.article-content p')
        text = ''
        for i in text_list:
            text += str(i)
        data['mainBody'] = text
        img_list = [html.xpath('//header//img/@src')[0]]
        introduce_list = ['封面']
        for img in html.xpath('//figure'):
            img_list.append(img.xpath('img/@src')[0])
            try:
                introduce_list.append(img.xpath('figcaption/text()')[0])
            except:
                introduce_list.append('')
        data['images'] = '#'.join(img_list)
        data['imageDescriptions'] = '#'.join(introduce_list)
        data['subTitle'] = ''
        data['authorArea'] = ''
        data['authorDescriptions'] = ''
        data['channel'] = ''
        data['page'] = ''
        data['cookies'] = ''
        data['referer'] = ''
        return data
