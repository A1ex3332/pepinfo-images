# Text decals for the pepinfo "untested seller" smash: UNTESTED stamp (block) and COA (ball).
from PIL import Image, ImageDraw, ImageFont
B = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
import os
if not os.path.exists(B): B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
def stamp(path, text, col, size=(1024,1024), fs=170, box=True, rot=-8):
    im = Image.new("RGBA", size, (0,0,0,0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(B, fs); w = d.textlength(text, font=f)
    cx, cy = size[0]//2, size[1]//2
    d.text((cx, cy), text, font=f, fill=col, anchor="mm")
    if box:
        pad = 40; h = fs*0.75
        d.rounded_rectangle((cx-w/2-pad, cy-h/2-pad, cx+w/2+pad, cy+h/2+pad), radius=24, outline=col, width=22)
    im = im.rotate(rot, resample=Image.BICUBIC)
    im.save(path)
stamp("untested.png", "UNTESTED", (255,107,107,255), fs=150)
stamp("coa.png", "COA", (51,225,255,255), size=(1024,1024), fs=330, box=False, rot=0)
print("ok")
