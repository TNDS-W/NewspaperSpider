import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from lxml import etree
from lxml.html import tostring
import re
import time
import datetime
from spiders.basespider import Spider
from selenium.webdriver.chrome.options import Options
#
class Smh(Spider):
    Session = requests.session()
    newspaperlibraryid = "1049098394242383872"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'cookie':'visid_incap_1763466=Veyagll1SkaR3c6PMBYkYqopClwAAAAAQUIPAAAAAACWhFXZyap8U1o9ot4U+Nls; visid_incap_966147=AxMZiuY+QtqB2KrAlQcruJh4D1wAAAAAQUIPAAAAAACqsZUdCvkDOxhTOQUpjWDW; _ga=GA1.4.1754351629.1544517787; _gid=GA1.4.925426486.1550193172; _smh_state=Id=ef4b9370790bb0e3be68bef94e4b35d527533398b4939dfaad316adaeb68ca47&sv=1&ed=nnqAVxAqGrSiFRHxy6jhUB1irJoUKxFws9QxyvqLoAGY+HEBJVEXhkvw01bB0rFUXi8uKmAQ4oBLLaGWl0roZpkr8lzyikC2FRXELgH/BAfN2JbrxEf0Gqg0vLGk8uzNz973Nq6K3/WQRKkJ8MtfyLvhchmxVskWpPKEkIL3re0=; incap_ses_1206_966147=7/a5TTu5eUhE7cKQpZK8ELRgZ1wAAAAAFPxOfgKUTNtuFoKYgMia7g==; _gat=1'
    }
    proxy = {'http': 'http://127.0.0.1:8124', 'https': 'https://127.0.0.1:8124'}
    follow = {}
    def login(self,i=1):
        # browser = webdriver.Chrome()
        try:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('log-level=3')
            browser = webdriver.Chrome(chrome_options=chrome_options) #chrome_options=chrome_options
            browser.get("https://www.smh.com.au/")
            wait = WebDriverWait(browser, 30)
            wait.until(EC.element_to_be_clickable((By.XPATH,'//button[@class="_3S9ou"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH,'//input[@id="login-email-address"]'))).send_keys("13574827001@163.com")
            time.sleep(0.2)
            wait.until(EC.presence_of_element_located((By.XPATH,'//input[@id="login-password"]'))).send_keys("Yyy123456")
            time.sleep(0.2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="login-password"]'))).send_keys(Keys.ENTER)
            time.sleep(2)
            try:
                browser.find_element_by_xpath('//input[@id="login-password"]').send_keys(Keys.ENTER)
            except:
                pass
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="myAccountMenuButton"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, '//ul[@id="myAccountMenu"]/li/a'))).click()
            try:
                browser.find_element_by_xpath('//ul[@id="myAccountMenu"]/li/a').click()
            except:
                pass
            try:
                wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="layer content-layer"]')))
            except:
                pass
            cookie = browser.get_cookies()
            self.headers['cookie'] = ''
            for i in cookie:  # 添加cookie到CookieJar
                self.headers['cookie'] += i["name"] + '=' + i["value"] + ';'
            browser.close()
        except:
            browser.close()
            if i<4:
                i += 1
                return self.login(i = i)
            else:
                print('登陆失败，请检查网络')

    def paper_list(self,href):
        data = {'kind':'doc','href':href}
        url = 'http://todayspaper.smedia.com.au/smh/get/prxml.ashx'
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

    def paper_text(self,id,href):
        data = {'href':href,'id':id}
        url = 'http://todayspaper.smedia.com.au/smh/get/article.ashx'
        package = {'title':'','subTitle':'','author':'','abstract':'','authorArea':'','authorDescriptions':'','channel':'','mainBody':'','page':'','images':'','imageDescriptions':'','cookies':'','referer':'',}
        i = 0
        while True:
            try:
                response = self.Session.get(url, headers=self.headers, params=data,proxies = self.proxy)
                if response.status_code == 200:
                    break
            except:
                i += 1
                if i > 3:
                    return
        html = etree.HTML(response.content)
        try:
            dic = eval(html.xpath('//div[@class="article"]/span/@data-json')[0])
        except:
            return
        package['channel'] = [dic['section']]
        try:
            package['page'] = [dic['label']]
        except:
            pass
        if id in self.follow.keys():
            for i in self.follow[id]:
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
                try:
                    if dic['label'] not in package['page']:
                        package['page'].append(dic['label'])
                except:
                    pass
        name = html.xpath('//address[@class="ByLine"]/p//text()')
        package['title'] = html.xpath('//h1[@class="headline"]/text()')
        img_url = []
        img_message = []
        for i in html.xpath('//div[@class="embed Picture"]'):
            img = eval(i.xpath('div[@class="placeholder img"]/@data-img-info')[0])
            img_url.append('http://todayspaper.smedia.com.au/smh/get/image.ashx?kind=' + img['type'] + '&href=' + img['doc'] + '&id=' + img['id'] + '&ext=' + img['ext'] + '&pr=' + img['id'])
            message = i.xpath('div[@class="Caption"]/p/text()')
            if message:
                img_message.append(';'.join(message))
            else:
                img_message.append('')
        package['images'] = '#'.join(img_url)
        package['imageDescriptions'] = '#'.join(img_message)
        mainbody = html.xpath('//div[@class="Content"]/p')
        if name:
            if len(name) > 1:
                if name[0] == 'EXCLUSIVE' or name[0] == 'By':
                    package['author'] =name[1]
                else:
                    package['author'] = name[0]
                    try:
                        package['authorDescriptions'] = name[-1]
                    except:
                        pass
            else:
                package['author'] = name[0]
        package['author'] = re.sub('^(BY|By|by)\s+','',package['author'].strip())
        if re.search('\s(BY|By|by)\s',package['author']):
            package['author'] = re.sub('.*\s(BY|By|by)\s+', '', package['author'])
        package['author'] = re.sub('\s+(and|AND|And)\s+', '#', package['author'])
        text = ''
        for i in mainbody:
            n = tostring(i).decode('utf-8', 'ignore').replace("&#8216;", "'").replace("\n", "").replace("&#8217;", "'")
            n = re.sub('<span.*?>|</span>', '', n)
            n = re.sub('<p.*?>\s*', '<p>', n).strip()
            text += n
        package['mainBody'] = text
        package['channel'] = '#'.join(package['channel'])
        try:
            package['page'] = '#'.join(sorted(package['page'], key=lambda x: int(x)))
        except:
            package['page'] = '#'.join(package['page'])
        package['cookies'] = self.headers['cookie']
        if text or package['images']:
            return package

    def date_get(self,i = 0):
        while i < 5:
            try:
                response = self.Session.get('http://todayspaper.smedia.com.au/smh/get/browse.ashx?kind=recent&count=180',headers=self.headers,proxies = self.proxy)
                if response.status_code == 200:
                    text = response.json()
                    break
                i += 1
            except:
                i += 1
                if i == 5:
                    print('cookie无效，正在重新登陆')
                    self.login()
                    return self.date_get()
        return text['items'][0]['date'],text['items'][0]['href']

    def run(self):
        print('开始采集：悉尼先驱晨报')
        self.login()
        print('登陆成功')
        date,href = self.date_get()
        if self.a(date):
            return 0
        paper_list = self.paper_list(href)
        if paper_list == None:
            return 0
        tips = 0
        package = []
        for i in paper_list:
            tips += 1
            print("开始采集第%d篇" % (tips))
            data = self.paper_text(i, href)
            if data:
                package.append(data)
            else:
                continue
        super().uploaddata(date, package, self.newspaperlibraryid, True)
        print("采集成功:悉尼先驱晨报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def get_paper(self,date):
        try:
            response = self.Session.get('http://todayspaper.smedia.com.au/smh/get/browse.ashx?kind=recent&count=200',headers=self.headers,proxies = self.proxy)
            text = response.json()
        except:
            print('cookie无效，正在重新登陆')
            self.login()
            return self.date_get()
        for i in text['items']:
            if i['date'] == date:
                return i['href']
        print('未找到指定报纸')
        return

    def supplement(self):
        # date = input('请输入日期：(例：2018-07-01)\n')
        dates = datetime.datetime.now().date()
        delta = datetime.timedelta(days=1)
        while True:
            dates -= delta
            # try:
            date = str(dates)
            print(date)
            if self.a(date):
                continue
                # return 0
            # self.login()
            print('登陆成功')
            href = self.get_paper(date)
            if not href:
                continue
                # return 0
            paper_list = self.paper_list(href)
            if paper_list == None:
                continue
                # return 0
            tips = 0
            package = []
            for i in paper_list:
                tips += 1
                print("正在采集第%d篇" % (tips))
                data = self.paper_text(i, href)
                if data:
                    package.append(data)
                else:
                    continue
            super().uploaddata(date, package, self.newspaperlibraryid, True)
            print("采集成功:悉尼先驱晨报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
            # return len(package)
            # except:
            #     dates += delta
            if dates < datetime.datetime.strptime('2018-07-22', '%Y-%m-%d').date():
                break

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