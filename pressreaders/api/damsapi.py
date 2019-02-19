import requests
import json
import pathlib
import random
import re


class DamsApi:
    def __init__(self, username, password):
        # API地址
        self.apiurl = "http://test.yuyiai.com/"
        # http://test.yuyiai.com/
        # http://192.168.1.116/
        # http://www.yuyiai.com:8000/
        # 访问token
        self.accesstoken = ""
        # 用于刷新的token
        self.refreshtoken = ""
        # token类型
        self.tokentype = ""
        # 登录用户名
        self.username = username
        # 登录密码
        self.password = password
        # 用户ID
        self.userid = 0
        # 用户名称
        self.truename = ""

    # 获取token
    def gettoken(self):
        url = self.apiurl + "api/oauth/token"
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'client_id': 'zkwg',
            'client_secret': 'zkwg'
        }
        headers = {'content-type': "application/json",'Connection':'keep-alive'}

        rsp = requests.post(url, data=data, headers=headers,timeout=40)

        # print(rsp.text)

        ret = rsp.json()

        if("error" in ret):
            print(ret["error_description"])
            return False
        else:
            self.accesstoken = ret["access_token"]
            self.refreshtoken = ret["refresh_token"]
            self.tokentype = ret["token_type"]

            userinfo = self.getuserinfo()

            if(userinfo["success"]):
                self.userid = userinfo["result"]["id"]
                self.truename = userinfo["result"]["trueName"]
                return True
            else:
                print(userinfo["error"]["message"])
                return False
    # 获取某个用户信息
    def getuserinfo(self):
        url = self.apiurl + "api/services/app/user/GetUser"

        headers = {
            'Authorization': self.tokentype + " " + self.accesstoken
            , 'Connection': 'keep-alive'
        }

        data = {
            'UserName': self.username
        }

        rsp = requests.get(url, params=data, headers=headers,timeout=40)

        # print(rsp.text)

        return rsp.json()

    # 获取报刊类型信息
    def getnewspaperlibraryinfo(self, newspaperlibraryid):
        url = self.apiurl + "api/services/app/newspaperlibrary/GetNewspaperLibrary"

        headers = {'Authorization': self.tokentype + " " + self.accesstoken,'Connection':'keep-alive'}

        data = {
            'newspaperLibraryId': newspaperlibraryid
        }

        rsp = requests.get(url, params=data, headers=headers,timeout=40)

        #print(rsp.text)

        return rsp.json()


    # 判断报纸是否存在
    def checknewspaperexists(self, newspaperlibraryid, publishedtime):
        url = self.apiurl + "api/services/app/newspaper/CheckNewspaperExists"

        headers = {'Authorization': self.tokentype + " " + self.accesstoken,'Connection':'keep-alive'}

        data = {
            'newspaperLibraryId': newspaperlibraryid,
            'publishedTime': publishedtime,
            'newspaperId': 0
        }

        rsp = requests.post(url, data=data, headers=headers,timeout=40)

        # print(rsp.text)

        return rsp.json()

    # 添加报纸
    def addnewspaper(self, newspaper):
        url = self.apiurl + "api/services/app/newspaper/CreateNewspaperByAPI"

        headers = {'Authorization': self.tokentype + " " + self.accesstoken,'Connection':'keep-alive'}

        rsp = requests.post(url, data=newspaper, headers=headers,timeout=40)

        # print(rsp.text)

        return rsp.json()

    # 添加文章
    def addarticle(self, article):
        url = self.apiurl + "api/services/app/article/CreateArticle"

        headers = {'Authorization': self.tokentype + " " + self.accesstoken,'Connection':'keep-alive'}
        i = 0
        while i < 3:
            try:
                rsp = requests.post(url, data=article, headers=headers, timeout=40)
                break
            except:
                i += 1

        # print(rsp.text)

        return rsp.json()

    # 上传图片
    def updateimg(self, imagesUrl, newspaperId, requireAgent, cookies="", referer=""):
        url = self.apiurl + "Articles/DownloadImages"

        headers = {'Authorization': self.tokentype + " " + self.accesstoken,'Connection':'keep-alive'}

        data = {
            "ImagesUrl": imagesUrl,
            "NewspaperId": newspaperId,
            "Cookies": cookies,
            "RequireAgent": requireAgent,
            "Referer":referer
        }
        i = 0
        while i<4:
            try:
                rsp = requests.post(url, data=data, headers=headers,timeout=40)
                if rsp.status_code == 200:
                    break
            except:
                i += 1

        # print(rsp.text)

        return rsp.json()

    def downloadimg(self,imagesUrl, requireAgent,times,papername,cookies="", referer=""):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            "Cookies": cookies,
        }
        if referer:
            headers["Referer"] = referer
        # "RequireAgent": requireAgent,
        proxy = {'http': 'http://127.0.0.1:8124', 'https': 'https://127.0.0.1:8124'}
        src = []
        for url in imagesUrl.split('#'):
            i = 0
            while i < 5:
                try:
                    if requireAgent:
                        rep = requests.get(url, headers=headers, timeout=40,proxies = proxy)
                    else:
                        rep = requests.get(url, headers=headers, timeout=40)
                    if rep.status_code == 200:
                        break
                except:
                    i += 1
            ext = re.search('\.[jpgnif]{3,4}',url,re.I).group()
            if not ext:
                ext = '.jpg'
            while True:
                file = "D:/数据采集系统_测试/电子文件/NewspaperImages/" + papername + '/' + times.split('-')[0] + '/' + times.replace('-','') + str(random.randint(1000000000, 10000000000)) + ext
                if not pathlib.Path(file).is_file():
                    break
            with open(file, 'wb') as f:
                f.write(rep.content)
            src.append('/ViewFile/NewspaperImages' + file.split('NewspaperImages')[1])
        return {'result':'#'.join(src)}
