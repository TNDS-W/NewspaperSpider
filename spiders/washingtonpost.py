import requests,re,json,time
from spiders.basespider import Spider
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from spiders.basespider import Spider


class WstPost(Spider):
    message = []    # 存储所有信息
    newspaperlibraryid = "1033578898694078464"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome()

    # 登陆获取cookie
    def log_in(self):
        driver.get(
            "https://subscribe.washingtonpost.com/loginregistration/index.html#/register/group/long?action=login&rememberme=true")
        WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//div[@class="form-group"]/input[@type="email"]'))).send_keys("13574827001@163.com")
        driver.find_element_by_id("password").send_keys("Yyy123456")
        log_in_btn = driver.find_element_by_id("signinBtnTWP")
        time.sleep(1)
        log_in_btn.click()
        time.sleep(10)
        WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'sw-text'))).click()
        result = driver.page_source
        # 得到当前页面的url
        url = driver.current_url
        times = "".join(re.findall('/([0-9]{8})/',url))
        # 获取发行日期
        date = times[:4]+"-"+times[4:6]+"-"+times[6:]
        accessToken = "".join(re.findall(r'"accessToken":"(.+?)"',result))
        return accessToken,date



    # 获取每个版面所有新闻的id
    def getid(self,date):
        times = "".join(date.split("-"))
        id = []             # 存储每个版面的所有id
        url = "https://s.prcdn.co/se2skyservices/toc/?callback=tocCallback&issue=1047"+times+"00000000001001&version=8&expungeVersion="
        header = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            'Referer': 'http://thewashingtonpost.pressreader.com/the-washington-post/201811/textview'
        }
        i = 0
        while i<3:
            try:
                response = requests.get(url,headers=header)
                result = response.content.decode("utf=8")
                break
            except:
                i +=1
        # print(result)
        # getAll = re.findall(r'tocCallback\((.*)\)',result)
        pagename = re.findall(r'"Articles":\[.+?].*?"SectionName":"(.+?)"',result)    #有内容的版面
        pagename = list(set(pagename))
        # print(result)
        resultdict = json.loads("".join(re.findall(r"tocCallback\((.*)\)",result)))["Pages"]
        for x in pagename:
            articleid = []
            for y in range(len(resultdict)):
                articles = resultdict[y]["Articles"]
                if resultdict[y]["SectionName"] == x:
                    if articles != None:
                        for z in range(len(articles)):
                            articleid.append(str(articles[z]["Id"]))
            id.append(articleid)

        return id



    # 拼接并得到所有版面的url
    def get_url(self,id,accessToken):
        urls = []
        for x in id:
            if len(x) <= 1:
                ids = "".join(x)
            else:
                ids = "%2c".join(x)
            url = "https://svc.pressreader.com/se2skyservices/articles/GetItems/?accessToken="+accessToken+"&articles="+ids+"&comment=LatestByAll&options=1&viewType=text"
            urls.append(url)
        return urls


    def parse_url(self,urls):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            'Origin': 'http://thewashingtonpost.pressreader.com',
            'Referer': "http://thewashingtonpost.pressreader.com/the-washington-post-sunday/20181209/textview"
        }
        for url in urls:
            i = 0
            time.sleep(2)
            while i<3:
                try:
                    response = requests.get(url,headers=header)
                    break
                except:
                    i += 1
            result = json.loads(response.content.decode("utf-8"))["Articles"]
            for x in range(len(result)):
                imgurls = []
                imgdescription = []
                content = []
                cont = result[x]["Blocks"]
                for a in range(len(cont)):
                    content.append(cont[a]["Text"])
                title = "".join(result[x]["Title"].split("\xad"))
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
                # print(imgdescription)
                if len(imgurls) <= 1:
                    imgurl = "".join(imgurls)
                else:
                    imgurl = "#".join(imgurls)
                authorArea = ""
                mainbody = "".join("".join(["<p>"+b+"</p>" for b in content]).split("\xad"))
                authorDescriptions = ""
                abstract = result[x]["Abstract"]
                channel = ""
                if len(imgdescription) <= 1:
                    imageDescriptions = "".join(imgdescription)
                else:
                    imageDescriptions = "#".join(imgdescription)
                author = result[x]["Byline"]
                pagename = result[x]["PageName"]

                self.message.append({"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                                     "authorDescriptions": authorDescriptions, "abstract": abstract,
                                     "channel": channel, "mainBody": mainbody, "page": pagename,
                                     "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
                                     "referer": ""})
                publishedTime = result[0]["Issue"]["Date"]


    def run(self):
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return
        # 从网页中获取发行日期
        publishedtime = self.log_in()[1]
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：华盛顿邮报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return
        else:
            print("开始采集:华盛顿邮报")
            print("正在采集新闻")
            url = self.get_url(self.getid(publishedtime),self.log_in()[0])
            self.parse_url(url)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
            print("采集成功:华盛顿邮报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")


if __name__ == '__main__':
    wst = WstPost("wzq","123456")

    wst.log_in()

