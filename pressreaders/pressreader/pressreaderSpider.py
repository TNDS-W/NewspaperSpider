import requests,re,json,datetime,os,time
from pressreaders.api.basespider import Spider
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pressreaders.pressreader.author_clean import AuthorClean

# 作者：文振乾
# 时间：2018-12-13
# 用途：爬取pressreader系列

class PressreaderSpider(Spider):
    def __init__(self,username,password,newspaperlibraryid,paperId,displayname):
        self.newspaperlibraryid = newspaperlibraryid
        self.paperId = paperId
        self.displayname = displayname
        super().__init__(username,password)
        self.proxy ={"http":"http://127.0.0.1:8124","https":"https://127.0.0.1:8124"}
        self.Session = requests.session()


    # 获取每个版面所有新闻的id
    def getresponse(self,cookie,date,paperId,serviceUrl):
        times = "".join(str(date).split("-"))
        url = serviceUrl + "toc/?callback=tocCallback&issue="+paperId + times+"00000000001001&version=3&expungeVersion="
        header = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            # 'Referer': 'http://thewashingtonpost.pressreader.com/the-washington-post/201811/textview'
            'cookie' : cookie
        }
        try:
            response = self.Session.get(url,headers=header,proxies=self.proxy)
        except:
            response = self.Session.get(url, headers=header,proxies=self.proxy)

        #如果昨天没有新闻 则返回
        if response.status_code == 404:
            # print(date + " 日暂无新闻，可能是周报")
            return

        result = response.content.decode("utf=8")
        return result,date

    def getid(self,result):
        id = []  # 存储每个版面的所有id
        pagename = re.findall(r'"Articles":\[.+?].*?"SectionName":"(.+?)"',result)    #有内容的版面
        pagename = list(set(pagename))
        resultdict = json.loads("".join(re.findall(r"tocCallback\((.*)\)",result)))["Pages"]
        for x in pagename:
            articleid = []
            for y in range(len(resultdict)):
                articles = resultdict[y]["Articles"]
                if resultdict[y]["SectionName"] == x:
                    if articles != None:
                        for z in range(len(articles)):
                            articleid.append(str(articles[z]["Id"]))
            if articleid != []:
                id.append(articleid)

        return id



    # 拼接并得到所有版面的url
    def get_url(self,id,accessToken,serviceUrl):
        urls = []
        for x in id:
            if len(x) <= 1:
                ids = "".join(x)
            else:
                ids = "%2c".join(x)
            url = serviceUrl+"articles/GetItems/?accessToken="+accessToken+"&articles="+ids+"&comment=LatestByAll&options=1&viewType=text"
            # print(url)
            urls.append(url)
        return urls


    def parse_url(self,urls,cookie,paperId):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            # 'Origin': 'http://thewashingtonpost.pressreader.com',
            # 'Referer': "http://thewashingtonpost.pressreader.com/the-washington-post-sunday/20181209/textview"
            "cookie": cookie
        }
        count = 0
        for url in urls:
            i = 0
            while i<3:
                try:
                    response = self.Session.get(url,headers=header,proxies=self.proxy)
                    # time.sleep(10)
                    break
                except:
                    i += 1
            # response = requests.get(url,headers=header)
            result = json.loads(response.content.decode("utf-8"))["Articles"]
            for x in range(len(result)):
                imgurls = []
                imgdescription = []
                content = []
                title = result[x]["Title"]
                if title == None:
                    continue
                cont = result[x]["Blocks"]
                if cont == None:
                    continue
                for a in range(len(cont)):
                    content.append(cont[a]["Text"].replace("",""))

                subTitle = "".join(result[x]["Subtitle"].split("\xad"))
                imgs = result[x]["Images"]
                if imgs != None:
                    for y in range(len(imgs)):
                        if imgs[y]["Url"] == None:
                            imgurls.append("")
                        else:
                            imgurls.append(imgs[y]["Url"])
                        if imgs[y]["Title"] == None:
                            imgdescription.append("")
                        else:
                            imgdescription.append(imgs[y]["Title"])
                if len(imgurls) <= 1:
                    imgurl = "".join(imgurls)
                else:
                    imgurl = "#".join(imgurls)
                authorArea = ""
                mainbody = "".join("".join(["<p>"+b+"</p>" for b in content]).split("\xad"))
                authorDescriptions = ""
                abstract = result[x]["Abstract"]
                channel = result[x]["Section"]
                if len(imgdescription) <= 1:
                    imageDescriptions = "".join(imgdescription)
                else:
                    imageDescriptions = "#".join(imgdescription)
                authors = result[x]["Byline"]     #.replace("By ","")
                author = AuthorClean(paperId,authors).cleaning()
                pagename = result[x]["PageName"]
                pagenumber = result[x]["Page"]
                yield {"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                       "authorDescriptions": authorDescriptions, "abstract": abstract,
                       "channel": channel, "mainBody": mainbody, "page": pagename,
                       "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
                       "referer": "","pagenumber":pagenumber}
                print("-->采集第" + str(count + 1) + "篇文章<--")
                count += 1
        print("一共采集" + str(count) + "篇文章")

    # 处理内容重复问题
    def message_clean(self, messages):
        message = []

        for x in range(len(messages)):
            right = True
            for y in range(x, len(messages)):
                if x == y:
                    continue
                if messages[x]["title"] == messages[y]["title"]:
                    if messages[x]["mainBody"][0] == messages[y]["mainBody"][0]:
                        if messages[y]["page"] not in messages[x]["page"]:
                            messages[y]["page"] = messages[x]["page"] + "#" + messages[y]["page"]
                        if (messages[y]["channel"] not in messages[x]["channel"]) and (messages[x]["channel"] not in messages[y]["channel"]):
                            messages[y]["channel"] = messages[x]["channel"] + "#" + messages[y]["channel"]
                        messages[y]["pagenumber"] = messages[x]["pagenumber"]
                        # messages[y]["page"] = "".join(set(messages[y]["page"].split("#")))
                        right = False
                        break
            if right:
                message.append(messages[x])

        return message

    # 根据质检的要求删除华盛顿邮报的的第一个版面
    def delete_page(self, messages):
        message = []
        # 去掉版面为a1的所有文章
        for x in range(len(messages)):
            if messages[x]["page"] != "A1" or messages[x]["pagenumber"] != 1:
                message.append(messages[x])
        return message

    # 用于补录时的登陆
    def log_in(self, url, baseurl, datenumber):
        global driver
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('log-level=3')
        options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        time.sleep(5)
        #登陆
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "userphoto"))).click()
        # WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located(
        #     (By.XPATH, '//span[@class="textbox"]//input[@id="SignInEmailAddress"]'))).send_keys("13574827001@163.com")
        time.sleep(2)
        driver.find_element_by_id("SignInEmailAddress").send_keys("13574827001@163.com")
        driver.find_element_by_xpath('//span[@class="textbox"]//input[@type="password"]').send_keys("Yyy123456")
        log_in_btn = driver.find_element_by_xpath('//div[@class="pop-group"]//button[@type="submit"]')
        time.sleep(1)
        log_in_btn.send_keys(Keys.RETURN)
        time.sleep(3)
        #浏览页面
        driver.get(baseurl + "".join(datenumber.split("-")) + "/textview")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "datepickerContainer")))


    def run(self):
        api = self.api
        # 获取token信息
        try:
            ret = api.gettoken()
        except:
            ret = api.gettoken()
        if not ret:
            return 0
        with open(os.getcwd()+"\info.json","r") as f:
            info = eval(f.read())

        oneday = datetime.timedelta(days=1)
        # 由于境内境外报纸更新日期不同 所有统一爬前一天的报纸
        datenumber = datetime.date.today() - oneday
        accessToken = info["accessToken"]
        cookie = info["cookie"]
        serviceUrl = info["serviceUrl"]

        getresponse = self.getresponse(cookie,datenumber,self.paperId,serviceUrl)
        if getresponse == None:
            print(str(datenumber) + " 今天暂无新闻，"+self.displayname+"可能是周报,或者该报纸周末不更新")
            return 0
        # 从网页中获取发行日期
        publishedtime = str(getresponse[1])
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        #如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败："+self.displayname+"-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            id = self.getid(getresponse[0])
            print("开始采集:"+self.displayname)
            print("正在采集新闻")
            urls = self.get_url(id,accessToken,serviceUrl)
            messages=list(self.parse_url(urls,cookie,self.paperId))
            if self.paperId == "1047" or self.paperId == "1058":
                message = self.delete_page(messages)
                message = self.message_clean(message)
            else:
                message = self.message_clean(messages)
            message.sort(key=lambda message:int(message["pagenumber"]))
            super().uploaddata(publishedtime, message, self.newspaperlibraryid, True)
            print("采集成功:"+self.displayname+"-发行日期（" + publishedtime + "),文章数量（" + str(len(message)) + "）")
        return len(message)

    #补录
    def supplement(self,baseurl):
        api = self.api
        # 获取token信息
        try:
            ret = api.gettoken()
        except:
            ret = api.gettoken()
        if not ret:
            return 0
        with open(os.getcwd() + "\info.json", "r") as f:
            info = eval(f.read())

        # 输入补录日期
        datenumber = input("请输入要补录的日期（例：2018-01-01）：")    # str
        oneday = datetime.timedelta(days=1)
        publishedtime = datetime.datetime.strptime(datenumber, '%Y-%m-%d')   #datetime
        accessToken = info["accessToken"]
        cookie = info["cookie"]
        serviceUrl = info["serviceUrl"]
        # 打开网页,登陆
        self.log_in("https://www.pressreader.com",baseurl,datenumber)

        for x in range(200):
            # driver = webdriver.Chrome()
            right = False
            i = 0
            while i < 2:
                try:
                    driver.get(baseurl + "".join(str(publishedtime).split(" ")[0].split("-")) + "/textview")
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "datepickerContainer")))
                    time.sleep(3)
                    right = False
                    break
                except Exception as e:
                    print(e)
                    driver.refresh()
                    time.sleep(2)
                    i += 1
                    right = True

            if right:
                publishedtime += oneday
                continue

            # driver.close()

            getresponse = self.getresponse(cookie, str(publishedtime).split(" ")[0], self.paperId, serviceUrl)
            if getresponse == None:
                print(str(publishedtime).split(" ")[0] + " 今天暂无新闻，" + self.displayname + "可能是周报,或者该报纸周末不更新")
                # return 0
                publishedtime += oneday
            # 判断报纸是否存在
            ret = api.checknewspaperexists(self.newspaperlibraryid, str(publishedtime).split(" ")[0])
            # 如果为True,则说明已经存在
            if (ret["success"] and ret["result"]):
                print("采集失败：" + self.displayname + "-发行日期已经存在，报纸日期（" + str(publishedtime).split(" ")[0] + ")")
                # return 0
                publishedtime += oneday
            else:
                id = self.getid(getresponse[0])
                print("开始采集:" + self.displayname)
                print("正在采集新闻")
                urls = self.get_url(id, accessToken, serviceUrl)
                messages = list(self.parse_url(urls, cookie,self.paperId))
                if self.paperId == "1047" or self.paperId == "1058":
                    message = self.delete_page(messages)
                    message = self.message_clean(message)
                else:
                    message = self.message_clean(messages)
                message.sort(key=lambda message: int(message["pagenumber"]))
                super().uploaddata(str(publishedtime).split(" ")[0], message, self.newspaperlibraryid, True)
                print("采集成功:" + self.displayname + "-发行日期（" + str(publishedtime).split(" ")[0] + "),文章数量（" + str(len(message)) + "）")
                publishedtime += oneday

# if __name__ == '__main__':
#     wst = WstPost("wzq","123456")
#
#     wst.run()

