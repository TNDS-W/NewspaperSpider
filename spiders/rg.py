import re,time
from lxml import etree
from selenium import webdriver
from spiders.basespider import Spider
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# 作者：文振乾
# 时间：2019-01-13
# 用途：爬取俄罗斯报

class Rg(Spider):
    newspaperlibraryid = "1059265222734249984"
    message = []

    def get_publishedtime(self):
        global driver
        option = webdriver.ChromeOptions()
        option.add_argument('--disable-gpu')
        option.add_argument('log-level=3')
        option.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=option)
        driver.set_page_load_timeout(50)
        try:
            driver.get("https://rg.ru/gazeta/rg/svezh.html")
        except:
            driver.execute_script('window.stop()')
        times = driver.find_element_by_xpath('(//div[@class="b-list-head__date"]/span)[1]').text
        publishedtime = times.split(" ")[0:-1]

        # 清洗日期         俄罗斯报月份不明确，报纸上的月份和翻译出来的月份可能不一样,需要定期更改
        months = {
            "января": "01",
            'февраль': "02",
            'февраля': "02",
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
        year = publishedtime[2]
        try:
            month = months[publishedtime[1]]
        except:
            print("月份不同需更改或者网络出错")
        day = publishedtime[0]
        publishedTime = year + "-" + month + "-" + day
        return publishedTime

    def get_driver(self,publishedtime):
        global driver
        option = webdriver.ChromeOptions()
        option.add_argument('--disable-gpu')
        option.add_argument('log-level=3')
        option.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=option)
        driver.set_page_load_timeout(50)
        times = publishedtime.replace("-","/")
        try:
            driver.get("https://rg.ru/gazeta/rg/" + times + ".html")
        except:
            driver.execute_script('window.stop()')
        return

    def get_url(self):
        urls = []
        news = driver.find_elements_by_xpath(
            '//h2[@class="b-news-inner__list-item-title"]/a|//h2[@class="b-news__list-item-title"]/a|//div[@class="b-broadside"]')
        page = ""
        for x in range(len(news)):
            if re.search('Полоса',news[x].text):
                page = news[x].text
                urls.append(page)
            else:
                if page != "":
                    url = news[x].get_attribute("href")
                    urls.append(url)
        return urls

    def parse_page(self,urls):
        number = 1    # 用于计数
        page = ""
        for x in range(len(urls)):
            if re.search('Полоса',urls[x]):
                page = urls[x]
            else:
                if page != "":
                    try:
                        driver.get(urls[x])
                    except:
                        try:
                            driver.execute_script('window.stop()')
                        except:
                            pass
                    try:
                        WebDriverWait(driver,100).until(EC.presence_of_element_located((By.XPATH,'(//img[@class="b-material-img__img"]|//div[@class="article-img__pic"]|(//img[@class="fotorama__img"])[1])')))
                    except:
                        driver.refresh()
                        time.sleep(2)
                        WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,'//h1[@class="b-material-head__title"]')))

                    mainbody = []
                    imgurl = []
                    descriptions = []
                    imageDescriptions = []
                    result = driver.page_source
                    html = etree.HTML(result)
                    title = "".join(html.xpath('//h1[@class="b-material-head__title"]/text()'))

                    subTitle = "".join(html.xpath('//div[@class="b-material-head__subtitle"]/text()'))

                    author = "".join(html.xpath('//div[@class="b-material-head__authors-item"]/a/text()')).replace(",","#")

                    authorArea = ""

                    authorDescriptions = ""

                    abstract = "".join(html.xpath('//div[@class="b-material-wrapper__lead"]//text()'))

                    channel = "".join(html.xpath('//div[@class="b-material-head__rubric"]/a/text()'))

                    cont = html.xpath('(//div[@class="b-material-wrapper__text"]/p|//div[@class="b-material-wrapper__text"]/h2|//div[@class="b-material-wrapper__text"]/div[@class="incut" or @class="Section"])//text()')
                    for x in cont:
                        if x != "":
                            mainbody.append("<p>" + x + "</p>")
                    mainbody = "".join(mainbody)

                    imgs = html.xpath('(//img[@class="b-material-img__img"]|//div[@class="article-img__pic"]|(//img[@class="fotorama__img"])[1]|//a[@class="cboxElement"])//@src')
                    for y in imgs:
                        imgurl.append("https:" + y)
                    if len(imgurl) >1:
                        imgurl = "#".join(imgurl)
                    else:
                        imgurl = "".join(imgurl)

                    description = html.xpath('//div[@class="b-material-img__title" or @class="article-img__info" or @class="fotorama__caption__wrap" or @class = "article-img__infograph__text"]')
                    for z in range(len(description)):
                        descrip = html.xpath('(//div[@class="b-material-img__title" or @class="article-img__info" or @class="fotorama__caption__wrap" or @class = "article-img__infograph__text"])[' + str(z+1) + ']//text()')
                        descriptions.append("".join(descrip))
                    if len(imageDescriptions) > 1:
                        imageDescriptions = "#".join(descriptions)
                    else:
                        imageDescriptions = "".join(descriptions)


                    self.message.append({"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                                         "authorDescriptions": authorDescriptions, "abstract": abstract,
                                         "channel": channel, "mainBody": mainbody, "page": page,
                                         "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
                                         "referer": ""})
                    print("第" + str(number) + "条采集完成")
                    number += 1
                else:
                    raise Exception("版面错误")

    def run(self):
        self.message = []
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        try:
            publishedtime = self.get_publishedtime()
        except Exception as e:
            driver.close()
            raise e
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：俄罗斯报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("开始采集:俄罗斯报")
            print("正在采集新闻")
            try:
                self.parse_page(self.get_url())
            except Exception as e:
                driver.close()
                raise e
            driver.close()
            # time.sleep(3)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
            print("采集成功:俄罗斯报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        return len(self.message)

    def supplement(self):
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        publishedtime = input("请输入补录的日期(2018-01-01):")
        try:
            self.get_driver(publishedtime)
        except Exception as e:
            driver.close()
            raise e
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：俄罗斯报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("开始采集:俄罗斯报")
            print("正在采集新闻")
            try:
                self.parse_page(self.get_url())
            except Exception as e:
                driver.close()
                raise e
            driver.close()
            # time.sleep(3)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
            print("采集成功:俄罗斯报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        self.message = []



# if __name__ == '__main__':
#     Rg().get_publishedtime()