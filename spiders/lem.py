from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import re
from spiders.basespider import Spider
#
class Lemonde(Spider):
    newspaperlibraryid = "1052399163934769152"
    tips = 0
    def login(self,browser,date = ''):
        try:
            wait = WebDriverWait(browser, 60)
            if date:
                month = {'janvier': '1', 'février': '2', 'mars': '3', 'avril': '4', 'mai': '5', 'juin': '6', 'juillet': '7',
                         'août': '8', 'septembre': '9', 'octobre': '10', 'novembre': '11', 'décembre': '12'}
                date_list =  wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="subTitle"]')))
                click = 0
                for days in date_list:
                    day = days.text.split()
                    if len(day) < 3:
                        continue
                    day = [day[2], month[day[1]], day[0]]
                    if '-'.join(day) == date:
                        print('已找到报纸')
                        click = 1
                        days.click()
                        break
                if click == 0:
                    print('未找到报纸')
                    browser.close()
                    return
            else:
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="main-button-wrapper pointer"]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="connection_mail"]'))).send_keys("13574827001@163.com")
            time.sleep(0.3)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="connection_password"]'))).send_keys("Yyy123456")
            time.sleep(0.3)
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="connection_save"]'))).click()
        except Exception as e:
            print(e)
            browser.get('https://journal.lemonde.fr')
            return self.login(browser,date = date)

    def paper_list(self,browser,i=1):
        # try:
        wait = WebDriverWait(browser, 120)
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="swiper-slide-page-click"]'))).click()
        except:
            time.sleep(5)
                # browser.maximize_window()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="swiper-slide-page-click"]'))).click()
        package = []
        tips = 0
        while True:
            data = self.paper_text(browser)
            if data:
                tips += 1
                print('正在采集第%s篇' % tips)
                package.append(data)
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH,'//div[contains(@class,"alb-nav-next")]'))).click()
            except:
                break
        return package
        # except:
        #     if i < 5:
        #         print(i)
        #         i += 1
        #         time.sleep(5)
        #         package = self.paper_list(browser, i)
        #     else:
        #         print('采集失败,请检查网络')


    def paper_text(self,browser):
        cookie = browser.get_cookies()
        c = ''
        for i in cookie:  # 添加cookie到CookieJar
            c += i["name"] + '=' + i["value"] + ';'
        data = {}
        wait = WebDriverWait(browser, 20)
        div = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="swiper-slide alb-slide swiper-slide-active"]')))
        data['title'] = div.find_element_by_xpath('div//div[@class="alb-article-title"]').text
        try:
            data['subTitle'] = div.find_element_by_xpath('div//div[@class="alb-article-subtitle"]').get_attribute('innerText')
        except:
            data['subTitle'] = ''
        imgs = div.find_elements_by_xpath('div//div[contains(@class,"swiper-slide-alb-img pointer") and contains(@class,"swiper-slide")]')
        images = []
        introduce = []
        for img in imgs:
            images.append(img.find_element_by_xpath('div//img').get_attribute('src'))
            try:
                introduce.append(img.find_element_by_xpath('div//p').get_attribute('innerText'))
            except:
                introduce.append('')
        data['images'] = '#'.join(images)
        data['imageDescriptions'] = '#'.join(introduce)
        authors = div.find_elements_by_xpath('div//div[@class="alb-article-author"]//span')
        author = []
        if len(authors) > 1:
            for i in authors:
                author.append(i.text.replace(',','').replace(' et ','').replace('Propos recueillis par ',''))
            data['author'] = '#'.join(author)
        elif len(authors) == 1:
            data['author'] = authors[0].text.replace(',','#').replace(' et ','#').replace('Propos recueillis par ','')
        else:
            data['author'] = ''
        try:
            data['abstract'] = div.find_element_by_xpath('div//div[@class="alb-article-introduction"]').text
        except:
            data['abstract'] = ''
        text = div.find_elements_by_xpath('div//div[@class="alb-article-content"]/div[@class="dropcap"]/*')
        data['authorArea'] = ''
        mainbody = ''
        if not text:
            text = div.find_elements_by_xpath('div//div[@class="alb-article-content"]/*')
        for i in text:
            if i.tag_name == 'renvoipage':
                continue
            if i.get_attribute('class') == 'fenetre' and not data['title']:
                data['title'] = i.text
                continue
            mainbody += '<p>' + i.text + '</p>'
        data['mainBody'] = mainbody
        data['authorDescriptions'] = ''
        data['channel'] = ''
        data['page'] = ''
        data['cookies'] = c
        data['referer'] = ''
        if data['title'] or data['mainBody'] or data['images']:
            return data
        else:
            return None

    def date_get(self,browser):
        month = {'janvier':'1','février':'2','mars':'3','avril':'4','mai':'5','juin':'6','juillet':'7','août':'8','septembre':'9','octobre':'10','novembre':'11','décembre':'12'}
        wait = WebDriverWait(browser, 60)
        try:
            data = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'main-label'))).text.split()
            date = [data[2],month[data[1]],data[0]]
        except:
            time.sleep(1)
            date = self.date_get(browser)
            return date
        return '-'.join(date)

    def supplement(self):
        date = input('请输入日期：(例如：2019-01-07)\n')
        if self.a(date):
            return 0
        new_date = [re.sub('^0', '', i) for i in date.split('-')]
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get("https://journal.lemonde.fr")
        try:
            self.login(browser,date = '-'.join(new_date))
            print('登陆成功，开始采集数据')
            package = self.paper_list(browser)
            browser.close()
            if not package:
                return 0
            super().uploaddata(date, package, self.newspaperlibraryid, True)
            print("采集成功:法国世界报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
            return len(package)
        except Exception as e:
            # browser.close()
            raise e

    def run(self):
        print('开始采集：法国世界报')
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get("https://journal.lemonde.fr")
        try:
            date = self.date_get(browser)
            if self.a(date):
                browser.close()
                return 0
            self.login(browser)
            print('登陆成功，开始采集数据')
            package = self.paper_list(browser)
            browser.close()
            if not package:
                return 0
            super().uploaddata(date, package, self.newspaperlibraryid, True)
            print("采集成功:法国世界报-发行日期（" + date + "),文章数量（" + str(len(package)) + "）")
            return len(package)
        except Exception as e:
            browser.close()
            raise e


    def a(self,publishedtime):
        api = self.api
        # 先获取token
        ret = api.gettoken()
        if not ret:
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：法国世界报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return True
        else:
            return False
