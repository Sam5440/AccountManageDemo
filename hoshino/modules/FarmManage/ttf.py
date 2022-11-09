import base64
from io import BytesIO

import qrcode
from PIL import Image, ImageDraw, ImageFont


# 将Lolita.ttf放到
# C盘根目录下
def str_image_generate(text):
    """
    将文字换为base64的CQ码
    """
    l = len(text)  # 字符串长度
    text_format = "#   猫猫服务中心   #\n                -[]\n"
    # n = 4000
    # for i in range(0, l, n):
    #     text_format += text[i:i+n]
    #     text_format += "\n"
    text = text.replace("]", "]\n")
    text = text.replace(")", ")\n")
    text = text.replace("）", "）\n")
    text = text.replace("\n\n", "\n")
    text = text.replace("\n\n", "\n")
    text_format += text
    return str2image(text_format)#+qrcode_url(text)

def qrcode_url(source_url):
    qr_img = qrcode.make(source_url)
    # qr_img = qrcode.make(data=source_url, version=10,
    #                      error_correction=qrcode.constants.ERROR_CORRECT_Q,
    #                      box_size=8,
    #                      border=4)
    byte_io = BytesIO()
    qr_img.save(byte_io, 'PNG')
    # byte_io.seek(0)
    # base64_data = str(base64.b64encode(byte_io.getvalue()))
    # base64_data = base64_data.replace("b'", "base64://")
    # base64_data = base64_data.replace("'", "")
    base64_data = 'base64://' + base64.b64encode(byte_io.getvalue()).decode()
    return f"[CQ:image,file={base64_data}]"

def str2image(str_text):
    img = Image.new('RGB', get_font_render_size(str_text), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), str_text, fill="#00000000", font=ImageFont.truetype("C:\Lolita.ttf", size=60))
    draw.text((20, 20), "#   猫猫服务中心   #\n                -[]\n", fill="#98F353",
              font=ImageFont.truetype("C:\Lolita.ttf", size=60))
    # img.show()
    bio = BytesIO()
    img.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    return f"[CQ:image,file={base64_str}]"


def get_font_render_size(text):
    canvas = Image.new('RGB', (2048, 2048 * 10))
    draw = ImageDraw.Draw(canvas)
    monospace = ImageFont.truetype("C:\Lolita.ttf", size=60)
    draw.text((0, 0), text, font=monospace, fill="#ffffffff")
    bbox = canvas.getbbox()
    # 宽高
    size = (bbox[2] - bbox[0] + 40, bbox[3] - bbox[1] + 40)
    return size

