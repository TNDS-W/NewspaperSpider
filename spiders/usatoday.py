import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree
import time
import re
import json
from spiders.basespider import Spider
from selenium.webdriver.chrome.options import Options

class Usatoday(Spider):
    Session = requests.session()
    newspaperlibraryid = "1049871921027481600"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        'cookie':'_ga=GA1.2.494576664.1544595754; _ga=GA1.3.494576664.1544595754; qsp-carrier=eyJvblN1Y2Nlc3NSZWRpcmVjdFVSTCI6ICJodHRwczovL2FjY291bnQudXNhdG9kYXkuY29tLyJ9; AMCV_CF4957F555EE9B727F000101%40AdobeOrg=1099438348%7CMCMID%7C00173098424439033960489486859049767466%7CMCAAMLH-1545204700%7C7%7CMCAAMB-1545204874%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCCIDH%7C1981800231%7CMCOPTOUT-1544607100s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.1.0; gup_anonid=25a6178a-fde1-11e8-992b-06248512b99e; utag_main=v_id:0167a114c855000a63ac9c8a37360306e002d06600bd0$_sn:2$_ss:0$_st:1544602689776$dc_visit:2$_pn:7%3Bexp-session$ses_id:1544599859129%3Bexp-session$dc_event:4%3Bexp-session$dc_region:eu-central-1%3Bexp-session; _USAToday_state=Id=13574827001@163.com&sv=0&ed=eKSdWPw6IJi4E9MBEASu7MmCP/wkf0y5Kr53JwJ/HhhKswdbXi8mhp5aJl3caDqES82EKTPP6O/sS8se3T4xsn+Bh68+1AlXH3/+nCgyU66035Y9P4zHIBitFjr4tWxtqvyqn7sN1kwYW70Gkvmd04mWTrBtIrE+RDtd0EukhF4=&pu=0; _gid=GA1.3.1695192140.1547797686'
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
            browser.get("http://ee.usatoday.com/Subscribers/Default.aspx")
            wait = WebDriverWait(browser, 30)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="formAuth:textEmail"]'))).send_keys("13574827001@163.com")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="formAuth:secretPass"]'))).send_keys("Yyy123456")
            time.sleep(0.5)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="formAuth:loginButton"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="image-layer"]')))
            cookie = browser.get_cookies()
            self.headers['cookie'] = ''
            for i in cookie:  # 添加cookie到CookieJar
                self.headers['cookie'] += i["name"] + '=' + i["value"] + ';'
            browser.close()
        except:
            browser.close()
            self.login()

    def paper_list(self,href):
        data = {'kind':'doc','href':href}
        url = 'http://ee.usatoday.com/Subscribers/get/prxml.ashx'
        response = self.Session.get(url,headers = self.headers,params=data,proxies = self.proxy)
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

    def paper_text(self,Id,href,i=0):
        data = {'href':href,'id':Id}
        url = 'http://ee.usatoday.com/Subscribers/get/article.ashx'
        package = {'title':'','subTitle':'','author':'','abstract':'','authorArea':'','authorDescriptions':'','channel':'','mainBody':'','page':'','images':'','imageDescriptions':'','cookies':'','referer':'',}
        while i < 5:
            try:
                response = self.Session.get(url, headers=self.headers, params=data,proxies = self.proxy)
                if response.status_code == 200:
                    break
            except:
                i += 1
                if i == 5:
                    print('采集失败',Id)
                    return
        html = etree.HTML(response.content)
        try:
            dic = eval(html.xpath('//div[@class="article"]/span/@data-json')[0])
        except:
            return
        package['channel'] = dic['section']
        package['page'] = [dic['label']]
        try:
            package['title'] = html.xpath('//h1[@class="headline"]//text()')[0]
        except:
            pass
        subTitle = html.xpath('//h1[@class="drop-head"]//text()')
        if subTitle:
            subTitle = subTitle[0]
        name = html.xpath('//address[@class="ByLine"]/p//text()')
        if name:
            package['author'] = name[0].replace(' and ','#').replace('USA TODAY','')
        img_url = []
        img_message = []
        for i in html.xpath('//div[@class="embed Picture"]'):
            img = eval(i.xpath('div[@class="placeholder img"]/@data-img-info')[0])
            img_url.append('http://ee.usatoday.com/Subscribers/get/image.ashx?kind=' + img['type'] + '&href=' + img['doc'] + '&id=' + img['id'] + '&ext=' + img['ext'] + '&pr=' + img['id'])
            message = i.xpath('div[@class="Caption"]/p//text()')
            if message:
                img_message.append(';'.join(message))
            else:
                img_message.append('')
        package['images'] = '#'.join(img_url)
        package['imageDescriptions'] = '#'.join(img_message)
        main = []
        for i in html.xpath('//div[@class="Content"]/*'):
            text = etree.tostring(i).decode('utf-8', 'ignore').replace("\n", "").replace("&#13;","")  # .replace('&#8220;','"').replace('&#13;','"').replace('&#8217;',"'")
            text = re.sub('<div.*?>|</div>', '', text)
            text = re.sub('<span.*?>|</span>', '', text)
            text = re.sub('<p.*?>\s*', '<p>', text).strip()
            if text:
                main.append(text)
        package['mainBody'] = ''.join(main)
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
                    package['channel'] += '#' + dic['section']
                package['page'].append(dic['label'])
        package['page'] = '#'.join(package['page'])
        package['cookies'] = self.headers['cookie']
        if package['mainBody'] or package['images'] or package['author']:
            return package

    def date_get(self,date = ''):
        i = 0
        while i < 5:
            try:
                response = self.Session.get('http://ee.usatoday.com/Subscribers/get/browse.ashx?kind=recent&count=180',headers=self.headers,proxies = self.proxy)
                if response.status_code == 200:
                    break
            except:
                i += 1
                if i == 5:
                    print('采集失败，请检查网络')
                    return
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

    def supplement(self):
        date = input('请输入日期：(例：2018-07-01)\n')
        if self.a(date):
            return 0
        # self.login()
        print('登陆成功，开始采集数据')
        href = self.date_get(date)
        if not href:
            return 0
        id_list  = self.paper_list(href)
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
        print("采集成功:今日美国-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def run(self):
        print('开始采集：今日美国')
        self.login()
        date,href = self.date_get()
        if self.a(date):
            return 0
        print('登陆成功，开始采集数据')
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
        print("采集成功:今日美国-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
        return len(package)

    def a(self,publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：今日美国-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return True
        else:
            return False
