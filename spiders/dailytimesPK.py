from spiders.basespider import Spider
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# 获取最新期刊日期
def getDate():
    global driver
    global wait
    global chrome_options
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('log-level=3')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    wait = WebDriverWait(driver, 20)
    driver.get('https://dailytimes.com.pk/epaper/07-01-2019/')
    epaper_navList = driver.find_elements_by_xpath('//div[@class="one-sixth first"]/ul[@class="epaper-nav"]/li')
    areaHrefList = []
    i = 1
    for epaper_nav in epaper_navList:
        epaper_nav.click()
        wait.until(
            EC.presence_of_element_located((By.XPATH, '//DIV[@id="result"]/MAP[@name="a' + str(i) + '"]/AREA')))
        areaList = driver.find_elements_by_xpath('//div[@id="result"]/map[@name="a' + str(i) + '"]/area')
        for area in areaList:
            areaHref = str(area.get_attribute("href"))
            if areaHref.count(".jpg") is 0:
                print(areaHref)
                areaHrefList.append(areaHref)
        i += 1
    count = 0
    for newarea in areaHrefList:
        driver.get(newarea)
        try:
            titleXpath = driver.find_element_by_xpath(
                '//div[@class="header-content no-image"]/h1[@class="entry-title"]')
            title = titleXpath.text
            print("-->采集第" + str(count + 1) + "篇文章<--")
            print("新闻标题：" + title)
        except Exception as e:
            continue
        count += 1
    driver.close()

    sleep(10)


if __name__ == '__main__':
    getDate()
