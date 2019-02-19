import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import threading,time,re
from spiders.basespider import Spider

# 作者：文振乾
# 时间：2018-12-27
# 用途：爬取金字塔报

class Ahram(Spider):
    newspaperlibraryid = "1062159789942898688"
    message = []
    number = 1
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}

    #获取报纸发行日期
    def getpublishedtime(self):
        url = 'http://weekly.ahram.org.eg/'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        try:
            response = requests.get(url,headers=header, proxies=self.proxy)
        except:
            response = requests.get(url,headers=header, proxies=self.proxy)
        result = response.text
        # timenumber = re.findall('Issue.*?\((.*?) -',result)
        timenumber = re.findall("Issue.*?\((.*?)\)",result)
        time.sleep(0.3)
        times = timenumber[0].split()
        print(times)
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
        year = times[-1]
        month = months[times[3].capitalize()]
        day = times[0]
        publishedtime = year + "-" + month + "-" + day
        return publishedtime

    # 获取所有新闻的url
    def getnewsurl(self):
        #声明driver为全局变量
        global driver
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('http://weekly.ahram.org.eg/')
        driver.set_page_load_timeout(50)
        menu = driver.find_elements_by_xpath('//ul[@id="ctl00_ulMenu"]/li/a')[1:]
        #所有新闻的url
        newsurl = []
        paper = 1
        for x in range(len(menu)):
            try:
                driver.find_elements_by_xpath('//ul[@id="ctl00_ulMenu"]/li/a')[x+1].click()
            except:
                driver.refresh()
                time.sleep(2)
                driver.find_elements_by_xpath('//ul[@id="ctl00_ulMenu"]/li/a')[x + 1].click()

            # try:
            #     driver.set_page_load_timeout(10)
            # except:
            #     driver.refresh()
            #     time.sleep(4)
            time.sleep(0.2)
            result = driver.page_source
            html = etree.HTML(result)
            url = html.xpath('//div[@class="col-xs-12 col-sm-9 col-md-9 col-lg-9 inContLeft"]//div//h2/a/@href')
            print("第"+str(paper)+"条url获取成功")
            paper += 1
            if url != []:
                newsurl.append(url)
            while True:
                try:
                    driver.find_elements_by_xpath('//a[@aria-label="Next"]')[0].click()              #下一页
                    time.sleep(0.2)
                    result = driver.page_source
                    html = etree.HTML(result)
                    url = html.xpath('//div[@class="col-xs-12 col-sm-9 col-md-9 col-lg-9 inContLeft"]//div//h2/a/@href')
                    print("第" + str(paper) + "条url获取成功")
                    paper += 1
                    if url != []:
                        newsurl.append(url)
                except:
                    break
        try:
            driver.find_elements_by_xpath('//ul[@id="ctl00_ulMenu"]/li/a')[0].click()
        except:
            driver.refresh()
            time.sleep(2)
            driver.find_elements_by_xpath('//ul[@id="ctl00_ulMenu"]/li/a')[0].click()
        result = driver.page_source
        html = etree.HTML(result)
        listingurl = html.xpath('//ul[@class="listingUl"]/li/a/@href')
        newsurl.append(listingurl)
        driver.close()
        return newsurl

    def parsepage(self,urls):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        for x in range(len(urls)):
            print("第"+ str(self.number) +"篇采集成功")
            self.number += 1
            try:
                response = requests.get(urls[x], headers=header, timeout=10, proxies=self.proxy)
            except:
                response = requests.get(urls[x], headers=header, timeout=10, proxies=self.proxy)

            while True:
                if response.status_code != 200:
                    time.sleep(0.5)
                    response = requests.get(urls[x], headers=header, timeout=10, proxies=self.proxy)
                else:
                    break

            time.sleep(0.2)
            result = response.content.decode("utf-8")
            # print(result)
            html = etree.HTML(result)
            #标题
            title = "".join(html.xpath('//div[@id="ctl00_ContentPlaceHolder1_header"]/h1/text()')).strip()

            #副标题
            subTitle = "".join(html.xpath('//div[@id="ctl00_ContentPlaceHolder1_abstractDiv"]//text()')).replace('\r\n',"").replace('\xa0',"").replace("\t","")

            #作者
            author = "".join(html.xpath('//div[@class="row"]/div/h5/a/text()'))

            # 正文
            mainbody = []
            content = html.xpath('//div[@class="innTxt"]/p//text()')
            hr = html.xpath('//div[@class="innTxt"]/hr')
            if hr != []:
                authorDescriptions = content[-1]           # 作者描述
                for x in content[:-1]:
                    if x != "\r\n\t":
                        article = "<p>"+ x + "</p>"
                        mainbody.append(article)
            else:
                authorDescriptions = ""
                for x in content:
                    if x != "\r\n\t":
                        article = "<p>"+ x + "</p>"
                        mainbody.append(article)
            mainbody = "".join(mainbody).replace("\r\n\t","")

            #图片
            try:
                imgurl = html.xpath('((//div[@class="cycle-slideshow"]/img)[1]|//div[@class="innTxt"]/div/img)/@src')
                if len(imgurl) <=1:
                    imgurl = "".join(imgurl)
                    imageDescriptions = "".join(html.xpath('//div[@class="cycle-slideshow"]/h5/text()|//div[@class="innTxt"]/div/h5/text()'))
                else:
                    imgurl = "#".join(imgurl)
                    imageDescriptions = "#".join(html.xpath('//div[@class="cycle-slideshow"]/h5/text()|//div[@class="innTxt"]/div/h5/text()'))
            except:
                imgurl = ""
                imageDescriptions = ""

            #频道
            channel = "".join(html.xpath('//h3[@id="ctl00_ContentPlaceHolder1_inContH1"]/a//text()'))

            authorArea = ""
            abstract = ""
            self.message.append(
                {"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                 "authorDescriptions": authorDescriptions, "abstract": abstract,
                 "channel": channel, "mainBody": mainbody, "page": "",
                 "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
                 "referer": ""})
            # print((subTitle,channel))


    def main(self):
        print("正在获取url")
        urls = self.getnewsurl()
        print("获取完成")
        threads = []    #线程池
        for url in urls:
            threads.append(threading.Thread(target=self.parsepage,args=[url]))
        for x in threads:
            x.start()
        for y in threads:
            y.join()
        # for x in urls:
        #     self.parsepage(x)

    def run(self):
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        publishedtime = self.getpublishedtime()
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：金字塔报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("开始采集:金字塔报")
            print("正在采集新闻")
            try:
                self.main()
            except Exception as e:
                driver.close()
                raise e
            # time.sleep(3)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
            print("采集成功:金字塔报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        return len(self.message)


# Ahram("wzq","123456").run()
# if __name__ == '__main__':
#     Ahram("wzq", "123456").run()

