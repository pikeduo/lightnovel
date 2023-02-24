import textwrap
from io import BytesIO
from aip import AipOcr
from PIL import Image, ImageDraw, ImageFont

def luan_word_to_img(text, _ttf_path, img_path):
    # 设置文字个数
    para = textwrap.wrap(str, width=40)
    # 设置图片大小
    img_size = 1024
    img = Image.new('1', (img_size, img_size), 255)
    draw = ImageDraw.Draw(img)
    # word_size = int(img_size * (1 / len(text)))
    # 导入字体文件
    font = ImageFont.truetype(_ttf_path, 25)
    # 设置高度，当文字超出时在下一行画文字
    current_h, pad = 30, 10
    for line in para:
        x, y = draw.textsize(line, font)
        draw.text(((img_size - x) // 2, current_h), line, font=font, fill=0)
        current_h += y + pad
    bytes_io = BytesIO()
    img.save(bytes_io, format="PNG")
    img.show()
    img.save('a.png')
    # 调用百度api的ocr识别文字
    APP_ID = 'xxx'
    API_KEY = 'xxx'
    SECRET_KEY = 'xxx'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    dic_result=client.basicGeneral(bytes_io.getvalue())
    print(dic_result)

str = '''原滔资袋，蛤耸阅桑─举的─界明，曹听关渣，丐，……'''
luan_word_to_img(str, './fonts/d44f5fae30c76105f3a3976dfa651528.woff2', 'a.png')