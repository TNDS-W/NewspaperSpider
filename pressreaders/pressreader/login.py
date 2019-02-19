import re,time,datetime,os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from pressreaders.pressreader.pressreaderSpider import PressreaderSpider

# 作者：文振乾
# 时间：2018-12-13
# 用途：登陆pressreader

class Login():


    def log(self, url, pressreaderlist):
        global driver
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('log-level=3')
        options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        time.sleep(5)
        #登陆
        WebDriverWait(driver, 20).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, "userphoto"))).click()
        # WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located(
        #     (By.XPATH, '//span[@class="textbox"]//input[@id="SignInEmailAddress"]'))).send_keys("13574827001@163.com")
        time.sleep(2)
        driver.find_element_by_id("SignInEmailAddress").send_keys("13574827001@163.com")
        driver.find_element_by_xpath('//span[@class="textbox"]//input[@type="password"]').send_keys("Yyy123456")
        log_in_btn = driver.find_element_by_xpath('//div[@class="pop-group"]//button[@type="submit"]')
        time.sleep(1)
        log_in_btn.send_keys(Keys.RETURN)
        time.sleep(5)

        #获取cookie
        driver.refresh()
        time.sleep(2)
        result = driver.page_source
        accessToken = "".join(re.findall(r'"accessToken":"(.+?)"', result))
        # i += 1
        cookies = driver.get_cookies()
        # self.driver.close()
        cookie = []
        for x in cookies:
            cookie.append(x["name"]+"="+x["value"])
        cookie = ";".join(cookie)

        time.sleep(7)
        # print(accessToken)
        serviceUrl = "".join(re.findall('window.serviceUrl = "(.+?)"',result))
        oneday = datetime.timedelta(days=1)
        today = datetime.date.today()
        yestoday = str(today-oneday).replace("-","")
        data = {"cookie":cookie,"accessToken":accessToken,"date":str(today),"serviceUrl":serviceUrl}

        #将每个页面先访问一遍才能采集到正文 否则正文不全
        for x in range(len(pressreaderlist)):
            driver.get(pressreaderlist[x]["class"] + str(yestoday) + '/textview')
            try:
                WebDriverWait(driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"datepickerContainer")))
            except:
                driver.refresh()
            print("开始加载"+ pressreaderlist[x]["displayname"] +"报刊")
            time.sleep(1)
        #  info 用来存 cookie accessToken date 数据
        with open(os.getcwd()+"\info.json","w+",encoding="utf-8") as f:
            f.write(str(data))
        driver.close()


    def main(self, pressreaderlist):
        print("正在登陆(需要访问页面，可能耗时较长)")
        try:
            self.log("https://www.pressreader.com", pressreaderlist)
        except Exception as e:
            driver.close()
            raise e
        print("加载完成")

# if __name__ == '__main__':
#     Login().run()

