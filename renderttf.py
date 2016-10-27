# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PIL import Image
from PIL import ImageFont, ImageDraw

font = ImageFont.truetype("E:/DevTool/novel/VisNovel/res/NanumBarunGothic.ttf", 25)

txt = u"ABC가나다"

image = Image.new("RGBA", font.getsize(txt), (255,255,255,0))
draw = ImageDraw.Draw(image)

draw.text((0, 0), txt, (255,255,255), font=font)
image.show()
image.save("a.png")
