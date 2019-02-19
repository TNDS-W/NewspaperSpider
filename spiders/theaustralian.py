import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree
import re
import time
import datetime
from spiders.basespider import Spider
from selenium.webdriver.chrome.options import Options

class Theaustralian(Spider):
    Session = requests.session()
    newspaperlibraryid = "1045865018479869952"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'cookie':'visid_incap_1763466=Veyagll1SkaR3c6PMBYkYqopClwAAAAAQUIPAAAAAACWhFXZyap8U1o9ot4U+Nls; _ga=GA1.4.1821726351.1544169902; visid_incap_966147=AxMZiuY+QtqB2KrAlQcruJh4D1wAAAAAQUIPAAAAAACqsZUdCvkDOxhTOQUpjWDW; incap_ses_540_966147=BaMZd2GFcGlR3T2iP3h+B74hPFwAAAAAFO7w6vHByHtJPixN21M1xw==; incap_ses_796_966147=vURPOBNZNVHTGcIN9/YLC29KPVwAAAAAtMFh7RyCP4lLlyllVY9v9Q==; _HTML5_state=Id=1&sv=1&ed=F61DosVWAHV61bOMhykECMpqnB6rA01E144cQH9xao02mR7XEHQ0esg6V0GhHQo6iSDiygdKZbtM2ohm8H1uu7tAbkjpfyHJYrylBdIvwDTU+MeDVxWKNxtKOuk+19fDZz2cn+RX1B//CX8a3KB88a0yZMiMV1dRKFLWHSnONSQ=; incap_ses_796_1763466=EvCSLsH3fxPKcgYP9/YLC1nNPlwAAAAACt1Md7S8/2H3zCLanO3wUQ==; _gid=GA1.4.757678428.1547619675'
    }
    proxy = {'http': 'http://127.0.0.1:8124', 'https': 'https://127.0.0.1:8124'}
    follow = {}
    def login(self):
        try:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('log-level=3')
            browser = webdriver.Chrome(chrome_options=chrome_options)  # options=opt
            browser.get("https://myaccount.news.com.au/theaustralian/login")
            wait = WebDriverWait(browser, 30)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="email"]'))).send_keys("13574827001@163.com")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="password"]'))).send_keys("Yyy123456")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(@class,"go")]'))).click()
            browser.get('http://www.theaustralian.com.au/digitalprinteditions')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//p[@class="readnow"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="pageview ReplicaPageView"]')))
            cookie = browser.get_cookies()
            self.headers['cookie'] = ''
            for i in cookie:  # 添加cookie到CookieJar
                self.headers['cookie'] += i["name"] + '=' + i["value"] + ';'
            browser.close()
        except:
            browser.close()
            self.login()

    def paper_list(self,href):
        data = {'kind':'doc','href':href,'snippets':'true'}
        url = 'https://theaustralian.smedia.com.au/HTML5/get/prxml.ashx'
        i = 0
        while i < 4:
            try:
                response = self.Session.get(url,headers = self.headers,params=data,proxies = self.proxy)
                if response.status_code == 200:
                    break
                else:
                    i += 1
            except:
                i += 1
        text = response.json()
        id_list = []
        for i in text['pages']:
            for n in i['en']:
                if 'Ar' in n['cid']:
                    try:
                        if n['cid'] in id_list:
                            if n['cid'] in self.follow.keys():
                                self.follow[n['cid']].append(n['id'])
                            else:
                                self.follow[n['cid']] = [n['id']]
                        else:
                            id_list.append(n['cid'])
                    except:
                        continue
        return id_list

    def paper_text(self,Id,href):
        data = {'href':href,'id':Id}
        url = 'https://theaustralian.smedia.com.au/HTML5/get/article.ashx'
        package = {'title':'','subTitle':'','author':'','abstract':'','authorArea':'','authorDescriptions':'','channel':'','mainBody':'','page':'','images':'','imageDescriptions':'','cookies':'','referer':'',}
        i = 0
        while i<5:
            try:
                response = self.Session.get(url, headers=self.headers, params=data,proxies = self.proxy)
                if response.status_code == 200:
                    break
            except:
                i += 1
                continue
        html = etree.HTML(response.content)
        try:
            dic = eval(html.xpath('//div[@class="article"]/span/@data-json')[0])
        except:
            return
        package['channel'] = [dic['section']]
        try:
            package['page'] = [dic['label']]
        except:
            package['page'] = []
        if Id in self.follow.keys():
            for i in self.follow[Id]:
                data = {'href': href, 'id': i}
                try:
                    response = self.Session.get(url, headers=self.headers, params=data, proxies=self.proxy)
                except:
                    response = self.Session.get(url, headers=self.headers, params=data, proxies=self.proxy)
                html = etree.HTML(response.content)
                try:
                    dic = eval(html.xpath('//div[@class="article"]/span/@data-json')[0])
                except:
                    continue
                if dic['section'] not in package['channel']:
                    package['channel'].append(dic['section'])
                if dic['label'] not in package['page']:
                    package['page'].append(dic['label'])
        try:
            package['title'] = html.xpath('//h1[@class="headline"]/text()')[0]
        except:
            pass
        name = html.xpath('//address[@class="ByLine"]/p/text()')
        if name:
            package['author'] = name[0]
            try:
                package['authorDescriptions'] = name[1]
            except:
                pass
        package['author'] = re.sub('^(BY|By|by)\s+','',package['author'].strip())
        if re.search('\s(BY|By|by)\s',package['author']):
            package['author'] = re.sub('.*\s(BY|By|by)\s+', '', package['author'])
        package['author'] = re.sub('\s+(and|AND|And)\s+', '#', package['author'])
        img_url = []
        img_message = []
        for i in html.xpath('//div[@class="embed Picture"]'):
            img = eval(i.xpath('div[@class="placeholder img"]/@data-img-info')[0])
            img_url.append('https://theaustralian.smedia.com.au/HTML5/get/image.ashx?kind=' + img['type'] + '&href=' + img['doc'] + '&id=' + img['id'] + '&ext=' + img['ext'] + '&pr=' + img['id'])
            message = i.xpath('div[@class="Caption"]/p/text()')
            if message:
                img_message.append(';'.join(message))
            else:
                img_message.append('')
        package['images'] = '#'.join(img_url)
        package['imageDescriptions'] = '#'.join(img_message)
        try:
            text = html.xpath('//div[@class="Content"]')[0]
            text = etree.tostring(text).decode('utf-8', 'ignore')
            text = re.sub('<div.*?>|</div>', '', text).replace("&#8216;", "'").replace("\n", "").replace("&#8217;", "'")
            text = re.sub('<span.*?>|</span>', '', text)
            text = re.sub('<p.*?>\s*', '<p>', text).strip()
            package['mainBody'] = text
        except:
            pass
        package['channel'] = '#'.join(package['channel'])
        try:
            package['page'] = '#'.join(sorted(package['page'], key=lambda x: int(x)))
        except:
            package['page'] = '#'.join(package['page'])
        package['cookies'] = self.headers['cookie']
        if package['mainBody'] or package['author']:
            return package

    def date_get(self,date = ''):
        response = self.Session.get('https://theaustralian.smedia.com.au/HTML5/get/browse.ashx?kind=recent&pub=NCAUS&count=190',headers=self.headers,proxies = self.proxy)
        text = response.json()
        if date:
            for i in text['items']:
                if i['date'] == date:
                    print('已找到指定报纸')
                    return i['href']
            print('未找到指定报纸')
            return
        else:
            return text['items'][0]['date'],text['items'][0]['href']

    def run(self):
        print('开始采集：澳大利亚人报')
        self.login()
        print('登陆成功，开始采集数据')
        date,href = self.date_get()
        if self.a(date):
            return 0
        id_list = self.paper_list(href)
        if id_list == None:
            return 0
        package = []
        tips = 0
        for i in id_list:
            data = self.paper_text(i, href)
            if data:
                tips += 1
                print('正在采集第%s篇' % tips)
                package.append(data)
            else:
                continue
        super().uploaddata(date, package, self.newspaperlibraryid, True)
        print("采集成功:澳大利亚人民报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def supplement(self):
        # date = input('请输入日期：(例：2018-07-01)\n')
        # dates = datetime.datetime.now().date()
        dates = datetime.datetime.strptime('2018-06-30', '%Y-%m-%d').date()
        delta = datetime.timedelta(days=1)
        while True:
            dates += delta
            if dates >= datetime.datetime.now().date():
                break
            try:
                date = str(dates)
                print(date)
                if self.a(date):
                    continue
                    # return 0
                # self.login()
                print('登陆成功，开始采集数据')
                href = self.date_get(date)
                if not href:
                    continue
                    # return 0
                id_list = self.paper_list(href)
                if id_list == None:
                    continue
                    # return 0
                package = []
                tips = 0
                for i in id_list:
                    print(i)
                    data = self.paper_text(i, href)
                    if data:
                        tips += 1
                        print('正在采集第%s篇' % tips)
                        package.append(data)
                    else:
                        continue
                super().uploaddata(date, package, self.newspaperlibraryid, True)
                print("采集成功:澳大利亚人民报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
                # return len(package)
            except Exception as e:
                print(e)
                dates -= delta

    def a(self, publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：澳大利亚人民报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return True
        else:
            return False