"""Upscale rendered frames to 1080x1920, draw hook + live piece counter, mux sound.
usage: python3 compose.py frames_dir sound.wav out.mp4 [--variant b]
Starts at timeline "trim" (opens mid-slice, playbook G3); --variant b swaps the hook text for the
trial-reel opening test (playbook G6; theme "hook_b", else a challenge hook).
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

fd, snd, out = sys.argv[1:4]
VARIANT = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "a"
tl = json.load(open(os.path.join(fd, "timeline.json")))
FPS = tl["fps"]; counts = tl["counts"]
TRIM = tl.get("trim", 0.0); F0 = int(round(TRIM * FPS))
HOOK = tl.get("theme", {}).get("hook", ["Cutting one block", "into 1,000 pieces"])
FINAL = max(counts)
if VARIANT == "b":
    HOOK = tl.get("theme", {}).get("hook_b", ["Try to keep watching", "until 1,000 pieces"])
HOOK = [h.replace("1,000", f"{FINAL:,}") for h in HOOK]
W, H = 1080, 1920
B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
M = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
f_hook = ImageFont.truetype(B, 66)
f_num = ImageFont.truetype(B, 132)
f_lab = ImageFont.truetype(B, 56)

frames = sorted(x for x in os.listdir(fd) if x.startswith("f") and x.endswith(".png") and int(x[1:5]) >= F0)
p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                      "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-ss", f"{TRIM:.3f}", "-i", snd,
                      "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "slow",
                      "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                      "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)

def shadow_text(img, xy, text, font, fill, anchor="mm", blur=8, alpha=170):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 4), text, font=font, fill=(0, 0, 0, alpha), anchor=anchor)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(sh)
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor)

prev = 1; pop_f = -99
for n, name in enumerate(frames):
    f = int(name[1:5]); t = f / FPS; tv = t - TRIM      # tv = time on screen
    im = Image.open(os.path.join(fd, name)).convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    c = counts[min(f, len(counts) - 1)]
    if c != prev:
        pop_f = f; prev = c
    # hook (first 2.6 s), then the counter takes over
    rw0, rw1 = tl.get("rw0", 1e9), tl.get("rw1", 1e9)
    if tv < 2.35 or t > rw0 + 0.35:     # hook on screen at 0.0 s, no fade-in
        a = int(255 * min(1, (2.35 - tv) / 0.3)) if tv < 2.35 else int(255 * min(1, (t - rw0 - 0.35) / 0.3))
        shadow_text(im, (W // 2, 175), HOOK[0], f_hook, (255, 255, 255, a), alpha=int(170 * a / 255))
        shadow_text(im, (W // 2, 250), HOOK[1], f_hook, (255, 225, 120, a), alpha=int(170 * a / 255))
    if True:
        a = 255
        k = max(0, 1 - (f - pop_f) / 5)          # little pop when the count changes
        size = int(132 * (1 + 0.16 * k))
        fn = ImageFont.truetype(B, size)
        col = (255, 225, 120, a) if c >= 1000 else (255, 255, 255, a)
        shadow_text(im, (W // 2, 410), f"{c:,}", fn, col, alpha=int(170 * a / 255))
        shadow_text(im, (W // 2, 503), "piece" if c == 1 else "pieces", f_lab, (255, 255, 255, a), alpha=int(190 * a / 255))
    p.stdin.write(im.convert("RGB").tobytes())
p.stdin.close(); p.wait()
print("wrote", out)
