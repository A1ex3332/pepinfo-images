"""pepinfo compose: 1080x1920, Dark Lab type, two-beat hook, rehook, then an end card over the held last frame.
usage: python3 compose_pepinfo.py frames_dir sound.wav out.mp4 card.json
card.json: {"hook":[a,b],"hook_b_at":0.4,"rehook":"...","rehook_at":[2.4,5.4],"card_at":5.5,"total":15,
            "card_title":"...","items":[[head,sub],...],"source":"...","cta":"...","ruo":"..."}"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
fd, snd, out, cj = sys.argv[1:5]
K = json.load(open(cj)); FPS = 30; W, H = 1080, 1920
I = "/usr/share/fonts/opentype/inter/"
fb = lambda s: ImageFont.truetype(I + "Inter-Black.otf", s)
fs = lambda s: ImageFont.truetype(I + "Inter-SemiBold.otf", s)
CY, RED, WH, MU = (51, 225, 255), (255, 107, 107), (242, 245, 247), (154, 167, 178)
frames = sorted(x for x in os.listdir(fd) if x.startswith("f") and x.endswith(".png"))
N = int(K["total"] * FPS)
p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", snd, "-af", K.get("af", "loudnorm=I=-14:TP=-1.5:LRA=11"), "-c:v", "libx264", "-preset", "slow", "-crf", "11", "-maxrate", "24M", "-bufsize", "40M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", str(K["total"]), "-movflags", "+faststart", out],
                     stdin=subprocess.PIPE)
def txt(im, xy, s, font, fill, a=255, anchor="mm", sh=True):
    if a <= 0: return
    if sh:
        L = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(L).text((xy[0], xy[1] + 5), s, font=font, fill=(0, 0, 0, int(190 * a / 255)), anchor=anchor)
        im.alpha_composite(L.filter(ImageFilter.GaussianBlur(9)))
    ImageDraw.Draw(im).text(xy, s, font=font, fill=(*fill, a), anchor=anchor)
def fade(t, t0, d=0.18): return int(255 * max(0, min(1, (t - t0) / d)))
cache = {}
def frame(i):
    name = frames[min(i, len(frames) - 1)]
    if name not in cache:
        cache.clear(); cache[name] = Image.open(os.path.join(fd, name)).convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    return cache[name].copy()
GR = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(GR)
for yy in range(380): gd.line((0, yy, W, yy), fill=(10, 12, 15, int(215 * (1 - yy / 380) ** 1.3)))
for i in range(N):
    t = i / FPS; im = frame(i)
    if t < K["rehook_at"][1]: im.alpha_composite(GR)
    if t < K["rehook_at"][0]:
        txt(im, (W // 2, 190), K["hook"][0], fb(74), WH)
        txt(im, (W // 2, 285), K["hook"][1], fb(74), CY, a=fade(t, K["hook_b_at"], 0.08))
    elif t < K["rehook_at"][1]:
        a = min(fade(t, K["rehook_at"][0]), 255 - fade(t, K["rehook_at"][1] - 0.2))
        txt(im, (W // 2, 230), K["rehook"], fb(72), WH, a=a)
    if t >= K["card_at"]:
        tc = t - K["card_at"]
        dim = Image.new("RGBA", im.size, (10, 12, 15, int(min(1, tc / 0.35) * 205))); im.alpha_composite(dim)
        txt(im, (W // 2, 300), K["card_title"], fb(66), WH, a=fade(tc, 0.1))
        y = 480
        for j, (head, sub) in enumerate(K["items"]):
            a = fade(tc, 0.5 + j * 1.1, 0.25)
            d = ImageDraw.Draw(im)
            if a: d.rounded_rectangle((90, y - 70, W - 90, y + 150), radius=28, fill=(18, 22, 27, int(a * 0.95)), outline=(*CY, a), width=3)
            txt(im, (140, y - 5), f"{j+1}  {head}", fb(68), CY, a=a, anchor="lm", sh=False)
            txt(im, (140, y + 80), sub, fs(42), WH, a=a, anchor="lm", sh=False)
            y += 260
        a = fade(tc, 0.5 + len(K["items"]) * 1.1 + 0.3)
        txt(im, (W // 2, y - 10), K["cta"][0], fb(52), WH, a=a)
        txt(im, (W // 2, y + 60), K["cta"][1], fb(52), RED, a=a)
        txt(im, (W // 2, 1420), K["source"], fs(32), MU, a=a, sh=False)
        txt(im, (W // 2, 1465), K["ruo"], fs(32), MU, a=a, sh=False)
    p.stdin.write(im.convert("RGB").tobytes())
p.stdin.close(); p.wait(); print("wrote", out)
