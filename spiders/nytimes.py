from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from lxml import etree
from spiders.basespider import Spider
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# 作者：文振乾
# 时间：2018-12-11
# 用途：爬取纽约时报

class Nytimes(Spider):
    newspaperlibraryid = "1031862569821798400"
    message = []  # 保存爬取下来的所有数据


    # 登陆
    def log_in(self):
        # 将driver 定义为全局
        global driver
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get("https://app.nytimes.com/")
        # 通过contains函数，提取匹配特定文本的所有元素
        # iframe = driver.find_element_by_xpath('//iframe[contains(@src,"https://myaccount.nytimes.com/mobile/login/iframe/index.html?EXIT_URI=https%3A%2F%2Fapp.nytimes.com%2FloginReturn")]')
        # 进入iframe页面
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "newLogin")))
        driver.switch_to.frame("newLogin")
        driver.find_element_by_id("username").send_keys("13574827001@163.com")
        password = driver.find_element_by_id("password")
        password.send_keys("Yyy123456")
        password.send_keys(Keys.RETURN)
        # 返回到主页面
        driver.switch_to.default_content()
        time.sleep(5)
        # for x in range(1):
        #     before = driver.find_element_by_xpath('(//div[@class="content"]/div)[2]')
        #     before.click()
        # time.sleep(2)
        result = driver.page_source
        html = etree.HTML(result)

        try:
            times = html.xpath('//p[@class="edition-date"]/text()')[-1]
        except:
            time.sleep(5)
            times = html.xpath('//p[@class="edition-date"]/text()')[-1]

        # 清洗日期
        months = {
            "January": "01",
            'February': "02",
            'March': "03",
            'April': "04",
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': "12"
        }
        year = times.split(", ")[2]
        month = months[times.split(", ")[1].split(" ")[0]]
        day = times.split(", ")[1].split(" ")[1]
        publishedTime = year + "-" + month + "-" + day
        driver.find_elements_by_xpath('//div[@class="overlay"]/h1')[-1].click()
        return publishedTime

    # 补录登陆方法
    # def supplement_log(self,date):
    #     # 将driver 定义为全局
    #     global driver
    #     chrome_options = webdriver.ChromeOptions()
    #     # chrome_options.add_argument('--headless')
    #     # chrome_options.add_argument('--disable-gpu')
    #     chrome_options.add_argument('log-level=3')
    #     # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
    #     driver = webdriver.Chrome(chrome_options=chrome_options)
    #     driver.get("https://app.nytimes.com/")
    #     # 通过contains函数，提取匹配特定文本的所有元素
    #     # iframe = driver.find_element_by_xpath('//iframe[contains(@src,"https://myaccount.nytimes.com/mobile/login/iframe/index.html?EXIT_URI=https%3A%2F%2Fapp.nytimes.com%2FloginReturn")]')
    #     # 进入iframe页面
    #     time.sleep(1)
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "newLogin")))
    #     driver.switch_to.frame("newLogin")
    #     driver.find_element_by_id("username").send_keys("13574827001@163.com")
    #     password = driver.find_element_by_id("password")
    #     password.send_keys("Yyy123456")
    #     password.send_keys(Keys.RETURN)
    #     # 返回到主页面
    #     driver.switch_to.default_content()
    #     time.sleep(5)
    #     result = driver.page_source
    #     html = etree.HTML(result)
    #     try:
    #         times = html.xpath('//p[@class="edition-date"]/text()')
    #     except:
    #         time.sleep(5)
    #         times = html.xpath('//p[@class="edition-date"]/text()')
    #     times = times.reverse()
    #     # 清洗日期
    #     months = {
    #         "January": "01",
    #         'February': "02",
    #         'March': "03",
    #         'April': "04",
    #         'May': '05',
    #         'June': '06',
    #         'July': '07',
    #         'August': '08',
    #         'September': '09',
    #         'October': '10',
    #         'November': '11',
    #         'December': "12"
    #     }
    #     for x in range(len(times)):
    #         year = times[x].split(", ")[2]
    #         month = months[times[x].split(", ")[1].split(" ")[0]]
    #         day = times[x].split(", ")[1].split(" ")[1]
    #         publishedTime = year + "-" + month + "-" + day
    #         if date == times[x]:
    #             for y in range(x):
    #                 driver.find_element_by_class_name("carousel-prev").click()
    #             driver.find_elements_by_xpath('//div[@class="overlay"]/h1')[-(x+1)].click()
    #             break
    #     return publishedTime

    def get_news(self):
        time.sleep(5)
        leftlist = driver.find_elements_by_xpath('//div[@id="accordion"]/div[@class]//span')  # 频道列表
        newslist = driver.find_elements_by_xpath('//div[@class="accordion-section-holder"]/ol/li/div/div')  # 每个频道下的新闻列表
        page = 1
        intpage = count = 0
        for y in range(len(newslist)):
            time.sleep(0.5)
            try:
                newslist[y].click()
                time.sleep(0.5)
                intpage += 1
                try:
                    element = driver.find_elements_by_xpath('(//div[@class="article-content"])[' + str(intpage) + ']//img')
                    for pict in range(len(element)):
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].scrollIntoView();", element[pict])
                        time.sleep(0.5)
                except:
                    pass
                # print("----------------------------------------------------------")
                result = driver.page_source
            except Exception as e:
                leftlist[page].click()
                time.sleep(0.5)
                newslist[y].click()
                time.sleep(0.3)
                intpage = 1
                try:
                    element = driver.find_elements_by_xpath('(//div[@class="article-content"])[' + str(intpage) + ']//img')[-1]
                    for pict in range(len(element)):
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].scrollIntoView();", element[pict])
                        time.sleep(0.5)
                except:
                    pass
                result = driver.page_source
                page += 1

            self.parsepage(result, intpage)
            count = y + 1
            print("——>采集第" + str(count) + "篇文章<--")
        print("一共采集" + str(count) + "篇文章")

    # 解析页面
    def parsepage(self, result, intpage):
        mainbody = []
        html = etree.HTML(result)
        title = "".join(html.xpath('(//div[@class="article-content"]//div//h2)[' + str(intpage) + ']//text()'))
        try:
            authors = "".join(html.xpath(
                '(//div[@class="article-content"])[' + str(intpage) + ']/div[@class="byline"]/text()')).replace("By ","")
            if ("and" in authors) or ("," in authors):
                author = "#".join(authors.split(" and ")).replace(",", "#")

            else:
                author = authors
        except:
            author = ""

        try:
            number = html.xpath('(//div[@class="article-content"])[' + str(intpage) + ']/div[@class="body"]//p')
            for x in range(len(number)):
                content = html.xpath('((//div[@class="article-content"])[' + str(intpage) + ']/div[@class="body"]//p)[' + str(x+1) + ']//text()|(//div[@class="article-content"])[' + str(intpage) + ']/div[@class="body"]//h4//text()')
                content = " ".join(content)
                if content != "":
                    mainbody.append("<p>" + content + "</p>")
            mainbody = "".join(mainbody)
        except:
            mainbody = ""

        try:
            img = html.xpath('(//div[@class="article-content"])[' + str(intpage) + ']//img//@src')
            if len(img) <= 1:
                imgurl = "".join(img)
            else:
                imgurl = "#".join(img)
        except:
            imgurl = ""

        try:
            descriptions = html.xpath(
                '(//div[@class="article-content"])[' + str(intpage) + ']//div[@class="caption"]/text()')
            if len(descriptions) <= 1:
                imageDescriptions = "".join(descriptions)
            else:
                imageDescriptions = "#".join(descriptions)
        except:
            imageDescriptions = ""

        subTitle = ""
        authorArea = ""
        authorDescriptions = ""
        abstract = ""
        channel = "".join(html.xpath('(//div[@class="article-content"]//div/div/span)[1]//text()'))
        self.message.append(
            {"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
             "authorDescriptions": authorDescriptions, "abstract": abstract,
             "channel": channel, "mainBody": mainbody, "page": "",
             "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
             "referer": ""})

    def run(self):
        self.message = []
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0

        # 从网页中获取发行日期
        print("开始采集:纽约时报")
        try:
            publishedtime = self.log_in()
        except Exception as e:
            driver.close()
            raise e
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：纽约时报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            driver.close()
            return 0
        else:
            print("正在采集新闻……")
            try:
                self.get_news()
            except Exception as E:
                driver.close()
                raise E
            driver.close()
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
            print("采集成功:纽约时报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        return len(self.message)

    def supplement(self):
        times = input("请输入要补录的报纸日期(例：2018-01-01):")

# if __name__ == '__main__':
#     Nytimes("wzq","123456").supplement()
