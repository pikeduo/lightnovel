'''
主函数
'''

from Selenium import Selenium
from Book import make_Book

if __name__ == '__main__':
    url = 'https://www.lightnovel.app/book/info/12279'
    selenium = Selenium()
    msg_html = selenium.get_msg_html(url)
    book = make_Book()
    message = book.get_book_msg(msg_html)
    # print(message)
    if message:
        for chapter in message['catlog']:
            url = chapter['href']
            title = chapter['title']
            i = url.split('/')[-1]
            content_html = selenium.get_contet_html(url)
            book.get_book_content(content_html, title, i)
    book.merge_file()
    print('EPUB制作完成！')