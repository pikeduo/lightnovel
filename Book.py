'''
获取书籍信息，制作epub
'''
import os, shutil, requests
import time
import uuid

import pathlib
import zipfile

from lxml import etree
from bs4 import BeautifulSoup
import re
import constant


class make_Book():
    def __init__(self):
        self.message = {}
        self.uuid = uuid.uuid4()    # 生成uuid
        self.text = []  # 存储章节名
        self.image = [] # 存储图片
        self.font = [] # 存储字体文件
        self.ncx = []   # 存储ncx
        self.guide = [] # 存储guide
        self.navPoint = []  # 存储navPoint
        self.path = ''  # 存储文件路径

    # 获取书籍信息
    def get_book_msg(self, html):
        try:
            # xpath加载html
            message_html = etree.HTML(html)
            # 书名，需要处理，去除书名号，获取书名后，创建文件夹
            title = message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[2]/div/div[2]/text()')[
                0].replace('《', '').replace('》', '')
            self.path = os.path.join('E:\EPUB', title)
            self.init_file()
            # 封面，获取封面后下载封面
            cover = \
            message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[1]/div/div/div[2]/img/@src')[
                0]
            res = self.download(cover)
            with open('Images/cover.jpg', 'wb') as f:
                f.write(res.content)
            # 作者,需要处理，去除‘作者：’
            creator = message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[2]/div/div[3]/text()')[
                0].replace('作者：', '')
            # 更新时间，需要处理，提取年月日
            date = message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[2]/div/div[5]/text()')[0]
            date = re.search(r'[1-9]\d{3}-\d{2}-\d[1-9]', date, re.S).group()
            # 简介，需要换行处理
            description = message_html.xpath('//div[@class="introduction"]')[1].xpath('//p/text()')
            description = "\n".join([p for p in description])
            # 目录，获取每个章节的名称和链接地址
            catlog = []
            host = 'https://www.lightnovel.app'
            for a in message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[2]/a'):
                href = host + a.xpath('@href')[0]
                name = a.xpath('string(.)')
                catlog.append({'href': href, 'title': name})
            self.message = {
                'cover': cover,  # 封面
                'title': title,  # 书名
                'creator': creator,  # 作者
                'date': date,  # 更新时间
                'description': description,  # 简介
                'catlog': catlog  # 目录
            }
            # 获取到书籍信息后，打印输出
            book_msg = f'''\t书名：《{title}》
作者：\t{creator}
更新时间：\t{date}
简介：\t{description}
'''
            print(book_msg)
            return self.message
        except Exception as e:
            print(e)

    # 获取章节内容
    def get_book_content(self, html, title, i):
        try:
            # 使用beautifulsoup加载html
            bs = BeautifulSoup(html, 'html.parser')
            # 字体文件，获取style下的font-face，提取字体文件
            style = bs.find('style', attrs={'id': 'read_style'})  # 字体style
            style = self.handle_style(style)
            if not style:
                style = ''
            #章节内容
            content = bs.find('div', attrs={'class': 'html-reader read'})  # 主体内容
            main = self.handle_content(content)
            #将处理后的章节写入html文件
            with open('Text/exam.html', 'r', encoding='utf-8') as f1, open(f'Text/chapter{i}.html', 'w',
                                                                           encoding='utf-8') as f2:
                chapter = f1.read().format(title=title, style=style, main=main)
                bs = BeautifulSoup(chapter, 'html.parser').prettify()
                f2.write(chapter)
                print(f'《{title}》写入完成!')
                self.text.append(constant.TEXT.format(text=f'chapter{i}.html'))
                self.ncx.append(constant.NCX.format(href=f'chapter{i}.html'))
                self.guide.append(constant.GUIDE.format(href=f'chapter{i}.html', title=title))
                self.navPoint.append(constant.NAVPOINT.format(i=i, href=f'chapter{i}.html', title=title))
        except Exception as e:
            print(e)

    # 如果目录不存在则创建目录，否则删除原目录
    def new_file(self, path=''):
        if os.path.exists(path):
            shutil.rmtree(path)
        else:
            os.makedirs(path)


    # 初始化文件夹
    def init_file(self):
        # 新建文件夹
        self.new_file(self.path)
        # 将模板复制到文件夹下
        shutil.copytree('EXAM', self.path)
        # 拼接获取文件夹的路径
        os.chdir(os.path.join(self.path, 'OEBPS'))

    # 下载相关的文件
    def download(self, url):
        res = requests.get(url)
        return res

    # 处理字体文件
    def handle_style(self, style):
        # 纯图片这种可能没有字体文件，所以需要进行判断
        if style:
            # 匹配链接
            a = re.search('(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', style.text)
            if a:
                # 下载字体文件
                res = self.download(a[0])
                # 获取字体文件的名字，保存
                name = a[0].split('/')[-1]
                with open(f'Fonts/{name}', 'wb') as f:
                    f.write(res.content)
                # 替换字体文件的路径
                style = str(style).replace(a[0], f'../Fonts/{name}')
                self.font.append(constant.FONT.format(font=name))
                return style

    # 处理图片
    def handle_content(self, content):
        # 找到全部的图片标签
        div_img = content.find_all('img')
        main = str(content)
        for div in div_img:
            # 获取图片链接
            img = div.attrs['src']
            # 过滤注释的图片
            if img != './img/note.png':
                # 下载图片
                res = self.download(img)
                # 获取图片名称，保存
                name = img.split('/')[-1]
                with open(f'Images/{name}', 'wb') as f:
                    f.write(res.content)
                # 替换图片路径
                main = main.replace(img, f'../Images/{name}')
                self.image.append(constant.IMAGE.format(image=name))
        # 替换注释图片的路径
        main = main.replace('./img/note.png', '../Images/note.png')
        return main

    # 合并文件
    def merge_file(self):
        content_opf = {
            'uuid': self.uuid,
            'title': self.message['title'],
            'creator': self.message['creator'],
            'date': self.message['date'],
            'description': self.message['description'],
            'text': self.prettify_xml(self.text),
            'image': self.prettify_xml(self.image),
            'font': self.prettify_xml(self.font),
            'ncx': self.prettify_xml(self.ncx),
            'guide': self.prettify_xml(self.guide)
        }
        content = ''
        # 打开opf文件，修改内容后重写
        with open('content.opf', 'r', encoding='utf-8') as f:
            content = f.read().format(content_opf)
        with open('content.opf', 'w', encoding='utf-8') as f:
            f.write(content)

        toc = ''
        # 打开ncx文件，修改内容后重写
        with open('toc.ncx', 'r', encoding='utf-8') as f:
            toc = f.read().format(uuid=self.uuid, title=self.message['title'], author=self.message['creator'], navPoint=self.prettify_xml(self.navPoint))
        with open('toc.ncx', 'w', encoding='utf-8') as f:
            f.write(toc)
        # 删除模板
        os.remove('Text/exam.html')
        # 切换文件路径
        os.chdir(self.path)
        print("正在压缩文件!")
        # 压缩文件
        directory = pathlib.Path(self.path)
        with zipfile.ZipFile(f"{self.message['title']}(手机请用Lithium打开).epub", mode='w') as archive:
            for file_path in directory.rglob("*"):
                archive.write(file_path, arcname=file_path.relative_to(directory))
        print("压缩文件完成")
        # 删除不需要的文件
        shutil.rmtree('META-INF')
        shutil.rmtree('OEBPS')
        os.remove('mimetype')
        time.sleep(1)
        # 打开文件夹窗口
        os.startfile(self.path)


    # 美化代码
    def prettify_xml(self, content):
        return '\n        '.join(content)

