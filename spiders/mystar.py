from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import selenium.common.exceptions as Ex
import datetime
from spiders.basespider import Spider
import time
import re
from selenium.webdriver.chrome.options import Options

class Mystar():
    #报纸id
    newspaperlibraryid = '1056715269021368320'

    #采集报纸
    def getnewepaper(self):
        # 报纸集合
        neweparper = []
        publishtime = ''

        # 站点的电子报路径    马来西亚星报
        url = 'http://mystar.newspaperdirect.com/epaper/viewer.aspx'

        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu') chrome_options=chrome_options

        # 声明驱动
        driver = webdriver.Chrome()

        # 声明等待
        wait = WebDriverWait(driver, 10)

        # 鼠标行动
        actions = ActionChains(driver)

        # 访问站点
        driver.get(url)

        # 窗口最大化
        driver.maximize_window()

        #登陆
        driver.find_element_by_id('signin').click()
        driver.switch_to.frame('content_frame')
        driver.find_element_by_id('_ctl0__ctl0_MainContentPlaceHolder_MainPanel__ctl1_login__ctl0_UserName').send_keys('13574827001@163.com')
        driver.find_element_by_id('_ctl0__ctl0_MainContentPlaceHolder_MainPanel__ctl1_login__ctl0_Password').send_keys('Yyy123456')
        driver.find_element_by_id('login_existing_user_login_btn').click()

        #选择报纸
        driver.find_element_by_xpath("//DIV[@class='se-t2-paper_place']/A").click()

        #电子报首页
        driver.switch_to.default_content()

        #发布时间
        publishtime = driver.find_element_by_id('calendar_menu_title').text

        #进入第一篇文章
        actions.move_to_element(driver.find_element_by_xpath("//A[@id='toc_icon']/SPAN")).perform()
        time.sleep(2)
        actions.move_to_element(driver.find_element_by_xpath("//DIV[@id='toc_menubody']//TBODY/TR[2]")).perform()
        time.sleep(1)
        driver.find_element_by_xpath("//DIV[@id='toc_submenu_menubody']/DIV[2]/A").click()

        #文章
        driver.switch_to.frame("content_frame")
        driver.switch_to.frame("content_window_frame_elm")
        nextbtn = driver.find_elements_by_xpath("//DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")

        #取文章内容
        while True:
            time.sleep(1)
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

            ##取值
            title = driver.find_element_by_xpath("//*[@id='artMain']//H1")
            subtitle = driver.find_element_by_xpath("//*[@id='artMain']//DIV[@class='clear']//H2")
            author = driver.find_element_by_xpath("//*[@id='artMain']/div/ul/li[4]")
            authordescriptions = driver.find_element_by_xpath("//*[@id='artMain']/div/ul/li[4]")
            mainbody = driver.find_elements_by_xpath("//DIV[contains(@id,'testArtCol')]/P")
            images = driver.find_elements_by_xpath("//*[@id='artMain']//IMG")
            imagesdescriptions = driver.find_elements_by_xpath("//*[@id='artMain']//span[contains(@class,'imagetext')]")
            driver.switch_to.default_content()
            driver.switch_to.frame("content_frame")
            page = driver.find_element_by_xpath("//*[@id='content_window_title']")
            channel = driver.find_element_by_xpath("//*[@id='content_window_title']")


            # 打印，数据处理
            #标题
            titlelist = titlelist + title.text

            # 副标题
            subtitlelist = subtitlelist + subtitle.text

            # 作者
            author = author.text
            if author:
                author = author.split("By ")
                it = re.finditer("[A-Z]+((\.\s)|\s)([A-Z]+\s)+", author[1])
                for mm in it:
                    mm.group()
                authorlist = authorlist + mm.group(0)
            else:
                authorlist = authorlist + author

            #作者描述
            authordescriptions = authordescriptions.text
            if authordescriptions:
                authordescriptions = authordescriptions.split("By ")
                it = re.finditer('[a-z.]+@thestar.com.my', authordescriptions[1])
                for mm in it:
                    mm.group()
                authordescriptionslist = authordescriptionslist + mm.group(0)
            else:
                authordescriptionslist = authordescriptionslist + authordescriptions

            # 版面
            page = page.text
            page = re.finditer('[0-9]+', page)
            for mp in page:
               mp.group()
            pagelist = pagelist + mp.group(0)

            # 频道
            channel = channel.text
            channel = re.finditer('([A-Za-z]+(\s|))+', channel)
            for cp in channel:
                cp.group()
            channellist = channellist + cp.group(0)

            # 正文
            for mb in mainbody:
                mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"

            # 图片
            for im in images:
                imageslist = imageslist + im.get_attribute('src') + "#"
            imageslist = imageslist[:-1]

            # 图片描述
            for imd in imagesdescriptions:
                imagesdescriptionslist = imagesdescriptionslist + imd.text + "#"
            imagesdescriptionslist = imagesdescriptionslist[:-1]

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

            neweparper.append(artpage)

            driver.switch_to.frame("content_window_frame_elm")

            #下一篇
            try:
                nextbtn[1].click()
            except Ex.NoSuchElementException:
                break

        driver.close()
        newtime = {'newepaper': neweparper, "publishtime": self.EtoCtime(publishtime)}
        return newtime

    def EtoCtime(self,publishtimes):
        Etime = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "Aug": 8,
            "Sept": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12
        }

        tp = publishtimes.split(" ")

        publishtime = "%s-%s-%s" % (tp[2], Etime[tp[1]], tp[0])
        return publishtime

if __name__ == '__main__':
    Mystar().getnewepaper()