import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from lxml import etree
import time
import re
from spiders.basespider import Spider
#zuo

class Wallstreet(Spider):
    Session = requests.session()
    newspaperlibraryid = "1049839508922564608"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        # 'cookie':'MACHINEID=32e7fa350abf4aabda11b9e7ffcf7fd4; bblogin=%7B%7B%20pSetup%20%7D%7D; __utmz=87361100.1544750227.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); editionfromcalling=; __utmc=87361100; TOKEN=02858e622db0a40d31e6504752765cc9_5c259ca0_66a06; udb_wallstreetjournal_EXTID=auth0%7C7628756c-65d9-4f72-80b5-76974168c4b6; firstThirdpartyRoute=null; __utma=87361100.1627321299.1544750227.1545968782.1545984763.10; __utmt=1; __utmb=87361100.1.10.1545984763; TAUID=420358; udb_wallstreetjournal_TAUID=420358; udb_wallstreetjournal_username=auth0%7C7628756c-65d9-4f72-80b5-76974168c4b6; username=auth0%7C7628756c-65d9-4f72-80b5-76974168c4b6'
    }
    tips = 0
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}
    def login(self,browser,i=1):
        try:
            browser.get("http://ereader.wsj.net/")
            wait = WebDriverWait(browser, 60)
            wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@id="mainframe"]')))
            browser.switch_to.frame("mainframe")
            wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@id="lightbox-iframe"]')))
            browser.switch_to.frame("lightbox-iframe")
            button = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"piccontainer")]')))
            button.click()
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="username"]'))).send_keys("13574827001@163.com")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="password"]'))).send_keys("Yyy123456789")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH,'//button[contains(@class,"basic-login-submit") and contains(@class,"solid-button")]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@id="mainframe"]')))
            cookie = browser.get_cookies()
            self.headers['cookie'] = ''
            for i in cookie:  # 添加cookie到CookieJar
                self.headers['cookie'] += i["name"] + '=' + i["value"] + ';'
            browser.close()
        except Exception as e:
            if i < 3:
                i += 1
                self.login(browser,i = i)
            else:
                browser.close()

    def paper_list(self,date):
        data = {
            'pSetup': 'wallstreetjournal',
            'useDB': 1,
            'action': 'sql-remote',
            'operationSQL': 'pagesAndArticlesByPageAndXmlId',
            'xmlId': 0,
            'section': 'The Wall Street Journal',
            'paper': 'wallstreetjournal',
            'issue': date,
            'editionForDB': 'thewallstreetjournal'}
        paper_list = []
        for i in range(100):
            text = self.get_data(i+1,data)
            if text['rows']:
                self.tips += 1
                print("正在采集第%d个板块" % (self.tips))
                paper_list.append(text['rows'])
            else:
                break
        return paper_list

    def get_data(self,page,data):
        url = 'http://ereader.wsj.net/eebrowser/ipad/html5.check.2350/ajax-request.php'
        data['pageId'] = page
        while True:
            try:
                response = self.Session.get(url, headers=self.headers, params=data, proxies=self.proxy)
                if response.status_code == 200:
                    return response.json()
                time.sleep(0.5)
            except:
                time.sleep(0.5)
                continue

    def paper_text(self,paper_list):
        package = []
        for i in paper_list:
            data = {
                'authorArea': '',
                'authorDescriptions': '',
                'subTitle': '',
                'abstract': '',
                'cookies': self.headers['cookie'],
                'referer': ''}
            if i ['type'] != 'Editorial':
                continue
            data['title'] = i['title']
            data['page'] = i['page']
            data['channel'] = i['section']
            html = etree.HTML(i['html'])
            images = html.xpath('//img/@src')
            imageDescriptions = []
            for i in html.xpath('//img'):
                paragraph = i.xpath('following-sibling::p[@class="paragraph"]/span/text()')
                if paragraph:
                    if paragraph[0] in imageDescriptions:
                        imageDescriptions.append('')
                    else:
                        imageDescriptions.append(paragraph[0])
                else:
                    imageDescriptions.append('')
            data['images']  = '#'.join(images)
            data['imageDescriptions'] = '#'.join(imageDescriptions)
            name = html.xpath('//p[@class="byline"]/span/text()')
            author = []
            if len(name) == 1:
                name = name[0].replace('|','').strip()
                name = re.sub('\s+(and|AND)\s+', '#', name)
                name = re.sub('\(%d\)', '', name)
                name = re.sub('^—', '', name)
                data['author'] = re.sub('^\s*B[Yy]\s+','',name).replace('—','')
                    # name[0].replace(' BY ','').replace(' AND ','#').replace(' By ','').replace('|','')
            elif len(name) > 1:
                for i in name:
                    i = i.replace('|','')
                    if re.search('^\s+in\s+|\s+(and|AND|And)',i): #' in ' in i or ' and' in i:
                        continue
                    else:
                        i = re.sub('^\s*B[Yy]\s+','',i)
                        i = re.sub('\(%d\)','',i)
                        i = re.sub(',$', '', i)
                        i = re.sub('^—', '', i)
                        i = re.sub('\s(AND|And|and)\s','#',i)
                        if i.strip():
                            author.append(i.replace(',','#'))
                data['author'] = '#'.join(author).replace('—','').replace('##','#')
            else:
                data['author'] = ''
            text = ''
            for i in html.xpath('//p[@class="abody"]'):
                if i.xpath('span/text()'):
                    text += etree.tostring(i).decode('utf-8', 'ignore')
                else:
                    continue
            data['mainBody'] = text
            package.append(data)
        return package

    def date_get(self,date = '',i=0):
        try:
            response = self.Session.get('http://ereader.wsj.net/eebrowser/ipad/html5.check.2350/ajax-request.php?pSetup=wallstreetjournal&useDB=1&action=issues&maxIssues=14&prefEdi=The%20Wall%20Street%20Journal',headers=self.headers,proxies=self.proxy)
        except:
            if i < 5:
                i += 1
                return self.date_get(date = date,i=i)
            else:
                return
        if date:
            for i in response.json():
                if i['issue'] == date.replace('-',''):
                    return date
            return 1
        else:
            d = response.json()[0]['issue']
            date = [d[:4],d[4:6],d[6:8]]
            return date
    def supplement(self):
        date = self.date_get(date = input('请输入日期：(例：2019-01-07)\n'))
        if not date:
            print('采集失败，网络错误')
            return 0
        elif date == 1:
            print('未找到指定报纸')
            return 0
        if self.a(date):
            return 0
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        self.login(browser)
        print('登陆成功，开始采集数据')
        paper = self.paper_list(date.replace('-',''))
        package = []
        for i in paper:
            data = self.paper_text(i)
            if data:
                package += data
            else:
                continue
        super().uploaddata(date, package, self.newspaperlibraryid, True)
        print("采集成功:华尔街日报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def run(self):
        print('开始采集:华尔街时报')
        date = self.date_get()
        if not date:
            print('采集失败，网络错误')
            return 0
        # cookie = self.headers['cookie']
        if self.a('-'.join(date)):
            return 0
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        self.login(browser)
        print('登陆成功，开始采集数据')
        paper = self.paper_list(''.join(date))
        package = []
        for i in paper:
            data = self.paper_text(i)
            if data:
                package += data
            else:
                continue
        super().uploaddata('-'.join(date), package, self.newspaperlibraryid, True)
        print("采集成功:华尔街日报-发行日期（" + '-'.join(date) + "),文章数量（" + str(len(package)) + "）")
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
            print("采集失败：华尔街日报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return True
        else:
            return False