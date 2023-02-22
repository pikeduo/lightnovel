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
        self.text = []
        self.image = []
        self.font = []
        self.ncx = []
        self.guide = []
        self.navPoint = []
        self.path = ''

    # 获取书籍信息
    def get_book_msg(self, html):
        try:
            message_html = etree.HTML(html)
            # 书名
            title = message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[2]/div/div[2]/text()')[
                0].replace('《', '').replace('》', '')
            self.path = os.path.join('E:\EPUB', title)
            self.init_file()
            # 封面
            cover = \
            message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[1]/div/div/div[2]/img/@src')[
                0]
            res = self.download(cover)
            with open('Images/cover.jpg', 'wb') as f:
                f.write(res.content)
            # 作者
            creator = message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[2]/div/div[3]/text()')[
                0].replace('作者：', '')
            # 更新时间
            date = message_html.xpath('//*[@id="q-app"]/div/div[3]/main/div[1]/div/div[1]/div[2]/div/div[5]/text()')[0]
            date = re.search(r'[1-9]\d{3}-\d{2}-\d[1-9]', date, re.S).group()
            # 简介
            description = message_html.xpath('//div[@class="introduction"]')[1].xpath('//p/text()')
            description = "\n".join([p for p in description])
            # 目录
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
            book_msg = f'''书名：《{title}》
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
            bs = BeautifulSoup(html, 'html.parser')
            # 字体文件
            style = bs.find('style', attrs={'id': 'read_style'})  # 字体style
            style = self.handle_style(style)
            if not style:
                style = ''
            content = bs.find('div', attrs={'class': 'html-reader read'})  # 主体内容
            main = self.handle_content(content)
            with open('Text/exam.html', 'r', encoding='utf-8') as f1, open(f'Text/chapter{i}.html', 'w',
                                                                           encoding='utf-8') as f2:
                chapter = f1.read().format(title=title, style=style, main=main)
                f2.write(chapter)
                print(f'《{title}》写入完成!')
                self.text.append(constant.TEXT.format(text=f'chapter{i}.html'))
                self.ncx.append(constant.NCX.format(href=f'chapter{i}.html'))
                self.guide.append(constant.GUIDE.format(href=f'chapter{i}.html', title=title))
                self.navPoint.append(constant.NAVPOINT.format(i=i, href=f'chapter{i}.html', title=title))
        except Exception as e:
            print(e)

    # 如果目录不存在则创建目录
    def new_file(self, path=''):
        if not os.path.exists(path):
            os.makedirs(path)

    # 创建一些固定的文件
    def init_file(self):
        self.new_file(self.path)
        shutil.copytree('EXAM', self.path)
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
                res = self.download(a[0])
                name = a[0].split('/')[-1]
                with open(f'Fonts/{name}', 'wb') as f:
                    f.write(res.content)
                style = str(style).replace(a[0], f'../Fonts/{name}')
                self.font.append(constant.FONT.format(font=name))
                return style

    # 处理图片
    def handle_content(self, content):
        div_img = content.find_all('img')
        main = str(content)
        for div in div_img:
            img = div.attrs['src']
            if img != './img/note.png':
                res = self.download(img)
                name = img.split('/')[-1]
                with open(f'Images/{name}', 'wb') as f:
                    f.write(res.content)
                main = main.replace(img, f'../Images/{name}')
                self.image.append(constant.IMAGE.format(image=name))
        main = main.replace('./img/note.png', '../Images/note.png')
        bs = BeautifulSoup(main, 'xml').prettify()
        return bs

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
        with open('content.opf', 'r', encoding='utf-8') as f:
            content = f.read().format(content_opf)
        with open('content.opf', 'w', encoding='utf-8') as f:
            f.write(content)

        toc = ''
        with open('toc.ncx', 'r', encoding='utf-8') as f:
            toc = f.read().format(uuid=self.uuid, title=self.message['title'], author=self.message['creator'], navPoint=self.prettify_xml(self.navPoint))
        with open('toc.ncx', 'w', encoding='utf-8') as f:
            f.write(toc)
        os.remove('Text/exam.html')
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
        os.startfile(self.path)


    # 美化代码
    def prettify_xml(self, content):
        return '\n        '.join(content)

