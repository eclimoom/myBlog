# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
from pyquery import PyQuery as pq
from tqdm import trange
import xlsxwriter
import os
# 定义一个taobao类


class taobao_infos:

    # 对象初始化
    def __init__(self):
        url = 'https://login.taobao.com/member/login.jhtml'
        self.url = url

        options = webdriver.ChromeOptions()
        # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 不加载图片,加快访问速度
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        # options.add_experimental_option(
        #     'excludeSwitches', ['enable-automation'])
        # 使用本地浏览器，免登录
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10, 0.5)  # 超时时长为10s

    # 登录淘宝

    def login(self):
        self.browser.implicitly_wait(3)
        # 打开网页
        self.browser.get(self.url)
        time.sleep(1)
        # 等待 淘宝账号 出现
        self.browser.find_element_by_id(
            "fm-login-id").send_keys(taobao_username)
        self.browser.find_element_by_id(
            "fm-login-password").send_keys(taobao_password)
        self.browser.find_element_by_css_selector(
            "#login-form > div.fm-btn > button").click()
        # time.sleep(1)
        self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 's-baseinfo')))
        taobaoName = self.browser.find_element_by_xpath(
            '//div[@class="s-baseinfo"]/div[@class="s-name"]/a/em').text
        print(taobaoName)
        print(self.browser.current_url)

    # 地址
    def get_addr(self):
        url = 'https://member1.taobao.com/member/fresh/deliver_address.htm'
        self.browser.get(url)
        html_str = self.browser.page_source
        obj_list = etree.HTML(html_str).xpath(
            '//tbody[@class="next-table-body"]/tr')
        data_list = []
        for obj in obj_list:
            item = {}
            item['name'] = obj.xpath('.//td[1]//text()')
            item['area'] = obj.xpath('.//td[2]//text()')
            item['detail_area'] = obj.xpath('.//td[3]//text()')
            item['youbian'] = obj.xpath('.//td[4]//text()')
            item['mobile'] = obj.xpath('.//td[5]//text()')
            print(item)
            data_list.append(item)
            # 地址

# 爬取淘宝 我已买到的宝贝商品数据, pn 定义爬取多少页数据
    def crawl_good_buy_data(self, pn=3):
        # 对我已买到的宝贝商品数据进行爬虫
        self.browser.get(
            "https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm")
        # 遍历所有页数
        for page in trange(1, pn):
            data_list = []
            # 等待该页面全部已买到的宝贝商品数据加载完毕
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#tp-bought-root > div.js-order-container')))
            # 获取本页面源代码
            html = self.browser.page_source
            # pq模块解析网页源代码
            doc = pq(html)
            # # 存储该页已经买到的宝贝数据
            good_items = doc('#tp-bought-root .js-order-container').items()
            # 遍历该页的所有宝贝
            for item in good_items:
                # 商品购买时间、订单号
                good_time_and_id = item.find(
                    '.bought-wrapper-mod__head-info-cell___29cDO').text().replace('\n', "").replace('\r', "")
                # 商家名称
                # good_merchant = item.find('.seller-mod__container___1w0Cx').text().replace('\n', "").replace('\r', "")
                good_merchant = item.find(
                    '.bought-wrapper-mod__seller-container___3dAK3').text().replace('\n', "").replace('\r', "")
                # 商品名称
                # good_name = item.find('.sol-mod__no-br___1PwLO').text().replace('\n', "").replace('\r', "")
                good_name = item.find(
                    '.sol-mod__no-br___3Ev-2').text().replace('\n', "").replace('\r', "")
                # 商品价格
                good_price = item.find(
                    '.price-mod__price___cYafX').text().replace('\n', "").replace('\r', "")
                # 只列出商品购买时间、订单号、商家名称、商品名称
                # 其余的请自己实践获取
                data_list.append(good_time_and_id)
                data_list.append(good_merchant)
                data_list.append(good_name)
                data_list.append(good_price)
                print(good_time_and_id, good_merchant, good_name)

    def get_product(self):
        url = 'https://s.taobao.com/search?q=牛奶'
        self.browser.get(url)
        # time.sleep(1)
        self.wait.until(EC.presence_of_element_located(
            (By.ID, 'mainsrp-itemlist')))
        html_str = self.browser.page_source
        obj_list = etree.HTML(html_str).xpath(
            '//div[@id="mainsrp-itemlist"]//div[@class="items"][1]/div')
        data_list = []
        for obj in obj_list:
            item = {}
            item['price'] = obj.xpath(
                './/div[@class="price g_price g_price-highlight"]/strong/text()')[0]
            item['title'] = obj.xpath(
                './/div[@class="row row-2 title"]/a')[0].xpath('string(.)').replace('\n', '').strip()
            item['shop'] = obj.xpath(
                './/div[@class="shop"]/a/span[last()]/text()')[0]
            print(item)
            data_list.append(item)
        self.saveProductToExcel(data_list)

    def saveProductToExcel(self, products):
        baseDir = "C:\\Users\\Administrator\\Desktop\\excel"
        excelName = 'taobaoProduct.xlsx'
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)
        # 创建一个Excel文件
        workbook = xlsxwriter.Workbook(os.path.join(baseDir, excelName))
        worksheet = workbook.add_worksheet()  # 创建一个sheet
        header_format = workbook.add_format({
            'bold': True, 'font_size': 15
        })
        header_format.set_align('center')  # 水平对齐
        header_format.set_align('vcenter')  # 垂直对齐
        header_format.set_text_wrap()  # 内容换行
        # 列宽
        worksheet.set_column('A:J', 20)
        # 自动过滤
        worksheet.autofilter('A1:C'+str(len(products)+1))
        # https://www.jianshu.com/p/c13b24d04730
        # 向 excel 中写入数据
        data1 = ['商品', '价格', '店铺']
        worksheet.write_row('A1', data1, header_format)
        for index, item in enumerate(products):
            data = []
            data.append(item.get("title", ''))
            data.append(item.get("price", ''))
            data.append(item.get("shop", ''))
            worksheet.write_row('A'+str(2+index), data)
        workbook.close()
# 使用教程：
# 1.下载chrome浏览器:https://www.google.com/chrome/
# 2.查看chrome浏览器的版本号，下载对应版本号的chromedriver驱动:http://chromedriver.storage.googleapis.com/index.html
# 3.将chromedriver放到python目录
# 4.执行命令pip install selenium


if __name__ == "__main__":

    taobao_username = "淘宝账号"  # 改成你的淘宝账号
    taobao_password = "淘宝密码"  # 改成你的淘宝密码

    a = taobao_infos()
    # a.login()  # 登录
    # a.crawl_good_buy_data()
    # a.get_addr()
    a.get_product()
