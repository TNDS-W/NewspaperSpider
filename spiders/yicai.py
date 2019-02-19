from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions as Ex
from spiders.basespider import Spider
import datetime
import time
import re
import requests
from lxml import etree
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from selenium.webdriver.common.by import By
import os
from spiders.vertify.numVertify import NumVertify

class Yicai(Spider):
    newspaperlibraryid = '1045861257275506688'

    def get_position(self,wait):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        img = wait.until(EC.presence_of_element_located((By.ID, 'Verify')))
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + \
                                   size['width']
        return (top, bottom, left, right)

    def get_screenshot(self,driver):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self, wait,driver):
        """
        获取验证码图片
        :return: 图片对象
        """
        name = 'captcha.png'
        top, bottom, left, right = self.get_position(wait)
        screenshot = self.get_screenshot(driver)
        captcha = screenshot.crop((left, top, right, bottom))
        if os.path.exists(name):
            os.remove(name)
        captcha.save(name)
        # return captcha

    #获取时间
    def get_time(self,url = 'http://buy.yicai.com/read/index/id/5.html'):
        resp = requests.get(url)

        html = etree.HTML(resp.text)

        date = html.xpath("//a[@class='brand']/text()")

        date = date[0]

        date = date.replace("年", "-")
        date = date.replace("月", "-")
        date = date.replace("日", "")

        # print(date)

        return date

    # 采集报纸
    def yicaipaper(self,url = 'http://buy.yicai.com/read/index/id/5.html'):
        # 报纸集合
        neweparper = []

        global driver

        # 站点的电子报路径    21世纪经济报道
        # url = 'http://buy.yicai.com/read/index/id/5.html'

        # 声明驱动
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        driver = webdriver.Chrome(chrome_options=chrome_options)

        # 声明等待
        wait = WebDriverWait(driver, 10)

        # 鼠标行动
        actions = ActionChains(driver)

        # 访问站点
        driver.get(url)

        # 窗口最大化
        driver.maximize_window()
        i = 0
        while i < 6:
            try:
                #登陆
                driver.find_element_by_xpath("//DIV[@id='LogNo']/A[@class='UserLogin']").click()

                time.sleep(1)
                driver.find_element_by_xpath(
                    "//DIV[@class='UserFrom']/DIV[@class='input-prepend']/INPUT[@name= 'username']").send_keys("13574827001")
                driver.find_element_by_xpath(
                    "//DIV[@class='UserFrom']/DIV[@class='input-prepend']/INPUT[@name= 'password']").send_keys("Yyy123456")

                # 验证码识别
                self.get_image(wait, driver)
                vertifyclass = NumVertify()
                vertify = vertifyclass.vertify_identity()

                driver.find_element_by_xpath("//DIV[@class='UserFrom']/DIV[@class='input-prepend']/INPUT[@name='code']").send_keys(vertify)

                driver.find_element_by_xpath("//button[@class='btn btn-info btn-block btn-primary']").click()

                driver.find_element_by_xpath("//DIV[@id='ShowConMain']//DIV[@class='navbar-inner']/DIV[2]/LI[2]/A")
                break
            except:
                i += 1
                driver.refresh()
                time.sleep(2)


        # #报纸
        # driver.find_element_by_xpath("//DIV[@class='left_menu']/DIV[6]//A").click()
        #
        # #选择窗口
        # win = driver.window_handles
        # # driver.close()
        # driver.switch_to.window(win[1])

        # 登陆
        # cookie = {"domain": "buy.yicai.com",
        #           'name': 'PHPSESSID',
        #           'value': 'a890df996d5f623b1cc8d04148212848',
        #           'path': '/',
        #           'httpOnly': False,
        #           'HostOnly': False,
        #           'Secure': False
        #           }
        # driver.add_cookie(cookie)

        # time.sleep(5)
        # driver.refresh()

        time.sleep(2)
        nextpage = driver.find_element_by_xpath("//DIV[@id='ShowConMain']//DIV[@class='navbar-inner']/DIV[2]/LI[2]/A")

        while nextpage != None:
            time.sleep(0.6)
            # 获取内容
            title = driver.find_element_by_xpath("//DIV[@class='conrand']//FONT[@class='SetTitle']")
            subtitle = driver.find_elements_by_xpath("//*[@id='SetsubTitle']")
            author = driver.find_element_by_xpath("//SPAN[@id='Setauthor']")
            page = driver.find_element_by_xpath("//FONT[@id='SetNumber']")
            channel = driver.find_element_by_xpath("//STRONG[@class='picBName']//A")
            mainbody = driver.find_elements_by_xpath("//*[@id='SetContent']/P")
            images = driver.find_elements_by_xpath("//*[@id='SetContent']/DIV/DIV[1]/img")
            imagesdescription = driver.find_elements_by_xpath("//DIV[@id='SetContent']/DIV/DIV[last()]")

            # 内容
            titlelist = ''
            subtitlelist = ''
            authorlist = ''
            authorarealist = ''
            authordescriptionslist = ''
            pagelist = ''
            channellist = ''
            abstractlist = ''
            mainbodylist = ''
            imageslist = ''
            imagesdescriptionslist = ''

            # 打印
            # 标题
            # print(title.text + "\n")
            titlelist = titlelist + title.text

            # 副标题
            for st in subtitle:
                # print(st.text + "\n")
                subtitlelist = subtitlelist + st.text

            # 作者
            # print(author.text)
            author =  author.text
            # 作者#处理
            pattern = re.compile(u'[\u4e00-\u9fa5]+')
            author = re.findall(pattern, author)
            for ah in author:
                authorlist = authorlist + ah + "#"
            authorlist = authorlist[:-1]

            # 版面
            try:
                # print(page.text + "\n")
                pagelist = pagelist + page.text
            except Ex.StaleElementReferenceException as e:
                pagelist = ''

            # 频道
            try:
                channel = channel.text
                if channel:
                    pattern = r'[A-Z]{1}?[0-9]{2}'
                    rechannel = re.sub(pattern,"",channel)
                    channel = rechannel.strip()
                    channellist = channellist + channel
            except Ex.StaleElementReferenceException as e:
                channellist = ''

            # 正文
            try:
                for mb in mainbody:
                    # print("<p>" + mb.text + "</p>" + "\n")
                    mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
            except Ex.StaleElementReferenceException as e:
                # print()
                mainbodylist = ''

            # 图片
            for im in images:
                # print( im.get_attribute('src') + "\n")
                imageslist = imageslist + im.get_attribute('src') + '#'

            # 图片描述
            try:
                for imd in imagesdescription:
                    # print(mb.text + "\n")
                    imagesdescriptionslist = imagesdescriptionslist + imd.text + '#'
            except Ex.StaleElementReferenceException:
                imagesdescriptionslist = ''

            # 保存到文章字典
            artpage = {
                'title': titlelist,
                'subTitle': subtitlelist,
                'author': authorlist,
                'authorArea': authorarealist,
                'authorDescriptions': authordescriptionslist,
                'page': pagelist,
                'channel': channellist,
                'abstract': abstractlist,
                'mainBody': mainbodylist,
                'images': imageslist,
                'imageDescriptions': imagesdescriptionslist,
                'cookies' : '',
                'referer' : ''
            }

            # 去除版面文章
            reg = re.compile(r'[A]{1}([0-9]{2})(\s\s|\s)[\u4e00-\u9fa5]+')
            need = re.match(reg, title.text)
            if need:
                pass
            else:
                # 去广告
                reg = re.compile(r'[A]{1}[D]{1}\.(\s\s|\s)')
                pa = re.match(reg, title.text)
                if pa:
                    pass
                else:
                    # 文章集合
                    neweparper.append(artpage)

            # 下一篇
            nextpage.click()

            try:
                alert = driver.switch_to.alert
                driver.close()
                return neweparper
                # break
            except Ex.NoAlertPresentException:
                pass
        # driver.close()

    def run(self):

        api = self.api

        #获取token
        ret = api.gettoken()
        if not ret:
            return 0

        # 从网页中获取发行日期
        publishedtime = self.get_time()

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：第一财经日报-发行日期已经存在，报纸日期（"+publishedtime+")")
            return 0
        else:
            #数据加到数据库
            print('开始采集：第一财经日报')
            print("正在采集新闻")
            # self.denglu()
            try:
                data = self.yicaipaper()
            except Exception as e:
                driver.close()
                raise e
            if len(data) < 1:
                print("采集结束:第一财经日报-发行日期（" + publishedtime + "),没有更新文章或不在更新日期内")
            else:
                super().uploaddata(publishedtime,data,self.newspaperlibraryid,False)
                print("采集成功:第一财经日报-发行日期（"+publishedtime+"),文章数量（"+str(len(data))+"）")
        return len(data)

    #补录
    def supplement(self):
        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return

        # 从网页中获取发行日期
        publishedtime = self.get_date()

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：第一财经日报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return
        else:
            # 数据加到数据库
            print("开始采集：第一财经日报")
            print("正在采集新闻……")
            try:
                data = self.selenium_get_paper_and_supplement()
            except Exception as e:
                raise e
            super().uploaddata(publishedtime, data, self.newspaperlibraryid, False)
            print("采集成功:第一财经日报-发行日期（" + publishedtime + "),文章数量（" + str(len(data)) + "）")

    def selenium_get_paper_and_supplement(self):

        neweparper = []

        driver = webdriver.Chrome()

        driver.maximize_window()

        driver.get('http://buy.yicai.com/read/index/id/5.html')

        # 登陆
        cookie = {"domain": "buy.yicai.com",
                  'name': 'PHPSESSID',
                  'value': 'a890df996d5f623b1cc8d04148212848',
                  'path': '/',
                  'httpOnly': False,
                  'HostOnly': False,
                  'Secure': False
                  }
        driver.add_cookie(cookie)

        driver.refresh()

        input_finish = input("完成登陆和报纸的定位（完成输入1）")

        if int(input_finish) == 1:
            nextpage = driver.find_element_by_xpath(
                "//DIV[@id='ShowConMain']//DIV[@class='navbar-inner']/DIV[2]/LI[2]/A")

            while nextpage != None:
                # 获取内容
                title = driver.find_element_by_xpath("//DIV[@class='conrand']//FONT[@class='SetTitle']")
                subtitle = driver.find_elements_by_xpath("//*[@id='SetsubTitle']")
                author = driver.find_element_by_xpath("//SPAN[@id='Setauthor']")
                page = driver.find_element_by_xpath("//FONT[@id='SetNumber']")
                channel = driver.find_element_by_xpath("//STRONG[@class='picBName']//A")
                mainbody = driver.find_elements_by_xpath("//*[@id='SetContent']/P")
                images = driver.find_elements_by_xpath("//*[@id='SetContent']/DIV/DIV[1]/img")
                imagesdescription = driver.find_elements_by_xpath("//DIV[@id='SetContent']/DIV/DIV[last()]")

                # 内容
                titlelist = ''
                subtitlelist = ''
                authorlist = ''
                authorarealist = ''
                authordescriptionslist = ''
                pagelist = ''
                channellist = ''
                abstractlist = ''
                mainbodylist = ''
                imageslist = ''
                imagesdescriptionslist = ''

                # 打印
                # 标题
                # print(title.text + "\n")
                titlelist = titlelist + title.text

                # 副标题
                for st in subtitle:
                    # print(st.text + "\n")
                    subtitlelist = subtitlelist + st.text

                # 作者
                # print(author.text)
                author = author.text
                # 作者#处理
                pattern = re.compile(u'[\u4e00-\u9fa5]+')
                author = re.findall(pattern, author)
                for ah in author:
                    authorlist = authorlist + ah + "#"
                authorlist = authorlist[:-1]

                # 版面
                try:
                    # print(page.text + "\n")
                    pagelist = pagelist + page.text
                except Ex.StaleElementReferenceException as e:
                    pagelist = ''

                # 频道
                try:
                    channel = channel.text
                    if channel:
                        pattern = re.compile(u'[\u4e00-\u9fa5]+$')
                        rechannel = re.findall(pattern, channel)
                        for channel in rechannel:
                            # print(channel + "\n")
                            channellist = channellist + channel
                except Ex.StaleElementReferenceException as e:
                    channellist = ''

                # 正文
                try:
                    for mb in mainbody:
                        # print("<p>" + mb.text + "</p>" + "\n")
                        mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
                except Ex.StaleElementReferenceException as e:
                    # print()
                    mainbodylist = ''

                # 图片
                for im in images:
                    # print( im.get_attribute('src') + "\n")
                    imageslist = imageslist + im.get_attribute('src') + '#'

                # 图片描述
                try:
                    for imd in imagesdescription:
                        # print(mb.text + "\n")
                        imagesdescriptionslist = imagesdescriptionslist + imd.text + '#'
                except Ex.StaleElementReferenceException:
                    imagesdescriptionslist = ''

                # 保存到文章字典
                artpage = {
                    'title': titlelist,
                    'subTitle': subtitlelist,
                    'author': authorlist,
                    'authorArea': authorarealist,
                    'authorDescriptions': authordescriptionslist,
                    'page': pagelist,
                    'channel': channellist,
                    'abstract': abstractlist,
                    'mainBody': mainbodylist,
                    'images': imageslist,
                    'imageDescriptions': imagesdescriptionslist,
                    'cookies': '',
                    'referer': ''
                }

                # 去除版面文章
                reg = re.compile(r'[A]{1}([0-9]{2})(\s\s|\s)[\u4e00-\u9fa5]+')
                need = re.match(reg, title.text)
                if need:
                    pass
                else:
                    # 去广告
                    reg = re.compile(r'[A]{1}[D]{1}\.(\s\s|\s)')
                    pa = re.match(reg, title.text)
                    if pa:
                        pass
                    else:
                        # 文章集合
                        neweparper.append(artpage)

                # 下一篇
                nextpage.click()

                try:
                    alert = driver.switch_to.alert
                    driver.close()
                    return neweparper
                    # break
                except Ex.NoAlertPresentException:
                    pass
        else:
            print("输入错误")



    def get_date(self):
        dade = input("输入补录的日期如（2019-01-01）")
        return dade



    # def denglu(self):
    #     # 站点的电子报路径
    #     url = 'http://buy.yicai.com/read/index/id/5.html'
    #
    #     driver = webdriver.Chrome()
    #
    #     wait= WebDriverWait(driver,10)
    #
    #     driver.get(url=url)
    #
    #     driver.maximize_window()
    #
    #     driver.find_element_by_xpath("//DIV[@id='LogNo']/A[@class='UserLogin']").click()
    #
    #     time.sleep(1)
    #     driver.find_element_by_xpath("//DIV[@class='UserFrom']/DIV[@class='input-prepend']/INPUT[@name= 'username']").send_keys("13574827001")
    #     driver.find_element_by_xpath("//DIV[@class='UserFrom']/DIV[@class='input-prepend']/INPUT[@name= 'password']").send_keys("Yyy123456")
    #
    #     #验证码识别
    #     self.get_image(wait,driver)
    #     vertifyclass = NumVertify()
    #     vertify = vertifyclass.vertify_identity()
    #
    #     driver.find_element_by_xpath("//input[@class='span1 Validform_error']").send_keys(vertify)
    #
    #     driver.find_element_by_xpath("//button[@class='btn btn-info btn-block btn-primary']").click()
    #
    #
    #     driver.close()

# if __name__ == '__main__':
#      Yicai().denglu()
