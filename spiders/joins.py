import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from lxml import etree
import time
import re
import datetime
from spiders.basespider import Spider
#
class JoongAng(Spider):
    newspaperlibraryid = '1055631968592461824'
    Session = requests.session()
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'cookie':'_ga=GA1.2.950144042.1546043731; PCID=15501974786545621510690; _gid=GA1.2.1579817892.1550197479; join_ref=http%3A//www.joins.com/Event/BugsMusicPkg.aspx%3Fwhere%3Dpc_visual_show; _ja_v2_i=15501974786545621510690; _ja_v2_in=1550197478654562151069057247368210::https://www.joins.com/Event/BugsMusicPkg.aspx?where=pc_visual_show::0::0; SSOInfo=F7D58FADF296D12F305B0E7E1362595C751E6F7DEE55F704267ABD24CC066CDACE59CF29FB12A3075241EAF140B37D8FD24FA4F03B417EBF967DF084B52AB80338F5DAAC6CD29FDC9B7C6A0CB115F4FD500867DB4DB84D8A12EADEAF67392A36D8A1B0BE2616A7EF6A5BB63232876B7F6A6E38D2C7970174AABC81797D0244A464A6D5A0E3F33AF0805F44AE43938D3BBB81A6EE18D3094A36A999913382E596DC174BA6163F5B5D; MemArray=MemID=lrover000&MemName=%3F%u5A01&MemType=n0003&MemStatus=m0001&ValidLogin=True&LoginStatus=True&adult=N&Myselfcfm=Y; Joins_ValidLogin=True; Joins_LoginStatus=True; Joins_MemName=%3F%u5A01; Joins_MemID=lrover000; _gat=1'
    }
    def login(self):
        try:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('log-level=3')
            browser = webdriver.Chrome(chrome_options=chrome_options)
            wait = WebDriverWait(browser, 30)
            browser.get("https://my.joins.com/login/?TargetURL=http://www.joins.com/Media/List.aspx?mseq=11")
            browser.find_element_by_id('txtId').send_keys('lrover000')
            browser.find_element_by_id('txtPasswd').send_keys('zhaowei0000')
            browser.find_element_by_xpath('//input[@class="comm_btn login_btn"]').click()
            a = wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="btn_view"]')))
            result = re.search('\d+,\d+', a.get_attribute('onclick')).group()
            # a.click()
            # time.sleep(10)
            cookie = browser.get_cookies()
            for i in cookie:  # 添加cookie到CookieJar
                self.headers['cookie'] += i["name"] + '=' + i["value"] + ';'
            browser.close()
            return result
        except:
            browser.close()

    def paper_list(self,result):
        data = {
            'CImg': 'Y',
            'CPdf': 'N',
            'CArt': 'Y',
            'CTum': 'N',
            'pseq': result[0],
            'ddiv': 'P'
            }
        self.Session.get('https://jsapi.joins.com/W/C/PubCont.aspx',headers = self.headers,params=data)
        time.sleep(3)
        response = self.Session.get('https://jsapi.joins.com/W/C/PubCont.aspx',headers = self.headers,params=data)
        data = response.json()['rt']
        date = data['pdt']
        paper_list = {}
        for i in data['jList']:
            paper_list[i['no']] = []
            for n in i['arts']:
                paper_list[i['no']].append(n['tid'])
        return date,paper_list

    def paper_text(self,key,val,result,error = 0):
        data = {'view':'p','mseq': result[1],'pseq': result[0],'tid': val}
        package = {'title': '', 'subTitle': '', 'author': '', 'abstract': '', 'authorArea': '', 'authorDescriptions': '','channel': '', 'mainBody': '', 'page': key, 'images': [], 'imageDescriptions': [], 'cookies': self.headers['cookie'],'referer': '', }
        while error < 5:
            try:
                response = self.Session.get('https://www.joins.com/V2/A/DetailView.aspx',headers = self.headers,params=data)
                if response.status_code == 200:
                    break
                else:
                    error += 1
            except:
                error += 1
                continue
        html = etree.HTML(response.text)
        package['title'] = html.xpath('//h2[@class="subject"]//text()')[0]
        try:
            package['subTitle'] = html.xpath('//div[@class="ab_sub_headingline"]//text()')[0]
        except:
            pass
        for i in html.xpath('//div[@class="image"]//img'):
            package['images'].append(i.xpath('@src')[0])
            package['imageDescriptions'].append(i.xpath('@alt')[0])
        package['images'] = '#'.join(package['images'])
        package['imageDescriptions'] = '#'.join(package['imageDescriptions'])
        main = html.xpath('//div[@id="article_content"]/font')
        if main:
            for i in reversed(range(len(main))):
                email = re.search('[a-zA-Z.]+@[a-zA-Z.]+', main[i].xpath('text()')[0])
                if email:
                    package['author'] = re.sub('[a-zA-Z.]+@[a-zA-Z.]+', '', main[i].xpath('text()')[0]).replace('기자','').replace('·','#').strip()
                    # package['authorDescriptions'] = email.group().strip()
                    del main[i]
                    break
                else:
                    continue
            package['mainBody'] = main
        else:
            main = html.xpath('//div[@id="article_content"]/text()')
            for i in reversed(range(len(main))):
                email = re.search('[a-zA-Z.]+@[a-zA-Z.]+', main[i])
                if email:
                    if '=' in main[i]:
                        authors = []
                        for n in main[i].split(','):
                            author = re.search('=\s*(\w+)', n)
                            if author:
                                authors.append(author.group(1))
                        package['author'] = '#'.join(authors)
                    else:
                        author = re.sub('[a-zA-Z.]+@[a-zA-Z.]+', '', main[i]).replace('기자','').replace('·','#').replace('골프팀장','').strip()
                        if author:
                            package['author'] = author.split()[0]
                        # package['authorDescriptions'] = email.group().strip()
                    del main[i]
                    break
                else:
                    continue
        if not package['author'] and main:
            tips = len(main)
            if tips > 3:
                for i in range(-1, -4, -1):
                    if '.' in main[i] or ',' in main[i] or '"' in main[i] or '◆' in main[i] or '▶' in main[i]:
                        continue
                    elif len(main[i]) < 40 and len(main[i].strip()) > 2:
                        package['author'] = main[i].strip().split()
            else:
                for i in reversed(range(tips)):
                    if '.' in main[i] or ',' in main[i] or '"' in main[i] or '◆' in main[i] or '▶' in main[i]:
                        continue
                    elif len(main[i]) < 40 and len(main[i].strip()) > 2:
                        package['author'] = main[i].strip().split()
            if package['author']:
                package['author'] = package['author'][0]
        for i in main:
            i = i.strip()
            if i:
                package['mainBody'] += '<p>' + i + '</p>'
        return package

    def supplement(self):
        # date = input('请输入日期：(例如：2019-01-07)\n')
        datex = datetime.datetime.now().date()
        delta = datetime.timedelta(days=1)
        while True:
            datex -= delta
            date = str(datex)
            if self.a(date):
                # return 0
                continue
            data = {'mseq': '11', 'pgs': '30', 'pyn': 'y'}
            rsp = self.Session.post('https://www.joins.com/Media/PubList.aspx',headers = self.headers,data = data)
            html = etree.HTML(rsp.text)
            tips = 1
            for i in html.xpath('//li'):
                dates = re.sub('\(.*\)','',i.xpath('strong[contains(@class,"media_name")]/span/text()')[0]).replace('.','-')
                if dates == date:
                    print('已找到指定报纸')
                    result = i.xpath('span//a[@class="btn_view"]/@onclick')[0]
                    result = re.search('(\d+),\s*(\d+)',result).group().split(',')
                    tips = 0
            if tips:
                print('未找到指定报纸')
                # return 0
                continue
            # ccc = self.login().split(',')
            dates,data_list = self.paper_list(result)
            package = []
            tips = 0
            for key, values in data_list.items():
                for val in values:
                    tips += 1
                    print('正在采集第%s篇' % tips)
                    data = self.paper_text(key, val, result)
                    if data:
                        package.append(data)
            super().uploaddata(date, package, self.newspaperlibraryid, True)
            print("采集成功:中央日报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
            # return len(package)

    def run(self,):
        result = self.login().split(',')
        date,data_list = self.paper_list(result)
        if self.a(date):
            return 0
        package = []
        tips = 0
        for key,values in data_list.items():
            for val in values:
                tips += 1
                print('正在采集第%s篇'%tips)
                data = self.paper_text(key,val,result)
                if data:
                    package.append(data)
        super().uploaddata(date, package, self.newspaperlibraryid, True)
        print("采集成功:中央日报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def a(self,publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：中央日报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return True
        else:
            return False