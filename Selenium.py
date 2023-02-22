'''
使用自动化测试工具selenium，模拟网页登录获取网页源码
'''
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
# from selenium.webdriver.edge.options import Options
# from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By

class Selenium():
    def __init__(self):
        # 加载设置
        option = Options()
        # 导入本地Edge浏览器的用户数据
        option.add_argument(r'user-data-dir=C:\Users\JK\AppData\Local\Google\Chrome\User Data')
        # 不自动关闭浏览器，用来调试
        # option.add_experimental_option("detach", True)
        # 设置加载策略
        option.page_load_strategy = 'normal'
        # 不显示浏览器
        option.add_argument('headless')
        # 载入设置
        self.driver = webdriver.Chrome(options=option)

    def get_msg_html(self, url):
        # 访问你要制作成epub的页面，注意需要提前在谷歌浏览器上登录
        self.driver.get(url)
        try:
            # 等待页面加载完成后再继续,只等待60秒
            Wait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="q-list q-list--separator"]')))
            message_html = self.driver.find_element(By.CSS_SELECTOR, 'html').get_attribute('outerHTML')
            return message_html
        except TimeoutException:
            print("超时！请检查谷歌浏览器正在运行或者是否登录该网站账号")

    # 获取每个章节的内容
    def get_contet_html(self, url):
        # 访问章节
        self.driver.get(url)
        try:
            # 等待页面加载完成后再继续,只等待60秒
            Wait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="html-reader read"]')))
            # 停10秒，防止频繁访问网页ip被封
            time.sleep(10)
            content_html = self.driver.find_element(By.CSS_SELECTOR, 'html').get_attribute('outerHTML')
            return content_html
        except TimeoutException:
            print("超时！请检查谷歌浏览器正在运行或者是否登录该网站账号")
    # 退出浏览器
    def exit(self):
        self.driver.close()
