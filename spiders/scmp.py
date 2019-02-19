import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from lxml import etree
import re
import datetime
import time
from lxml.html import tostring
from spiders.basespider import Spider

class SouthChina(Spider):
    Session = requests.session()
    newspaperlibraryid = "1049906225992433664"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'cookie':'ga=GA1.3.414403430.1545094012; SID=b83a1941-5d75-4e65-be2c-05968000e2b8; html5pubguid=ce49a68e-e3e9-49b6-bac7-34f6b665e7be'
    }
    def login(self,i=1):
        try:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('log-level=3')
            browser = webdriver.Chrome(chrome_options=chrome_options)  # options=opt
            browser.get('https://customerservice.scmp.com/accounts/epaperLogin')
            wait = WebDriverWait(browser, 30)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="AccountUsername"]'))).send_keys("13574827001@163.com")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="AccountPassword"]'))).send_keys("Yyy123456")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@value="Login"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]'))).click()
            time.sleep(2)
            page = browser.page_source
            wait.until(EC.presence_of_element_located((By.XPATH,'//div[@id="ext-element-453"]')))
            cookie = browser.get_cookies()
            self.headers['cookie'] = ''
            for i in cookie:  # 添加cookie到CookieJar
                self.headers['cookie'] += i["name"] + '=' + i["value"] + ';'
            browser.close()
            return page
        except:
            if i < 4:
                i += 1
                browser.close()
                page, c = self.login()
                return page, c
            else:
                print('登陆失败，请检查网络')

    def paper_list(self,page,i=0):
        html = etree.HTML(page)
        script = html.xpath('//script/text()')[0].split(';')
        data = {}
        data['pubid'] = script[6].split('"')[-2]
        data['edid'] = script[8].split('"')[-2]
        data['lm'] = script[13].split()[-1]
        while i < 5:
            try:
                response = self.Session.get('https://edition.pagesuite-professional.co.uk/html5/reader/get_articles.aspx',params=data,headers = self.headers)
                break
            except:
                i += 1
                if i == 5:
                    print('采集失败，请检查网络')
                    return
                continue
        data_list = response.json()['articles']
        time = script[11].split('"')[-2].split('/')
        date = [time[2],time[1],time[0]]
        return data_list,'-'.join(date)

    def paper_text(self,data):
        package = {
        'title':data['headline'],
        'subTitle':data['subHeadline'],
        'page':data['pageNumber'],
        'images':[],
        'imageDescriptions':[],
        'authorDescriptions':'',
        'authorArea' : '',
        'abstract' : '',
        'cookies' : self.headers['cookie'],
        'referer' : '',
        'channel':''
        }
        authors = data['byline'].replace('<br />','').replace('<br>',' ').split()
        tips = ''
        for a in range(len(authors)):
            if authors[a] == 'and':
                authors[a] = '#'
            if authors[a] == 'in':
                tips = authors[a + 1:]
                authors = authors[:a]
                break
            if re.match('^\S*@\w*.com\S*', authors[a]):
                del authors[a]
        package['author'] = ' '.join(authors).replace(' # ', '#').replace(',','#')
        package['author'] = re.sub('(BY|by|By)\s+','',package['author'])
        for i in range(len(tips)):
            if re.match('^\S*@\w*.com\S*', tips[i]):
                package['authorArea'] += tips[i]
                del tips[i]
        package['authorArea'] = ' '.join(tips)
        # package['author'] = authors[0]
        # try:
        #     package['authorDescriptions'] = authors[1]
        # except:
        #     package['authorDescriptions'] = ''
        for i in data['images']:
            package['images'].append(i['url'])
            package['imageDescriptions'].append(i['caption'].replace('<br />', ''))
        package['images'] = '#'.join(package['images'])
        package['imageDescriptions'] = '#'.join(package['imageDescriptions'])
        html = etree.HTML(data['body'])
        try:
            channel = html.xpath('//body//text()')[0]
            text = tostring(html.xpath('//body')[0]).decode('utf-8', 'ignore').replace('</div>', '')
        except:
            text = ''
            channel = ''
        if channel.isupper():
            text.replace(channel,'')
            package['channel'] = channel
        text = re.sub('<div.*?>', '', text)
        mainBody = '<p>' + re.sub('<body.*?>|</body>', '', text).replace('<br><br>','</p><p>')
        mainBody = re.sub('<p>$','',mainBody)
        mainBody = re.sub('<br>$', '</p>', mainBody)
        mainBody = re.sub('^<p><p>', '<p>', mainBody)
        mainBody = re.sub('<p>\s*</p>$', '', mainBody)
        mainBody = re.sub('\n+$', '', mainBody)
        package['mainBody'] = re.sub('</p><br>$', '</p>', mainBody)
        if package['mainBody'] or package['author'] or package['images']:
            return package

    def run(self):
        print('开始采集:南华早报')
        page = self.login()
        print('登陆成功')
        data_list,date = self.paper_list(page)
        if self.a(date):
            return 0
        package = []
        tips = 0
        for i in data_list:
            tips += 1
            print("正在采集第%d篇" % (tips))
            data = self.paper_text(i)
            if data:
                package.append(data)
            else:
                continue
        package = sorted(package, key=lambda x: x['page'])
        super().uploaddata(date, package, self.newspaperlibraryid, True)
        print("采集成功:南华早报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def get_date(self,data,date,i=0):
        # try:
        response = self.Session.get('https://edition.pagesuite-professional.co.uk/html5/editionsdesktop_json.aspx',headers=self.headers, params=data)
        eid = {'pubname': '', 'edid': ''}
        for i in response.json()['editions']['edition']:
            if i['@name'] == date:
                eid['edid'] = i['@editionguid']
                break
        if eid['edid']:
            print('已找到指定报纸，开始获取数据')
        else:
            print('未找到指定报纸，请确认日期是否正确')
            return
        response = self.Session.get('https://edition.pagesuite-professional.co.uk/html5/reader/production/default.aspx',headers=self.headers, params=eid)
        html = etree.HTML(response.text)
        script = html.xpath('//script/text()')[0].split(';')
        data = {}
        data['pubid'] = script[6].split('"')[-2]
        data['edid'] = script[8].split('"')[-2]
        data['lm'] = script[13].split()[-1]
        response = self.Session.get('https://edition.pagesuite-professional.co.uk/html5/reader/get_articles.aspx', params=data,headers=self.headers)
        return response.json()['articles']
        # except:
        #     if i < 3:
        #         i += 1
        #     else:
        #         print('获取报纸失败，请检查网络')
        #         return
        #     return self.get_date(page,date,i=i)

    def supplement(self):
        # date = input('请输入日期：(例：2018-07-01)\n')
        dates = datetime.datetime.now().date()
        delta = datetime.timedelta(days=1)
        while True:
            dates -= delta
            if dates < datetime.datetime.strptime('2019-01-01', '%Y-%m-%d').date():
                break
            try:
                date = str(dates)
                if self.a(date):
                    # return 0
                    continue
                # page = self.login()
                # html = etree.HTML(page)
                # script = html.xpath('//script/text()')[0].split(';')
                # data = {'maxnumber': '999999', 'version': 'production'}
                # data['publicationguid'] = script[6].split('"')[-2]
                # data['edid'] = script[8].split('"')[-2]
                # data['lm'] = script[13].split()[-1]
                data = {'maxnumber': '999999', 'version': 'production'}
                data['publicationguid'] = "ce49a68e-e3e9-49b6-bac7-34f6b665e7be"
                # data['edid'] = "bfa1f122-350c-4535-bce3-e55371c3b7c9"
                data['lm'] = '63683288091147'
                # print('登陆成功')
                data_list = self.get_date(data,'/'.join([i for i in reversed(date.split('-'))]))
                if not data_list:
                    # return 0
                    continue
                package = []
                tips = 0
                for i in data_list:
                    tips += 1
                    print("正在采集第%d篇" % (tips))
                    data = self.paper_text(i)
                    if data:
                        package.append(data)
                    else:
                        continue
                package = sorted(package, key=lambda x: x['page'])
                super().uploaddata(date, package, self.newspaperlibraryid, True)
                print("采集成功:南华早报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
                # return len(package)
            except:
                dates += delta

    def a(self,publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：南华早报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return True
        else:
            return False