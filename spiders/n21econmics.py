from selenium import webdriver
import requests
from lxml import etree
from spiders.basespider import Spider
import re
#
class N21econmics(Spider):
    newspaperlibraryid = '1045861163432148992'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

    #主方法
    def run(self):
        date,url,html = self.get_time()
        if self.a(date):
            # continue
            return 0
        package = self.paper_list(html, url)
        super().uploaddata(date, package, self.newspaperlibraryid, False)
        print("采集成功:悉尼先驱晨报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")

    #时间获取
    def get_time(self):
        browser = webdriver.Chrome()
        browser.get('http://epaper.21jingji.com')
        html = etree.HTML(browser.page_source)
        date = html.xpath('//div[@class="data"]/text()')[0].strip().replace('年','-').replace('日','')
        return date.replace('月','-'),'http://epaper.21jingji.com/html/' + date.replace('月','/') + '/',html

    #补录方法
    def supplement(self):
        date = input('请输入日期：(例如：2019-01-01)\n')
        url = 'http://epaper.21jingji.com/html/' + date.replace('-', '/').replace('/', '-', 1) + '/'
        if self.a(date):
            # continue
            return 0
        rsp = requests.get(url+'node_1.htm',headers = self.headers)
        rsp.encoding = 'utf-8'
        html = etree.HTML(rsp.text)
        if rsp.status_code == '404':
            print('未找到报纸，请检查日期')
            return
        package = self.paper_list(html,url)
        super().uploaddata(date, package, self.newspaperlibraryid,False)
        print("采集成功:悉尼先驱晨报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")

    #新闻链接获取
    def paper_list(self,html,url):
        news_list = html.xpath('//div[@class="news_list"]/ul') #获取新闻列表
        page_list = html.xpath('//div[@class="news_list"]/h5') #获取版面&频道列表
        package = []
        tips = 0
        for i in range(len(page_list)):
            page_channel = page_list[i].xpath('a[@id="pageLink"]/text()')[0]
            for n in news_list[i].xpath('li/a[@target="_blank"]/@href'):
                tips += 1
                print("开始采集第%d篇" % (tips))
                data = self.paper_get(page_channel, url + n)
                if data:
                    package.append(data)
        return package

    #新闻页面解析
    def paper_get(self,page_channel,url,i=0):
        page_channel = page_channel.split('：')
        page = page_channel[0]
        channel = page_channel[1]
        data = {'title':'','subTitle':'','author':'','abstract':'','authorArea':'','authorDescriptions':'','channel':channel,'mainBody':'','page':page,'images':'','imageDescriptions':'','cookies':'','referer':'',}
        while i < 5:
            try:
                rsp = requests.get(url,headers=self.headers)
                if rsp.status_code == 200:
                    break
                i += 1
            except:
                i += 1
        try:
            rsp.encoding = 'utf-8'
        except:
            print('网络错误请检查网络')
            return
        html = etree.HTML(rsp.text)
        try:
            data['title'] = html.xpath('//h1[@class="news_title"]/text()')[0]
        except:
            print('链接无法加载：',url)
            return
        if data['title'] == '广告':
            return
        body = html.xpath('//div[@id="news_text"]/p/text()')
        if body:
            while True:
                if body[0].strip():
                    break
                del body[0]
        author = html.xpath('//div[@class="news_author"]/text()')
        if author:
            data['author'] = author[0].replace(";", "#").strip()
            if body:
                author = data['author'].split('#')
                for a in author:
                    if re.sub('\s',' ',a) in re.sub('\s',' ',body[0]):
                        area = re.search('(\S+)报道', body[0].strip())
                        del body[0]
                        if area:
                            data['authorArea'] = area.group(1).replace('、', '#').replace('综合', '')
        elif body:
            author = body[0].strip()
            if re.search('^(本报|特约|特派)(记者|评论员)|报道$|\s实习(生|记者)\s|^21世纪\w*研究院|21世纪\w*研究院$',author) and len(author) < 50:
                del body[0]
                data['author'] = '#'.join(re.sub('^(本报|特约|特派)(记者|评论员)|\S+报道$|实习(生|记者)\s|^21世纪\w*研究院\w*|21世纪\w*研究院\w*$','',author).strip().split())
                area = re.search('(\S+)报道',author)
                if area:
                    data['authorArea'] = area.group(1).replace('、','#').replace('综合','')
        try:
            if re.search('^(导读|编者)',body[0].strip()):
                del body[0]
        except:
            pass
        data['mainBody'] = []
        for i in body:
            i = i.strip()
            if i:
                data['mainBody'].append('<p>' + i + '</p>')
        data['mainBody'] = ''.join(data['mainBody'])
        img = []
        for i in html.xpath('//div[@class="news_photo"]//img/@src'):
            img.append('http://epaper.21jingji.com/' + re.sub('(\.\./)+', '', i))
        data['images'] = '#'.join(img)
        print(data['images'])
        return data

    #查重
    def a(self, publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：悉尼先驱晨报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return True
        else:
            return False
